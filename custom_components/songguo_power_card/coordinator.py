"""Data coordinator for Songguo Power Card."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SongguoApiClient, SongguoApiError, SongguoStatus
from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=30)
_LOGGER = logging.getLogger(__name__)


class SongguoPowerCardCoordinator(DataUpdateCoordinator[SongguoStatus]):
    """Coordinate Songguo status updates."""

    def __init__(self, hass: HomeAssistant, client: SongguoApiClient, name: str) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=name,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> SongguoStatus:
        """Fetch current power status."""
        try:
            return await self.client.async_query_status()
        except SongguoApiError as err:
            raise UpdateFailed(str(err)) from err

    async def async_send_command(self, value: int) -> None:
        """Send a command, then refresh status."""
        try:
            await self.client.async_control(value)
        except SongguoApiError as err:
            raise UpdateFailed(str(err)) from err
        await self.async_request_refresh()
