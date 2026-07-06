"""Switch platform for Songguo Power Card."""

from __future__ import annotations

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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
    """Set up the switch."""
    coordinator: SongguoPowerCardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SongguoPowerCardSwitch(coordinator, entry)])


class SongguoPowerCardSwitch(SongguoPowerCardEntity, SwitchEntity):
    """Represent the computer power switch."""

    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_translation_key = "power_switch"

    def __init__(self, coordinator: SongguoPowerCardCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_power_switch"

    @property
    def is_on(self) -> bool | None:
        """Return the current power state."""
        return self.coordinator.data.is_on if self.coordinator.data else None

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn the computer on."""
        await self.coordinator.async_send_command(1)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn the computer off."""
        await self.coordinator.async_send_command(0)
