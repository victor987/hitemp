"""Number platform for HiTemp integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ALL_PARAM_DEFS,
    DOMAIN,
    WRITABLE_NUMBER_PARAMS,
)
from .coordinator import HiTempCoordinator

_LOGGER = logging.getLogger(__name__)

# Unit mapping from param.unit to HA units
UNIT_MAP: dict[str, str | None] = {
    "°C": UnitOfTemperature.CELSIUS,
    "min": UnitOfTime.MINUTES,
    "h": UnitOfTime.HOURS,
    "days": UnitOfTime.DAYS,
    "Hz": "Hz",
    "year": None,
    "month": None,
    "day": None,
    None: None,
}

# Device class mapping based on unit
DEVICE_CLASS_MAP: dict[str, NumberDeviceClass | None] = {
    "°C": NumberDeviceClass.TEMPERATURE,
    "min": NumberDeviceClass.DURATION,
    "h": NumberDeviceClass.DURATION,
    "days": NumberDeviceClass.DURATION,
    "Hz": None,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HiTemp number entities."""
    coordinator: HiTempCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[HiTempNumber] = []
    for device in coordinator.devices:
        device_code = device.get("deviceCode")
        if not device_code:
            continue

        for param_code in WRITABLE_NUMBER_PARAMS:
            if param_code in ALL_PARAM_DEFS:
                param = ALL_PARAM_DEFS[param_code]

                # Determine unit and device class
                native_unit = UNIT_MAP.get(param.unit)
                device_class = DEVICE_CLASS_MAP.get(param.unit)

                # Get min/max values
                min_value = param.min_value if param.min_value is not None else 0
                max_value = param.max_value if param.max_value is not None else 65535

                entities.append(
                    HiTempNumber(
                        coordinator=coordinator,
                        device_code=device_code,
                        param_code=param_code,
                        name=param.name,
                        native_unit=native_unit,
                        device_class=device_class,
                        min_value=min_value,
                        max_value=max_value,
                    )
                )

    async_add_entities(entities)


class HiTempNumber(CoordinatorEntity[HiTempCoordinator], NumberEntity):
    """Number entity for HiTemp writable parameters."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_step = 1.0

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
        param_code: str,
        name: str,
        native_unit: str | None = None,
        device_class: NumberDeviceClass | None = None,
        min_value: float = 0,
        max_value: float = 65535,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._param_code = param_code
        self._attr_name = name
        self._attr_native_unit_of_measurement = native_unit
        self._attr_device_class = device_class
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
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
    def native_value(self) -> float | None:
        """Return the current value."""
        value = self.coordinator.get_device_param(self._device_code, self._param_code)
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self.coordinator.async_write_param(
            self._device_code, self._param_code, int(value)
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes including the parameter code."""
        return {"code": self._param_code}
