"""Client for the Songguo open API."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, unquote

import aiohttp

CONTROL_URL = "https://songguoyun.topwd.top/Esp_Api_new.php"
ADVANCE_URL = "https://songguoyun.topwd.top/Esp_Api_advance.php"
REQUEST_TIMEOUT = 15

STATUS_SUCCESS = 0
STATUS_FAILED = -1
STATUS_BAD_AUTH = -2
STATUS_DEVICE_NOT_FOUND = -3
STATUS_OFFLINE = 2

POWER_OFF = 0
POWER_ON = 1
QUERY_STATUS = 11


class SongguoApiError(Exception):
    """Base API error."""


class SongguoAuthError(SongguoApiError):
    """Raised when account or password is invalid."""


class SongguoDeviceNotFoundError(SongguoApiError):
    """Raised when the configured device does not exist."""


class SongguoDeviceOfflineError(SongguoApiError):
    """Raised when the configured device is offline."""


@dataclass(frozen=True)
class SongguoStatus:
    """Power status returned by Songguo."""

    raw: int

    @property
    def is_on(self) -> bool | None:
        """Return True for on, False for off, None for unknown/offline."""
        if self.raw == POWER_ON:
            return True
        if self.raw == POWER_OFF:
            return False
        return None


class SongguoApiClient:
    """Small async client for Songguo's urlencoded JSON API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        account: str,
        password: str,
        device_name: str,
    ) -> None:
        self._session = session
        self._account = account
        self._password = password
        self._device_name = device_name

    async def async_control(self, value: int) -> int:
        """Send a control command and return the integer API status."""
        payload = {
            "sgdz_account": self._account,
            "sgdz_password": self._password,
            "device_name": self._device_name,
            "value": str(value),
        }
        data = await self._post_json(CONTROL_URL, payload)
        status = self._extract_status(data)
        self._raise_for_status(status)
        return status

    async def async_query_status(self) -> SongguoStatus:
        """Query the configured device power status."""
        status = await self.async_control(QUERY_STATUS)
        return SongguoStatus(status)

    async def async_list_devices(self) -> list[dict[str, Any]]:
        """Return devices from the Songguo account."""
        payload = {
            "sgdz_account": self._account,
            "sgdz_password": self._password,
            "type": 1,
        }
        data = await self._post_json(ADVANCE_URL, payload)
        if "deviceslist" not in data:
            status = self._extract_status(data)
            self._raise_for_status(status)
            raise SongguoApiError("Songguo API response has no device list")

        devices = data["deviceslist"]
        if not isinstance(devices, list):
            raise SongguoApiError("Songguo API returned an invalid device list")
        return devices

    async def async_device_exists(self) -> bool:
        """Check whether the configured device appears in the device list."""
        for device in await self.async_list_devices():
            if device.get("deviceName") == self._device_name:
                return True
        return False

    async def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        encoded_payload = quote(json.dumps(payload, ensure_ascii=False))

        try:
            async with self._session.post(
                url,
                data=encoded_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as response:
                response.raise_for_status()
                text = await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise SongguoApiError(f"Songguo API request failed: {err}") from err

        decoded = unquote(text).strip()
        try:
            parsed = json.loads(decoded)
        except json.JSONDecodeError as err:
            raise SongguoApiError(f"Songguo API returned invalid JSON: {decoded}") from err

        if not isinstance(parsed, dict):
            raise SongguoApiError("Songguo API returned an unexpected response")
        return parsed

    @staticmethod
    def _extract_status(data: dict[str, Any]) -> int:
        try:
            return int(data["status"])
        except (KeyError, TypeError, ValueError) as err:
            raise SongguoApiError(f"Songguo API response has no valid status: {data}") from err

    @staticmethod
    def _raise_for_status(status: int) -> None:
        if status == STATUS_BAD_AUTH:
            raise SongguoAuthError("Songguo account or password is invalid")
        if status == STATUS_DEVICE_NOT_FOUND:
            raise SongguoDeviceNotFoundError("Songguo device does not exist")
        if status == STATUS_OFFLINE:
            raise SongguoDeviceOfflineError("Songguo device is offline")
        if status == STATUS_FAILED:
            raise SongguoApiError("Songguo command failed")
