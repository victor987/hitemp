"""Climate platform for HiTemp integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MAX_TEMP,
    MIN_TEMP,
    MODE_TO_PRESET,
    PRESET_TO_MODE,
)
from .coordinator import HiTempCoordinator

_LOGGER = logging.getLogger(__name__)

# Parameter codes used by climate entity
PARAM_POWER = "Power"
PARAM_MODE = "mode_real"
PARAM_TARGET_TEMP = "R01"
PARAM_TEMP_BOTTOM = "T02"
PARAM_TEMP_TOP = "T03"
PARAM_COMPRESSOR_STATUS = "O01"
PARAM_HEATER_STATUS = "O02"
PARAM_DEFROST_STATUS = "O14"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HiTemp climate entities."""
    coordinator: HiTempCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        HiTempClimate(coordinator, device["deviceCode"])
        for device in coordinator.devices
        if device.get("deviceCode")
    ]

    async_add_entities(entities)


class HiTempClimate(CoordinatorEntity[HiTempCoordinator], ClimateEntity):
    """Climate entity for HiTemp water heater."""

    _attr_has_entity_name = True
    _attr_name = None  # Use device name as entity name
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_target_temperature_step = 1.0
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_preset_modes = list(PRESET_TO_MODE.keys())
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(
        self,
        coordinator: HiTempCoordinator,
        device_code: str,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_climate"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device = self.coordinator.get_device_info(self._device_code)
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_code)},
            name=device.get("deviceNickName", "HiTemp Water Heater") if device else "HiTemp Water Heater",
            manufacturer="HiTemp",
            model="PV300",
            serial_number=device.get("serialNumber") if device else None,
            sw_version=device.get("wifiSoftwareVer") if device else None,
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
    def current_temperature(self) -> float | None:
        """Return current temperature (average of bottom and top)."""
        bottom = self.coordinator.get_device_param(self._device_code, PARAM_TEMP_BOTTOM)
        top = self.coordinator.get_device_param(self._device_code, PARAM_TEMP_TOP)

        if bottom is not None and top is not None:
            try:
                return (float(bottom) + float(top)) / 2
            except (ValueError, TypeError):
                pass

        return None

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        value = self.coordinator.get_device_param(self._device_code, PARAM_TARGET_TEMP)
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        power = self.coordinator.get_device_param(self._device_code, PARAM_POWER)
        if power is not None:
            try:
                if int(power) == 0:
                    return HVACMode.OFF
            except (ValueError, TypeError):
                pass
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action."""
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF

        # Check defrost first
        defrost = self.coordinator.get_device_param(self._device_code, PARAM_DEFROST_STATUS)
        if defrost:
            try:
                if int(defrost) == 1:
                    return HVACAction.DEFROSTING
            except (ValueError, TypeError):
                pass

        # Check compressor
        compressor = self.coordinator.get_device_param(self._device_code, PARAM_COMPRESSOR_STATUS)
        if compressor:
            try:
                if int(compressor) == 1:
                    return HVACAction.HEATING
            except (ValueError, TypeError):
                pass

        # Check electric heater
        heater = self.coordinator.get_device_param(self._device_code, PARAM_HEATER_STATUS)
        if heater:
            try:
                if int(heater) == 1:
                    return HVACAction.HEATING
            except (ValueError, TypeError):
                pass

        return HVACAction.IDLE

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        mode = self.coordinator.get_device_param(self._device_code, PARAM_MODE)
        if mode is not None:
            try:
                mode_int = int(mode)
                return MODE_TO_PRESET.get(mode_int)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes including parameter codes."""
        return {
            "target_temp_code": PARAM_TARGET_TEMP,
            "mode_code": PARAM_MODE,
            "power_code": PARAM_POWER,
            "current_temp_codes": f"{PARAM_TEMP_BOTTOM}, {PARAM_TEMP_TOP}",
        }

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        await self.coordinator.async_write_param(
            self._device_code, PARAM_TARGET_TEMP, float(temperature)
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        elif hvac_mode == HVACMode.HEAT:
            await self.async_turn_on()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        mode_value = PRESET_TO_MODE.get(preset_mode)
        if mode_value is not None:
            await self.coordinator.async_write_param(
                self._device_code, PARAM_MODE, mode_value
            )

    async def async_turn_on(self) -> None:
        """Turn on the water heater."""
        await self.coordinator.async_write_param(self._device_code, PARAM_POWER, 1)

    async def async_turn_off(self) -> None:
        """Turn off the water heater."""
        await self.coordinator.async_write_param(self._device_code, PARAM_POWER, 0)
