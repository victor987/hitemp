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
    UnitOfEnergy,
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

        # Add computed sensors
        entities.append(
            HiTempTempDifferenceSensor(coordinator, device_code)
        )
        entities.append(
            HiTempEnergyStoredSensor(coordinator, device_code)
        )
        entities.append(
            HiTempCOPSensor(coordinator, device_code)
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


class HiTempTempDifferenceSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Temperature difference sensor (T02 - T01)."""

    _attr_has_entity_name = True
    _attr_name = "Temperature difference"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_temp_difference"

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
        """Return T02 - T01 (bottom water temp minus ambient)."""
        t01 = self.coordinator.get_device_param(self._device_code, "T01")
        t02 = self.coordinator.get_device_param(self._device_code, "T02")
        if t01 is not None and t02 is not None:
            try:
                return round(float(t02) - float(t01), 1)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        t01 = self.coordinator.get_device_param(self._device_code, "T01")
        t02 = self.coordinator.get_device_param(self._device_code, "T02")
        return {
            "formula": "T02 - T01",
            "T01_ambient": t01,
            "T02_bottom": t02,
        }


class HiTempEnergyStoredSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Energy stored in the tank relative to 0°C."""

    _attr_has_entity_name = True
    _attr_name = "Energy stored"
    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    # Tank capacity in liters (= kg of water)
    TANK_VOLUME_LITERS = 300
    # Specific heat of water: 4.186 kJ/(kg·K) = 0.001163 kWh/(kg·K)
    SPECIFIC_HEAT_KWH = 0.001163

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_energy_stored"

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
        """Return energy stored: 300kg × 0.001163 kWh/(kg·K) × T02."""
        t02 = self.coordinator.get_device_param(self._device_code, "T02")
        if t02 is not None:
            try:
                temp = float(t02)
                # Energy = mass × specific_heat × temperature
                energy = self.TANK_VOLUME_LITERS * self.SPECIFIC_HEAT_KWH * temp
                return round(energy, 2)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        t02 = self.coordinator.get_device_param(self._device_code, "T02")
        return {
            "formula": "300L × 0.001163 kWh/(kg·K) × T02",
            "tank_volume_liters": self.TANK_VOLUME_LITERS,
            "T02_bottom": t02,
        }


class HiTempCOPSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """COP (Coefficient of Performance) sensor."""

    _attr_has_entity_name = True
    _attr_name = "COP"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = None
    _attr_icon = "mdi:heat-pump"

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_cop"

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
        """Return COP value (only valid when heating and no water draw)."""
        return self.coordinator.get_cop(self._device_code)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        is_valid = self.coordinator.is_cop_valid(self._device_code)
        is_compressor_running = self.coordinator.is_compressor_running(self._device_code)
        o29 = self.coordinator.get_device_param(self._device_code, "O29")
        return {
            "valid": is_valid,
            "compressor_running": is_compressor_running,
            "O29_compressor_speed_hz": o29,
            "energy_sensor": "sensor.water_heater_energy",
            "note": "COP calculated when compressor running (O29>0) and no water draw detected",
        }
