"""DataUpdateCoordinator for HiTemp integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HiTempApiClient, HiTempAuthError, HiTempConnectionError
from .const import ALL_PARAMS, DOMAIN, MAX_TEMP, MIN_TEMP, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class HiTempCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Coordinator to manage fetching HiTemp data."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self._session: aiohttp.ClientSession | None = None
        self._client: HiTempApiClient | None = None
        self.devices: list[dict[str, Any]] = []

        # Bottom thermostat active control state
        self._bottom_control_enabled: dict[str, bool] = {}
        self._bottom_target: dict[str, float] = {}
        self._last_t03: dict[str, float | None] = {}
        self._last_r01: dict[str, float | None] = {}

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        self._session = aiohttp.ClientSession()
        self._client = HiTempApiClient(
            self._session,
            self.config_entry.data[CONF_EMAIL],
            self.config_entry.data[CONF_PASSWORD],
        )

        try:
            await self._client.login()
            self.devices = await self._client.get_devices()
            _LOGGER.debug("Found %d devices during setup", len(self.devices))
        except HiTempAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except HiTempConnectionError as err:
            raise UpdateFailed(f"Error connecting to HiTemp API: {err}") from err

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data from API."""
        if not self._client:
            raise UpdateFailed("Client not initialized")

        try:
            # Refresh device list periodically
            self.devices = await self._client.get_devices()

            # Fetch parameters for each device
            data: dict[str, dict[str, Any]] = {}

            for device in self.devices:
                device_code = device.get("deviceCode")
                if not device_code:
                    continue

                # Store device metadata
                data[device_code] = {
                    "_device": device,
                    "_params": {},
                }

                # Fetch all parameters
                params = await self._client.read_params(device_code, ALL_PARAMS)
                data[device_code]["_params"] = params

            # Store data first so _update_bottom_control can access it
            self.data = data

            # Run active bottom control loop for each device
            for device_code in data:
                await self._update_bottom_control(device_code)

            return data

        except HiTempAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except HiTempConnectionError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_write_param(
        self, device_code: str, code: str, value: int | float | str
    ) -> bool:
        """Write a parameter and refresh data."""
        if not self._client:
            return False

        try:
            success = await self._client.write_param(device_code, code, value)
            if success:
                # Refresh data after write
                await self.async_request_refresh()
            return success
        except (HiTempAuthError, HiTempConnectionError) as err:
            _LOGGER.error("Error writing parameter: %s", err)
            return False

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._session:
            await self._session.close()
            self._session = None

    def get_device_param(
        self, device_code: str, param_code: str
    ) -> Any | None:
        """Get a parameter value for a device."""
        if not self.data:
            return None

        device_data = self.data.get(device_code, {})
        params = device_data.get("_params", {})
        param = params.get(param_code, {})
        return param.get("value")

    def get_device_info(self, device_code: str) -> dict[str, Any] | None:
        """Get device metadata."""
        if not self.data:
            return None

        device_data = self.data.get(device_code, {})
        return device_data.get("_device")

    # =========================================================================
    # Bottom Thermostat Active Control
    # =========================================================================

    def calculate_r01_from_bottom_target(
        self, device_code: str, bottom_target: float
    ) -> float | None:
        """
        Calculate R01 from desired bottom temperature.

        Formula: R01 = (bottom_target + T03) / 2
        Returns None if T03 unavailable, clamped to MIN_TEMP-MAX_TEMP.
        """
        t03 = self.get_device_param(device_code, "T03")
        if t03 is None:
            return None

        try:
            t03_float = float(t03)
            calculated_r01 = (bottom_target + t03_float) / 2
            return max(MIN_TEMP, min(MAX_TEMP, calculated_r01))
        except (ValueError, TypeError):
            return None

    def calculate_bottom_target_from_r01(
        self, device_code: str, r01: float | None = None
    ) -> float | None:
        """
        Reverse calculate implied bottom target from R01.

        Formula: bottom_target = 2 * R01 - T03
        Uses current R01 if not specified.
        """
        if r01 is None:
            r01 = self.get_device_param(device_code, "R01")
        if r01 is None:
            return None

        t03 = self.get_device_param(device_code, "T03")
        if t03 is None:
            return None

        try:
            return 2 * float(r01) - float(t03)
        except (ValueError, TypeError):
            return None

    def enable_bottom_control(self, device_code: str, bottom_target: float) -> None:
        """Enable active bottom control with given target."""
        self._bottom_control_enabled[device_code] = True
        self._bottom_target[device_code] = bottom_target
        # Store current T03 to detect changes
        t03 = self.get_device_param(device_code, "T03")
        self._last_t03[device_code] = float(t03) if t03 is not None else None
        _LOGGER.debug(
            "Bottom control enabled for %s: target=%.1f°C",
            device_code, bottom_target
        )

    def disable_bottom_control(self, device_code: str) -> None:
        """Disable active bottom control."""
        self._bottom_control_enabled[device_code] = False
        _LOGGER.debug("Bottom control disabled for %s", device_code)

    def is_bottom_control_enabled(self, device_code: str) -> bool:
        """Check if bottom control is active."""
        return self._bottom_control_enabled.get(device_code, False)

    def get_bottom_target(self, device_code: str) -> float | None:
        """Get the stored bottom target for a device."""
        if not self.is_bottom_control_enabled(device_code):
            return None
        return self._bottom_target.get(device_code)

    async def _update_bottom_control(self, device_code: str) -> None:
        """Update R01 if T03 or external R01 changed (active control loop)."""
        if not self.is_bottom_control_enabled(device_code):
            return

        current_t03 = self.get_device_param(device_code, "T03")
        current_r01 = self.get_device_param(device_code, "R01")

        if current_t03 is None or current_r01 is None:
            return

        try:
            current_t03_float = float(current_t03)
            current_r01_float = float(current_r01)
        except (ValueError, TypeError):
            return

        last_t03 = self._last_t03.get(device_code)
        last_r01 = self._last_r01.get(device_code)

        # Check if R01 was changed externally (physical display or main thermostat)
        if last_r01 is not None and abs(current_r01_float - last_r01) > 0.1:
            # R01 changed externally, recalculate stored bottom target
            new_bottom_target = 2 * current_r01_float - current_t03_float
            self._bottom_target[device_code] = new_bottom_target
            _LOGGER.debug(
                "R01 changed externally for %s: R01=%.1f, new bottom_target=%.1f",
                device_code, current_r01_float, new_bottom_target
            )

        # Check if T03 changed - need to adjust R01
        if last_t03 is not None and abs(current_t03_float - last_t03) > 0.1:
            bottom_target = self._bottom_target.get(device_code)
            if bottom_target is not None:
                new_r01 = self.calculate_r01_from_bottom_target(device_code, bottom_target)
                if new_r01 is not None and abs(new_r01 - current_r01_float) > 0.1:
                    _LOGGER.debug(
                        "T03 changed for %s: %.1f→%.1f, adjusting R01: %.1f→%.1f",
                        device_code, last_t03, current_t03_float,
                        current_r01_float, new_r01
                    )
                    await self.async_write_param(device_code, "R01", new_r01)
                    # Update last_r01 to the value we just wrote
                    self._last_r01[device_code] = new_r01
                    # Return early - the write will trigger another update
                    return

        # Update tracking values
        self._last_t03[device_code] = current_t03_float
        self._last_r01[device_code] = current_r01_float
