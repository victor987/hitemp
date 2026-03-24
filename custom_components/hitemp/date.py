"""Date platform for HiTemp integration."""

from __future__ import annotations

from datetime import date
import logging
from typing import Any

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HiTempCoordinator

_LOGGER = logging.getLogger(__name__)

# Codes handled here, to exclude from number entities
DATE_PARAM_CODES = {"L02", "L03", "L04"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HiTemp date entities."""
    coordinator: HiTempCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[HiTempTimerDate] = []
    for device in coordinator.devices:
        device_code = device.get("deviceCode")
        if not device_code:
            continue
        entities.append(HiTempTimerDate(coordinator, device_code))

    async_add_entities(entities)


class HiTempTimerDate(CoordinatorEntity[HiTempCoordinator], DateEntity):
    """Timer schedule date from L02-L04."""

    _attr_has_entity_name = True
    _attr_name = "Timer date"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: HiTempCoordinator, device_code: str) -> None:
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_timer_date"

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
    def native_value(self) -> date | None:
        get = lambda code: self.coordinator.get_device_param(self._device_code, code)
        year = get("L02")
        month = get("L03")
        day = get("L04")
        if any(v is None for v in (year, month, day)):
            return None
        try:
            return date(2000 + int(float(year)), int(float(month)), int(float(day)))
        except (ValueError, TypeError):
            return None

    async def async_set_value(self, value: date) -> None:
        write = self.coordinator.async_write_param
        dc = self._device_code
        await write(dc, "L02", value.year - 2000)
        await write(dc, "L03", value.month)
        await write(dc, "L04", value.day)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"codes": "L02 (year), L03 (month), L04 (day)"}
