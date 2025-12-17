"""Sensor platform for HiTemp integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfFrequency,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ALL_PARAM_DEFS,
    DOMAIN,
    NUMERIC_SENSOR_PARAMS,
    TEMP_SENSOR_PARAMS,
)
from .coordinator import HiTempCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HiTemp sensor entities."""
    coordinator: HiTempCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[HiTempSensor] = []
    for device in coordinator.devices:
        device_code = device.get("deviceCode")
        if not device_code:
            continue

        # Add temperature sensors
        for param_code in TEMP_SENSOR_PARAMS:
            if param_code in ALL_PARAM_DEFS:
                param = ALL_PARAM_DEFS[param_code]
                entities.append(
                    HiTempSensor(
                        coordinator=coordinator,
                        device_code=device_code,
                        param_code=param_code,
                        name=param.name,
                        device_class=SensorDeviceClass.TEMPERATURE,
                        state_class=SensorStateClass.MEASUREMENT,
                        native_unit=UnitOfTemperature.CELSIUS,
                    )
                )

        # Add numeric sensors (O codes, counters, etc.)
        for param_code in NUMERIC_SENSOR_PARAMS:
            if param_code in ALL_PARAM_DEFS:
                param = ALL_PARAM_DEFS[param_code]
                device_class = None
                state_class = SensorStateClass.MEASUREMENT
                native_unit = None
                entity_category = EntityCategory.DIAGNOSTIC

                # Determine device class and unit based on parameter
                if param.unit == "h":
                    device_class = SensorDeviceClass.DURATION
                    state_class = SensorStateClass.TOTAL_INCREASING
                    native_unit = UnitOfTime.HOURS
                elif param.unit == "Hz":
                    device_class = SensorDeviceClass.FREQUENCY
                    native_unit = UnitOfFrequency.HERTZ
                elif param.unit == "°C":
                    device_class = SensorDeviceClass.TEMPERATURE
                    native_unit = UnitOfTemperature.CELSIUS

                entities.append(
                    HiTempSensor(
                        coordinator=coordinator,
                        device_code=device_code,
                        param_code=param_code,
                        name=param.name,
                        device_class=device_class,
                        state_class=state_class,
                        native_unit=native_unit,
                        entity_category=entity_category,
                    )
                )

        # Add WiFi signal sensor (from device metadata)
        entities.append(
            HiTempWifiSensor(coordinator, device_code)
        )

    async_add_entities(entities)


class HiTempSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Sensor entity for HiTemp parameters."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
        param_code: str,
        name: str,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_unit: str | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._param_code = param_code
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = native_unit
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
    def native_value(self) -> StateType:
        """Return the sensor value."""
        value = self.coordinator.get_device_param(self._device_code, self._param_code)
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return value
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes including the parameter code."""
        return {"code": self._param_code}


class HiTempWifiSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """WiFi signal strength sensor from device metadata."""

    _attr_has_entity_name = True
    _attr_name = "WiFi signal"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_wifi_signal"

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
    def native_value(self) -> StateType:
        """Return the WiFi signal strength."""
        device = self.coordinator.get_device_info(self._device_code)
        if device:
            signal = device.get("dtuSignalIntensity")
            if signal is not None:
                try:
                    return int(signal)
                except (ValueError, TypeError):
                    pass
        return None
