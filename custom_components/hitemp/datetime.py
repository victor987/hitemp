"""Datetime platform for HiTemp integration."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

from homeassistant.components.datetime import DateTimeEntity
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
DATETIME_PARAM_CODES = {"M12", "M13", "M14", "M15", "M16"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HiTemp datetime entities."""
    coordinator: HiTempCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[HiTempDeviceDatetime] = []
    for device in coordinator.devices:
        device_code = device.get("deviceCode")
        if not device_code:
            continue
        entities.append(HiTempDeviceDatetime(coordinator, device_code))

    async_add_entities(entities)


class HiTempDeviceDatetime(CoordinatorEntity[HiTempCoordinator], DateTimeEntity):
    """Device datetime from M12-M16."""

    _attr_has_entity_name = True
    _attr_name = "Device time"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: HiTempCoordinator, device_code: str) -> None:
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_device_datetime"

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
    def native_value(self) -> datetime | None:
        get = lambda code: self.coordinator.get_device_param(self._device_code, code)
        year = get("M16")
        month = get("M15")
        day = get("M14")
        hour = get("M13")
        minute = get("M12")
        if any(v is None for v in (year, month, day, hour, minute)):
            return None
        try:
            return datetime(
                2000 + int(float(year)),
                int(float(month)),
                int(float(day)),
                int(float(hour)),
                int(float(minute)),
                tzinfo=timezone.utc,
            )
        except (ValueError, TypeError):
            return None

    async def async_set_value(self, value: datetime) -> None:
        write = self.coordinator.async_write_param
        dc = self._device_code
        await write(dc, "M16", value.year - 2000)
        await write(dc, "M15", value.month)
        await write(dc, "M14", value.day)
        await write(dc, "M13", value.hour)
        await write(dc, "M12", value.minute)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"codes": "M12 (min), M13 (hour), M14 (day), M15 (month), M16 (year)"}
