"""Binary sensor platform for HiTemp integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ALL_PARAM_DEFS,
    BINARY_STATUS_PARAMS,
    DOMAIN,
)
from .coordinator import HiTempCoordinator

_LOGGER = logging.getLogger(__name__)

# Mapping of param codes to device classes
PARAM_DEVICE_CLASS_MAP: dict[str, BinarySensorDeviceClass | None] = {
    "Power": BinarySensorDeviceClass.POWER,
    "O01": BinarySensorDeviceClass.RUNNING,  # Compressor
    "O02": BinarySensorDeviceClass.RUNNING,  # Heater
    "O03": None,  # 4-way valve
    "O04": BinarySensorDeviceClass.RUNNING,  # Fan high
    "O05": BinarySensorDeviceClass.RUNNING,  # Fan low
    "O06": BinarySensorDeviceClass.RUNNING,  # Solar pump
    "O10": None,  # 3V_DE
    "O11": None,  # MV_DE
    "O12": None,  # Shutdown
    "O13": BinarySensorDeviceClass.CONNECTIVITY,  # WiFi status
    "O14": BinarySensorDeviceClass.RUNNING,  # Defrost
    "O15": None,  # High temp stage
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HiTemp binary sensor entities."""
    coordinator: HiTempCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[HiTempBinarySensor] = []
    for device in coordinator.devices:
        device_code = device.get("deviceCode")
        if not device_code:
            continue

        for param_code in BINARY_STATUS_PARAMS:
            if param_code in ALL_PARAM_DEFS:
                param = ALL_PARAM_DEFS[param_code]
                device_class = PARAM_DEVICE_CLASS_MAP.get(param_code)
                # Power is main entity, others are diagnostic
                entity_category = None if param_code == "Power" else EntityCategory.DIAGNOSTIC

                entities.append(
                    HiTempBinarySensor(
                        coordinator=coordinator,
                        device_code=device_code,
                        param_code=param_code,
                        name=param.name,
                        device_class=device_class,
                        entity_category=entity_category,
                    )
                )

    async_add_entities(entities)


class HiTempBinarySensor(CoordinatorEntity[HiTempCoordinator], BinarySensorEntity):
    """Binary sensor entity for HiTemp parameters."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
        param_code: str,
        name: str,
        device_class: BinarySensorDeviceClass | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._param_code = param_code
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_entity_category = entity_category
        self._attr_unique_id = f"{device_code}_{param_code}"

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
        """Return true if the binary sensor is on."""
        value = self.coordinator.get_device_param(self._device_code, self._param_code)
        if value is None:
            return None
        return str(value) == "1"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes including the parameter code."""
        return {"code": self._param_code}
