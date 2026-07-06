"""Songguo Power Card integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SongguoApiClient
from .const import CONF_ACCOUNT, CONF_DEVICE_NAME, CONF_PASSWORD, DEFAULT_NAME, DOMAIN
from .coordinator import SongguoPowerCardCoordinator

PLATFORMS = ["binary_sensor", "button", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Songguo Power Card from a config entry."""
    client = SongguoApiClient(
        session=async_get_clientsession(hass),
        account=entry.data[CONF_ACCOUNT],
        password=entry.data[CONF_PASSWORD],
        device_name=entry.data[CONF_DEVICE_NAME],
    )
    coordinator = SongguoPowerCardCoordinator(
        hass,
        client,
        entry.data.get(CONF_NAME, DEFAULT_NAME),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
