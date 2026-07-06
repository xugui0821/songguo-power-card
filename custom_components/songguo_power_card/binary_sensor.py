"""Binary sensor platform for Songguo Power Card."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SongguoPowerCardCoordinator
from .entity import SongguoPowerCardEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor."""
    coordinator: SongguoPowerCardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SongguoPowerStateBinarySensor(coordinator, entry)])


class SongguoPowerStateBinarySensor(
    SongguoPowerCardEntity,
    BinarySensorEntity,
):
    """Represent the computer power state."""

    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_translation_key = "power_state"

    def __init__(self, coordinator: SongguoPowerCardCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_power_state"

    @property
    def is_on(self) -> bool | None:
        """Return the current power state."""
        return self.coordinator.data.is_on if self.coordinator.data else None
