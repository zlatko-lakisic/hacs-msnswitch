"""MSNSwitch HTTP API client (UIS-622 / UIS-722 / MSNSwitch2)."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

API_STATUS = "/api/status"
API_CONTROL = "/api/control"

ACCESS_DENIED = "Access Denied"


class MSNSwitchAuthError(Exception):
    """Invalid credentials or API access denied."""


class MSNSwitchConnectionError(Exception):
    """Unable to reach the device."""


class MSNSwitchApi:
    """Async client for MSNSwitch REST API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._host = host.strip()
        self._username = username
        self._password = password
        self._session = session
        self._base_url = f"http://{self._host}"

    @property
    def host(self) -> str:
        return self._host

    def _auth_body(self) -> str:
        from urllib.parse import urlencode

        return urlencode(
            {"user": self._username, "password": self._password},
            safe="",
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = self._auth_body()

        try:
            async with self._session.request(
                method,
                url,
                params=params,
                data=body,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                text = await response.text()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise MSNSwitchConnectionError(
                f"Could not reach MSNSwitch at {self._host}: {err}"
            ) from err

        if ACCESS_DENIED in text:
            raise MSNSwitchAuthError(
                "API access denied. Add the Home Assistant host IP to "
                "System → API Whitelist on the MSNSwitch web UI."
            )

        if response.status >= 400:
            raise MSNSwitchConnectionError(
                f"MSNSwitch returned HTTP {response.status}: {text[:200]}"
            )

        if not text or text.lstrip().startswith("<"):
            raise MSNSwitchConnectionError(
                f"Unexpected response from MSNSwitch: {text[:200]}"
            )

        try:
            import json

            data = json.loads(text)
        except ValueError as err:
            raise MSNSwitchConnectionError(
                f"Invalid JSON from MSNSwitch: {text[:200]}"
            ) from err

        if not isinstance(data, dict):
            raise MSNSwitchConnectionError("MSNSwitch status payload was not an object")

        return data

    async def get_status(self) -> dict[str, Any]:
        """Fetch device status including outlets and connection checkers."""
        return await self._request("POST", API_STATUS)

    async def control(self, target: str, action: str) -> dict[str, Any]:
        """Control an outlet or UIS (target: outlet1|outlet2|outlet_all|uis)."""
        return await self._request(
            "POST",
            API_CONTROL,
            params={"target": target, "action": action},
        )

    async def control_uis(self, action: str) -> dict[str, Any]:
        """Enable or disable UIS; tries 'uis' then legacy 'us' target."""
        last_err: Exception | None = None
        for target in UIS_TARGETS:
            try:
                return await self.control(target, action)
            except MSNSwitchConnectionError as err:
                last_err = err
                _LOGGER.debug("UIS control via target=%s failed: %s", target, err)
        if last_err:
            raise last_err
        raise MSNSwitchConnectionError("UIS control failed")
