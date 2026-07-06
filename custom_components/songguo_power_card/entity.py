"""Shared entity helpers for Songguo Power Card."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_NAME, DOMAIN
from .coordinator import SongguoPowerCardCoordinator


class SongguoPowerCardEntity(CoordinatorEntity[SongguoPowerCardCoordinator]):
    """Base entity for Songguo Power Card."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SongguoPowerCardCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data[CONF_DEVICE_NAME],
            manufacturer="Songguo Electronics",
            model="Power Card",
        )
