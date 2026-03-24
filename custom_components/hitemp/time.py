"""Time platform for HiTemp integration."""

from __future__ import annotations

from datetime import time
import logging
from typing import Any

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HiTempCoordinator

_LOGGER = logging.getLogger(__name__)

# (key, name, hour_code, minute_code or None)
# (key, name, hour_code, minute_code, enabled_default)
TIME_PARAMS = [
    ("timer_1_start", "Timer 1 start", "L06", "L07", False),
    ("timer_1_end", "Timer 1 end", "L08", "L09", False),
    ("timer_2_start", "Timer 2 start", "L10", "L11", False),
    ("timer_2_end", "Timer 2 end", "L12", "L13", False),
    ("disinfection_start", "Disinfection start time", "G03", None, True),
    ("night_decrease_start", "Night decrease start", "N05", None, True),
    ("night_decrease_end", "Night decrease end", "N06", None, True),
]

# Codes handled here, to exclude from number entities
TIME_PARAM_CODES = {"L06", "L07", "L08", "L09", "L10", "L11", "L12", "L13", "G03", "N05", "N06"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HiTemp time entities."""
    coordinator: HiTempCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[HiTempTime] = []
    for device in coordinator.devices:
        device_code = device.get("deviceCode")
        if not device_code:
            continue
        for key, name, hour_code, minute_code, enabled_default in TIME_PARAMS:
            entities.append(
                HiTempTime(coordinator, device_code, key, name, hour_code, minute_code, enabled_default)
            )

    async_add_entities(entities)


class HiTempTime(CoordinatorEntity[HiTempCoordinator], TimeEntity):
    """Time entity combining hour and minute params."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
        key: str,
        name: str,
        hour_code: str,
        minute_code: str | None,
        enabled_default: bool = True,
    ) -> None:
        super().__init__(coordinator)
        self._device_code = device_code
        self._hour_code = hour_code
        self._minute_code = minute_code
        self._attr_name = name
        self._attr_unique_id = f"{device_code}_{key}"
        self._attr_entity_registry_enabled_default = enabled_default

    @property
    def device_info(self) -> DeviceInfo:
        device = self.coordinator.get_device_info(self._device_code)
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_code)},
            name=device.get("deviceNickName", "HiTemp Water Heater") if device else "HiTemp Water Heater",
            manufacturer="HiTemp",
            model="PV300",
        )

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        device = self.coordinator.get_device_info(self._device_code)
        return device.get("deviceStatus") == "ONLINE" if device else False

    @property
    def native_value(self) -> time | None:
        hour = self.coordinator.get_device_param(self._device_code, self._hour_code)
        if hour is None:
            return None
        try:
            h = int(float(hour))
            m = 0
            if self._minute_code:
                minute = self.coordinator.get_device_param(self._device_code, self._minute_code)
                if minute is not None:
                    m = int(float(minute))
            return time(h, m)
        except (ValueError, TypeError):
            return None

    async def async_set_value(self, value: time) -> None:
        if self._minute_code:
            await self.coordinator.async_write_param(self._device_code, self._hour_code, value.hour)
            await self.coordinator.async_write_param(self._device_code, self._minute_code, value.minute)
        else:
            # Hour-only: round to nearest hour
            hour = value.hour + (1 if value.minute >= 30 else 0)
            await self.coordinator.async_write_param(self._device_code, self._hour_code, hour % 24)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        codes = {"hour_code": self._hour_code}
        if self._minute_code:
            codes["minute_code"] = self._minute_code
        return codes
