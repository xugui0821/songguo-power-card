"""Config flow for Songguo Power Card."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    SongguoApiClient,
    SongguoApiError,
    SongguoAuthError,
)
from .const import CONF_ACCOUNT, CONF_DEVICE_NAME, CONF_PASSWORD, DEFAULT_NAME, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCOUNT): str,
        vol.Required(CONF_PASSWORD): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        ),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)


class SongguoPowerCardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Songguo Power Card."""

    VERSION = 1
    _user_input: dict[str, Any]
    _devices: list[dict[str, Any]]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Collect credentials and fetch devices."""
        errors: dict[str, str] = {}

        if user_input is not None:
            client = SongguoApiClient(
                session=async_get_clientsession(self.hass),
                account=user_input[CONF_ACCOUNT],
                password=user_input[CONF_PASSWORD],
                device_name="",
            )

            try:
                devices = await client.async_list_devices()
            except SongguoAuthError:
                errors["base"] = "invalid_auth"
            except SongguoApiError:
                errors["base"] = "cannot_connect"
            else:
                named_devices = [
                    device for device in devices if isinstance(device.get("deviceName"), str)
                ]
                if not named_devices:
                    errors["base"] = "no_devices"
                else:
                    self._user_input = user_input
                    self._devices = named_devices
                    return await self.async_step_device()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Let the user choose a device from the Songguo device list."""
        errors: dict[str, str] = {}
        device_names = [device["deviceName"] for device in self._devices]

        if user_input is not None:
            device_name = user_input[CONF_DEVICE_NAME]
            await self.async_set_unique_id(f"{self._user_input[CONF_ACCOUNT]}_{device_name}")
            self._abort_if_unique_id_configured()

            data = {
                **self._user_input,
                CONF_DEVICE_NAME: device_name,
            }
            title = data.get(CONF_NAME) or device_name or DEFAULT_NAME
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE_NAME): vol.In(device_names)}),
            errors=errors,
        )
