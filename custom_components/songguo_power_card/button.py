"""Button platform for Songguo Power Card."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SongguoPowerCardCoordinator
from .entity import SongguoPowerCardEntity


@dataclass(frozen=True)
class SongguoButtonDescription:
    """Button description."""

    key: str
    translation_key: str
    value: int
    device_class: ButtonDeviceClass | None = None


BUTTONS: tuple[SongguoButtonDescription, ...] = (
    SongguoButtonDescription("power_on", "power_on", 1),
    SongguoButtonDescription("power_off", "power_off", 0),
    SongguoButtonDescription(
        "restart",
        "restart",
        25,
        ButtonDeviceClass.RESTART,
    ),
    SongguoButtonDescription(
        "force_power_off",
        "force_power_off",
        14,
    ),
    SongguoButtonDescription(
        "force_restart",
        "force_restart",
        2,
        ButtonDeviceClass.RESTART,
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
        self._attr_translation_key = description.translation_key
        self._attr_device_class = description.device_class

    async def async_press(self) -> None:
        """Send the power command."""
        await self.coordinator.async_send_command(self.entity_description.value)
