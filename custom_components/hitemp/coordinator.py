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
from .const import ALL_PARAMS, DOMAIN, UPDATE_INTERVAL

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
