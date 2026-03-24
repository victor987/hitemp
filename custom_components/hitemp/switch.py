"""Switch platform for HiTemp integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HiTempCoordinator

_LOGGER = logging.getLogger(__name__)

# Parameter code for power
PARAM_POWER = "Power"
# Parameter code for booster (electric heater)
PARAM_BOOSTER = "M06"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HiTemp switch entities."""
    coordinator: HiTempCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device in coordinator.devices:
        device_code = device.get("deviceCode")
        if not device_code:
            continue
        entities.append(HiTempPowerSwitch(coordinator, device_code))
        entities.append(HiTempBoosterSwitch(coordinator, device_code))

    async_add_entities(entities)


class HiTempPowerSwitch(CoordinatorEntity[HiTempCoordinator], SwitchEntity):
    """Switch entity for HiTemp power control."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_power_switch"

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
        """Return true if the switch is on."""
        value = self.coordinator.get_device_param(self._device_code, PARAM_POWER)
        if value is None:
            return None
        try:
            return int(value) == 1
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes including the parameter code."""
        return {"code": PARAM_POWER}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await self.coordinator.async_write_param(self._device_code, PARAM_POWER, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await self.coordinator.async_write_param(self._device_code, PARAM_POWER, 0)


class HiTempBoosterSwitch(CoordinatorEntity[HiTempCoordinator], SwitchEntity):
    """Switch entity for HiTemp booster (electric heater) control."""

    _attr_has_entity_name = True
    _attr_name = "Booster"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_booster_switch"

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
        """Return true if the booster is on."""
        value = self.coordinator.get_device_param(self._device_code, PARAM_BOOSTER)
        if value is None:
            return None
        try:
            return int(value) == 1
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes including the parameter code."""
        return {"code": PARAM_BOOSTER}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the booster."""
        await self.coordinator.async_write_param(self._device_code, PARAM_BOOSTER, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the booster. M06 uses 2=Off (not 0)."""
        await self.coordinator.async_write_param(self._device_code, PARAM_BOOSTER, 2)
