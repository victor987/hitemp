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

# External sensor entity ID for COP calculation
ENERGY_SENSOR_ENTITY_ID = "sensor.water_heater_energy"
# Tank parameters for energy calculation
TANK_VOLUME_LITERS = 300
SPECIFIC_HEAT_KWH = 0.001163  # kWh/(kg·K)

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

        # Minimum thermostat active control state
        self._minimum_control_enabled: dict[str, bool] = {}
        self._minimum_target: dict[str, float] = {}
        self._last_max_temp: dict[str, float | None] = {}
        self._last_r01: dict[str, float | None] = {}

        # COP tracking - only updates when energy meter changes
        self._cop_last_energy_meter: dict[str, float | None] = {}
        self._cop_energy_stored_at_meter_change: dict[str, float | None] = {}
        self._cop_current: dict[str, float | None] = {}

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

            # Run active minimum control loop for each device
            for device_code in data:
                await self._update_minimum_control(device_code)
                self._update_cop(device_code)

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
    # Minimum Thermostat Active Control
    # =========================================================================

    def _get_max_temp(self, device_code: str) -> float | None:
        """Get max(T02, T03) for the device."""
        t02 = self.get_device_param(device_code, "T02")
        t03 = self.get_device_param(device_code, "T03")
        if t02 is None or t03 is None:
            return None
        try:
            return max(float(t02), float(t03))
        except (ValueError, TypeError):
            return None

    def _get_min_temp(self, device_code: str) -> float | None:
        """Get min(T02, T03) for the device."""
        t02 = self.get_device_param(device_code, "T02")
        t03 = self.get_device_param(device_code, "T03")
        if t02 is None or t03 is None:
            return None
        try:
            return min(float(t02), float(t03))
        except (ValueError, TypeError):
            return None

    def calculate_r01_from_minimum_target(
        self, device_code: str, min_target: float
    ) -> float | None:
        """
        Calculate R01 from desired minimum temperature.

        Formula: R01 = (min_target + max(T02, T03)) / 2
        Returns None if temps unavailable, clamped to MIN_TEMP-MAX_TEMP.
        """
        max_temp = self._get_max_temp(device_code)
        if max_temp is None:
            return None

        try:
            calculated_r01 = (min_target + max_temp) / 2
            return max(MIN_TEMP, min(MAX_TEMP, calculated_r01))
        except (ValueError, TypeError):
            return None

    def calculate_minimum_target_from_r01(
        self, device_code: str, r01: float | None = None
    ) -> float | None:
        """
        Reverse calculate implied minimum target from R01.

        Formula: min_target = 2 * R01 - max(T02, T03)
        Uses current R01 if not specified.
        """
        if r01 is None:
            r01 = self.get_device_param(device_code, "R01")
        if r01 is None:
            return None

        max_temp = self._get_max_temp(device_code)
        if max_temp is None:
            return None

        try:
            return 2 * float(r01) - max_temp
        except (ValueError, TypeError):
            return None

    def enable_minimum_control(self, device_code: str, min_target: float) -> None:
        """Enable active minimum control with given target."""
        self._minimum_control_enabled[device_code] = True
        self._minimum_target[device_code] = min_target
        # Store current max temp to detect changes
        max_temp = self._get_max_temp(device_code)
        self._last_max_temp[device_code] = max_temp
        _LOGGER.debug(
            "Minimum control enabled for %s: target=%.1f°C",
            device_code, min_target
        )

    def disable_minimum_control(self, device_code: str) -> None:
        """Disable active minimum control."""
        self._minimum_control_enabled[device_code] = False
        _LOGGER.debug("Minimum control disabled for %s", device_code)

    def is_minimum_control_enabled(self, device_code: str) -> bool:
        """Check if minimum control is active."""
        return self._minimum_control_enabled.get(device_code, False)

    def get_minimum_target(self, device_code: str) -> float | None:
        """Get the stored minimum target for a device."""
        if not self.is_minimum_control_enabled(device_code):
            return None
        return self._minimum_target.get(device_code)

    async def _update_minimum_control(self, device_code: str) -> None:
        """Update R01 if max temp or external R01 changed (active control loop)."""
        if not self.is_minimum_control_enabled(device_code):
            return

        current_max_temp = self._get_max_temp(device_code)
        current_r01 = self.get_device_param(device_code, "R01")

        if current_max_temp is None or current_r01 is None:
            return

        try:
            current_r01_float = float(current_r01)
        except (ValueError, TypeError):
            return

        last_max_temp = self._last_max_temp.get(device_code)
        last_r01 = self._last_r01.get(device_code)

        # Check if R01 was changed externally (physical display or main thermostat)
        if last_r01 is not None and abs(current_r01_float - last_r01) > 0.1:
            # R01 changed externally - disable minimum control (user took manual control)
            _LOGGER.debug(
                "R01 changed externally for %s: %.1f→%.1f, disabling minimum control",
                device_code, last_r01, current_r01_float
            )
            self.disable_minimum_control(device_code)
            # Update tracking values before returning
            self._last_max_temp[device_code] = current_max_temp
            self._last_r01[device_code] = current_r01_float
            return

        # Check if max temp changed - need to adjust R01
        if last_max_temp is not None and abs(current_max_temp - last_max_temp) > 0.1:
            min_target = self._minimum_target.get(device_code)
            if min_target is not None:
                new_r01 = self.calculate_r01_from_minimum_target(device_code, min_target)
                if new_r01 is not None and abs(new_r01 - current_r01_float) > 0.1:
                    _LOGGER.debug(
                        "Max temp changed for %s: %.1f→%.1f, adjusting R01: %.1f→%.1f",
                        device_code, last_max_temp, current_max_temp,
                        current_r01_float, new_r01
                    )
                    await self.async_write_param(device_code, "R01", new_r01)
                    # Update last_r01 to the value we just wrote
                    self._last_r01[device_code] = new_r01
                    # Return early - the write will trigger another update
                    return

        # Update tracking values
        self._last_max_temp[device_code] = current_max_temp
        self._last_r01[device_code] = current_r01_float

    # =========================================================================
    # COP Calculation
    # =========================================================================

    def _get_energy_stored(self, device_code: str) -> float | None:
        """Calculate energy stored in tank: 300kg × 0.001163 × T02 kWh."""
        t02 = self.get_device_param(device_code, "T02")
        if t02 is None:
            return None
        try:
            return TANK_VOLUME_LITERS * SPECIFIC_HEAT_KWH * float(t02)
        except (ValueError, TypeError):
            return None

    def _get_energy_meter(self) -> float | None:
        """Get current energy meter reading from external sensor."""
        state = self.hass.states.get(ENERGY_SENSOR_ENTITY_ID)
        if state is None or state.state in ("unknown", "unavailable"):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None

    def is_compressor_running(self, device_code: str) -> bool:
        """Check if compressor is running based on O29 (compressor speed Hz)."""
        o29 = self.get_device_param(device_code, "O29")
        if o29 is None:
            return False
        try:
            return float(o29) > 0
        except (ValueError, TypeError):
            return False

    def _update_cop(self, device_code: str) -> None:
        """Update COP - only when energy meter changes."""
        current_energy_meter = self._get_energy_meter()
        if current_energy_meter is None:
            return

        last_energy_meter = self._cop_last_energy_meter.get(device_code)

        # First run - just store values
        if last_energy_meter is None:
            self._cop_last_energy_meter[device_code] = current_energy_meter
            self._cop_energy_stored_at_meter_change[device_code] = self._get_energy_stored(device_code)
            return

        # No change in meter - do nothing
        if current_energy_meter == last_energy_meter:
            return

        # Meter changed - calculate COP
        current_energy_stored = self._get_energy_stored(device_code)
        energy_stored_at_start = self._cop_energy_stored_at_meter_change.get(device_code)

        if current_energy_stored is not None and energy_stored_at_start is not None:
            delta_stored = current_energy_stored - energy_stored_at_start
            delta_meter = current_energy_meter - last_energy_meter

            if delta_meter > 0:
                self._cop_current[device_code] = round(delta_stored / delta_meter, 2)

        # Update tracking for next meter change
        self._cop_last_energy_meter[device_code] = current_energy_meter
        self._cop_energy_stored_at_meter_change[device_code] = current_energy_stored

    def get_cop(self, device_code: str) -> float | None:
        """Get COP value."""
        return self._cop_current.get(device_code)
