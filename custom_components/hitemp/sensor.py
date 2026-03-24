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
    UnitOfPower,
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
    BITMASK_PARAMS,
    DOMAIN,
    NUMERIC_SENSOR_PARAMS,
    TEMP_SENSOR_PARAMS,
)
from .coordinator import HiTempCoordinator

_LOGGER = logging.getLogger(__name__)

# TODO: Investigate if power switch is redundant with climate entity on/off
#   Test with app/physical controls: does Power=0 fully shut down the device,
# TODO: Investigate O28 (alt 2066) — range 1-17, disabled.
#   Values >12 returned as negative with .6 offset (13→-12.6, 14→-11.6, etc).
#   Corrected with 25.6-v for negatives. Purpose unknown.
#   or is it the same as climate off (standby/idle)?


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

                enabled_default = param_code not in BITMASK_PARAMS and param_code not in {
                    "L31", "L32", "O28", "O07", "O08", "O29", "T09",
                }

                # Integer-valued sensors: hide the .0 decimal
                display_precision = 0 if param.unit != "°C" else None

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
                        enabled_default=enabled_default,
                        display_precision=display_precision,
                    )
                )

        # Add WiFi signal sensor (from device metadata)
        entities.append(
            HiTempWifiSensor(coordinator, device_code)
        )

        # Add temperature delta sensors
        for key, name, param_a, param_b in TEMP_DELTAS:
            entities.append(
                HiTempTempDeltaSensor(coordinator, device_code, key, name, param_a, param_b)
            )
        entities.append(
            HiTempPreciseTempSensor(coordinator, device_code)
        )
        entities.append(
            HiTempEnergyStoredMaxSensor(coordinator, device_code)
        )
        entities.append(
            HiTempEnergyStoredMinSensor(coordinator, device_code)
        )
        entities.append(
            HiTempEnergyStoredSensor(coordinator, device_code)
        )
        entities.append(
            HiTempCOPSensor(coordinator, device_code)
        )
        entities.append(
            HiTempPowerSensor(coordinator, device_code)
        )
        entities.append(
            HiTempEnergySensor(coordinator, device_code)
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
        enabled_default: bool = True,
        display_precision: int | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_entity_registry_enabled_default = enabled_default
        if display_precision is not None:
            self._attr_suggested_display_precision = display_precision
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
        # Treat empty strings as None (API returns '' for unavailable parameters)
        if value is not None and value != '':
            try:
                if self._param_code in BITMASK_PARAMS:
                    return int(str(value), 2)
                if self._param_code == "O28":
                    v = float(value)
                    return int(25.6 - v) if v < 0 else int(v)
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
    _attr_entity_registry_enabled_default = False

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


TEMP_DELTAS = [
    ("temp_difference", "Temperature difference", "T02", "T01"),
    ("superheat", "Superheat", "T05", "T04"),
    ("condenser_approach", "Condenser approach", "T07", "T02"),
    ("lift", "Lift", "T02", "T04"),
]


class HiTempTempDeltaSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Temperature delta sensor (param_a - param_b)."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
        key: str,
        name: str,
        param_a: str,
        param_b: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._param_a = param_a
        self._param_b = param_b
        self._attr_name = name
        self._attr_unique_id = f"{device_code}_{key}"

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
        """Return param_a - param_b."""
        val_a = self.coordinator.get_device_param(self._device_code, self._param_a)
        val_b = self.coordinator.get_device_param(self._device_code, self._param_b)
        if val_a is not None and val_b is not None:
            try:
                return round(float(val_a) - float(val_b), 1)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        val_a = self.coordinator.get_device_param(self._device_code, self._param_a)
        val_b = self.coordinator.get_device_param(self._device_code, self._param_b)
        return {
            "formula": f"{self._param_a} - {self._param_b}",
            self._param_a: val_a,
            self._param_b: val_b,
        }


class HiTempPreciseTempSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Average of T02 and T03 when within threshold."""

    _attr_has_entity_name = True
    _attr_name = "Precise temperature"
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
        self._attr_unique_id = f"{device_code}_precise_temp"

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
        """Return avg(T02, T03) if within threshold, else None."""
        return self.coordinator.get_precise_temperature(self._device_code)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        t02 = self.coordinator.get_device_param(self._device_code, "T02")
        t03 = self.coordinator.get_device_param(self._device_code, "T03")
        threshold = self.coordinator.get_precise_temp_threshold(self._device_code)
        return {
            "formula": "avg(T02, T03) when |T02-T03| <= threshold",
            "T02_bottom": t02,
            "T03_top": t03,
            "threshold": threshold,
        }


class HiTempEnergyStoredMaxSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Energy stored based on T03 (top)."""

    _attr_has_entity_name = True
    _attr_name = "Energy stored (max)"
    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator: HiTempCoordinator, device_code: str) -> None:
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_energy_stored_max"

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
    def native_value(self) -> StateType:
        return self.coordinator.get_energy_stored_max(self._device_code)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        t03 = self.coordinator.get_device_param(self._device_code, "T03")
        return {"source": "T03", "T03_top": t03}


class HiTempEnergyStoredMinSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Energy stored based on T02 (bottom)."""

    _attr_has_entity_name = True
    _attr_name = "Energy stored (min)"
    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator: HiTempCoordinator, device_code: str) -> None:
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_energy_stored_min"

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
    def native_value(self) -> StateType:
        return self.coordinator.get_energy_stored_min(self._device_code)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        t02 = self.coordinator.get_device_param(self._device_code, "T02")
        return {"source": "T02", "T02_bottom": t02}


class HiTempEnergyStoredSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Energy stored based on avg(T02, T03) when within threshold."""

    _attr_has_entity_name = True
    _attr_name = "Energy stored"
    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator: HiTempCoordinator, device_code: str) -> None:
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_energy_stored"

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
    def native_value(self) -> StateType:
        return self.coordinator.get_energy_stored_precise(self._device_code)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        t02 = self.coordinator.get_device_param(self._device_code, "T02")
        t03 = self.coordinator.get_device_param(self._device_code, "T03")
        threshold = self.coordinator.get_energy_stored_threshold(self._device_code)
        return {
            "formula": "avg(energy_max, energy_min) when diff <= threshold",
            "T02_bottom": t02,
            "T03_top": t03,
            "threshold_kwh": threshold,
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
        # Always visible - availability conditions preserved for later
        # if not self.coordinator.last_update_success:
        #     return False
        # device = self.coordinator.get_device_info(self._device_code)
        # if device:
        #     return device.get("deviceStatus") == "ONLINE"
        # return False
        return True

    @property
    def native_value(self) -> StateType:
        """Return COP value."""
        return self.coordinator.get_cop(self._device_code)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        energy_id = self.coordinator._find_entity_by_device_class("energy")
        return {
            "energy_sensor": energy_id or "(not configured)",
            "note": "COP updates when energy meter changes",
        }


class HiTempPowerSensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Power reading from configured power meter device."""

    _attr_has_entity_name = True
    _attr_name = "Power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(self, coordinator: HiTempCoordinator, device_code: str) -> None:
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_power_meter"

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
        return self.coordinator.get_power_reading() is not None

    @property
    def native_value(self) -> StateType:
        return self.coordinator.get_power_reading()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        source = self.coordinator._find_entity_by_device_class("power")
        return {"source": source or "(not configured)"}


class HiTempEnergySensor(CoordinatorEntity[HiTempCoordinator], SensorEntity):
    """Energy reading from configured power meter device."""

    _attr_has_entity_name = True
    _attr_name = "Energy"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator: HiTempCoordinator, device_code: str) -> None:
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_energy_meter"

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
        return self.coordinator._get_energy_meter() is not None

    @property
    def native_value(self) -> StateType:
        return self.coordinator._get_energy_meter()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        source = self.coordinator._find_entity_by_device_class("energy")
        return {"source": source or "(not configured)"}
