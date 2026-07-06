"""Button platform for Songguo Power Card."""

from __future__ import annotations

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SongguoPowerCardCoordinator
from .entity import SongguoPowerCardEntity


class SongguoButtonDescription(ButtonEntityDescription):
    """Button description."""

    value: int


BUTTONS: tuple[SongguoButtonDescription, ...] = (
    SongguoButtonDescription(key="power_on", translation_key="power_on", value=1),
    SongguoButtonDescription(key="power_off", translation_key="power_off", value=0),
    SongguoButtonDescription(
        key="restart",
        translation_key="restart",
        value=25,
        device_class=ButtonDeviceClass.RESTART,
    ),
    SongguoButtonDescription(
        key="force_power_off",
        translation_key="force_power_off",
        value=14,
    ),
    SongguoButtonDescription(
        key="force_restart",
        translation_key="force_restart",
        value=2,
        device_class=ButtonDeviceClass.RESTART,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up buttons."""
    coordinator: SongguoPowerCardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SongguoPowerCardButton(coordinator, entry, description) for description in BUTTONS
    )


class SongguoPowerCardButton(
    SongguoPowerCardEntity,
    ButtonEntity,
):
    """Represent a Songguo power command button."""

    entity_description: SongguoButtonDescription

    def __init__(
        self,
        coordinator: SongguoPowerCardCoordinator,
        entry: ConfigEntry,
        description: SongguoButtonDescription,
    ) -> None:
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    async def async_press(self) -> None:
        """Send the power command."""
        await self.coordinator.async_send_command(self.entity_description.value)
