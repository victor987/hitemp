"""API client for HiTemp water heater."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import aiohttp

from .const import (
    API_CONTROL,
    API_DEVICE_LIST,
    API_GET_DATA,
    API_LOGIN,
    BASE_URL,
    PRODUCT_ID,
)

_LOGGER = logging.getLogger(__name__)


class HiTempAuthError(Exception):
    """Exception for authentication errors."""


class HiTempConnectionError(Exception):
    """Exception for connection errors."""


class HiTempApiClient:
    """API client for HiTemp water heater."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._username = username
        self._password = password
        self._token: str | None = None
        self._user_id: str | None = None

    @property
    def token(self) -> str | None:
        """Return the current token."""
        return self._token

    @property
    def user_id(self) -> str | None:
        """Return the current user ID."""
        return self._user_id

    async def login(self) -> str:
        """Login and return the token."""
        password_md5 = hashlib.md5(self._password.encode()).hexdigest()

        try:
            async with self._session.post(
                f"{BASE_URL}{API_LOGIN}",
                headers={"Content-Type": "application/json; charset=utf-8"},
                json={"userName": self._username, "password": password_md5},
                ssl=False,
            ) as response:
                result = await response.json()

                if result.get("error_msg") != "Success":
                    error_msg = result.get("error_msg", "Unknown error")
                    _LOGGER.error("Login failed: %s", error_msg)
                    raise HiTempAuthError(f"Login failed: {error_msg}")

                obj_result = result.get("objectResult", {})
                self._token = obj_result.get("x-token")
                self._user_id = obj_result.get("userId") or obj_result.get("user_id")

                if not self._token:
                    raise HiTempAuthError("No token in response")

                _LOGGER.debug("Login successful, user_id: %s", self._user_id)
                return self._token

        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error during login: %s", err)
            raise HiTempConnectionError(f"Connection error: {err}") from err

    async def get_devices(self) -> list[dict[str, Any]]:
        """Get list of devices."""
        if not self._token or not self._user_id:
            await self.login()

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-token": self._token,
        }

        try:
            async with self._session.post(
                f"{BASE_URL}{API_DEVICE_LIST}",
                headers=headers,
                json={
                    "productIds": [PRODUCT_ID],
                    "toUser": self._user_id,
                    "pageIndex": 1,
                    "pageSize": 999,
                },
                ssl=False,
            ) as response:
                result = await response.json()

                if result.get("error_msg") != "Success":
                    error_msg = result.get("error_msg", "Unknown error")
                    if "token" in error_msg.lower() or "auth" in error_msg.lower():
                        self._token = None
                        raise HiTempAuthError(f"Auth error: {error_msg}")
                    raise HiTempConnectionError(f"API error: {error_msg}")

                devices = result.get("objectResult", [])
                _LOGGER.debug("Found %d devices", len(devices))
                return devices

        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error getting devices: %s", err)
            raise HiTempConnectionError(f"Connection error: {err}") from err

    async def read_params(
        self, device_code: str, codes: list[str]
    ) -> dict[str, dict[str, Any]]:
        """Read parameters from device.

        Returns dict mapping code -> {value, rangeStart, rangeEnd}
        """
        if not self._token:
            await self.login()

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-token": self._token,
        }

        try:
            async with self._session.post(
                f"{BASE_URL}{API_GET_DATA}",
                headers=headers,
                json={
                    "deviceCode": device_code,
                    "protocalCodes": codes,  # Note: API has typo "protocalCodes"
                },
                ssl=False,
            ) as response:
                result = await response.json()

                if result.get("error_msg") != "Success":
                    error_msg = result.get("error_msg", "Unknown error")
                    if "token" in error_msg.lower() or "auth" in error_msg.lower():
                        self._token = None
                        raise HiTempAuthError(f"Auth error: {error_msg}")
                    raise HiTempConnectionError(f"API error: {error_msg}")

                params = {}
                for item in result.get("objectResult", []):
                    code = item.get("code")
                    if code:
                        params[code] = {
                            "value": item.get("value"),
                            "rangeStart": item.get("rangeStart"),
                            "rangeEnd": item.get("rangeEnd"),
                        }

                return params

        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error reading params: %s", err)
            raise HiTempConnectionError(f"Connection error: {err}") from err

    async def write_param(
        self, device_code: str, code: str, value: int | float | str
    ) -> bool:
        """Write a parameter to device."""
        if not self._token:
            await self.login()

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-token": self._token,
        }

        # Convert value to appropriate type
        if isinstance(value, str):
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass  # Keep as string

        try:
            async with self._session.post(
                f"{BASE_URL}{API_CONTROL}",
                headers=headers,
                json={
                    "param": [
                        {
                            "deviceCode": device_code,
                            "protocolCode": code,
                            "value": value,
                        }
                    ]
                },
                ssl=False,
            ) as response:
                result = await response.json()

                if result.get("error_msg") != "Success":
                    error_msg = result.get("error_msg", "Unknown error")
                    if "token" in error_msg.lower() or "auth" in error_msg.lower():
                        self._token = None
                        raise HiTempAuthError(f"Auth error: {error_msg}")
                    _LOGGER.error("Write param failed: %s", error_msg)
                    return False

                _LOGGER.debug("Write param %s=%s successful", code, value)
                return True

        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error writing param: %s", err)
            raise HiTempConnectionError(f"Connection error: {err}") from err
