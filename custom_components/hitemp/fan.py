"""Fan platform for HiTemp integration."""

from __future__ import annotations

import math
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .const import DOMAIN
from .coordinator import HiTempCoordinator

PARAM_FAN = "M17"
ORDERED_NAMED_FAN_SPEEDS = ["1", "2", "3", "4", "5"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HiTemp fan entities."""
    coordinator: HiTempCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        HiTempFan(coordinator, device["deviceCode"])
        for device in coordinator.devices
        if device.get("deviceCode")
    ]

    async_add_entities(entities)


class HiTempFan(CoordinatorEntity[HiTempCoordinator], FanEntity):
    """Fan entity for HiTemp fan control."""

    _attr_has_entity_name = True
    _attr_name = "Fan"
    _attr_supported_features = FanEntityFeature.SET_SPEED
    _attr_speed_count = 5

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
    ) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_fan"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device = self.coordinator.get_device_info(self._device_code)
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_code)},
            name=device.get("deviceNickName", "HiTemp Water Heater") if device else "HiTemp Water Heater",
            manufacturer="HiTemp",
            model="PV300",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.last_update_success:
            return False
        device = self.coordinator.get_device_info(self._device_code)
        if device:
            return device.get("deviceStatus") == "ONLINE"
        return False

    @property
    def is_on(self) -> bool | None:
        """Return true if fan is on."""
        value = self.coordinator.get_device_param(self._device_code, PARAM_FAN)
        if value is None:
            return None
        try:
            return int(value) > 0
        except (ValueError, TypeError):
            return None

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        value = self.coordinator.get_device_param(self._device_code, PARAM_FAN)
        if value is None:
            return None
        try:
            speed = int(value)
        except (ValueError, TypeError):
            return None
        if speed == 0:
            return 0
        return ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, str(speed))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes including the parameter code."""
        return {"code": PARAM_FAN}

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage."""
        if percentage == 0:
            await self.coordinator.async_write_param(self._device_code, PARAM_FAN, 0)
        else:
            speed = int(percentage_to_ordered_list_item(ORDERED_NAMED_FAN_SPEEDS, percentage))
            await self.coordinator.async_write_param(self._device_code, PARAM_FAN, speed)

    async def async_turn_on(self, percentage: int | None = None, **kwargs: Any) -> None:
        """Turn on the fan."""
        if percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            await self.coordinator.async_write_param(self._device_code, PARAM_FAN, 5)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.coordinator.async_write_param(self._device_code, PARAM_FAN, 0)
