"""MSNSwitch HTTP API client (UIS-622 / UIS-722 / MSNSwitch2)."""

from __future__ import annotations

import json
import logging
import re
from typing import Any
from urllib.parse import urlencode

import aiohttp

from .const import UIS_TARGETS

_LOGGER = logging.getLogger(__name__)

API_STATUS = "/api/status"
API_CONTROL = "/api/control"

LOGIN_MARKERS = ("login.asp", "Access Denied", "access denied")

# UIS-622 (older firmware) omits commas between objects in arrays: {...}{...}
_MALFORMED_OBJECT_BOUNDARY = re.compile(r"\}\s*\{")


def parse_msnswitch_json(text: str) -> dict[str, Any]:
    """Parse MSNSwitch /api/status JSON, repairing known UIS-622 formatting bugs."""
    payload = text.strip()
    try:
        data = json.loads(payload)
    except ValueError:
        repaired = _MALFORMED_OBJECT_BOUNDARY.sub("},{", payload)
        try:
            data = json.loads(repaired)
        except ValueError as err:
            raise ValueError(f"Invalid JSON after repair: {payload[:200]}") from err
        _LOGGER.debug("Repaired malformed MSNSwitch JSON (missing array commas)")

    if not isinstance(data, dict):
        raise TypeError("MSNSwitch status payload was not an object")
    return data


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

    def _auth_fields(self, *, password_key: str = "password") -> dict[str, str]:
        return {"user": self._username, password_key: self._password}

    def _auth_body(self, *, password_key: str = "password") -> bytes:
        return urlencode(self._auth_fields(password_key=password_key), safe="").encode(
            "utf-8"
        )

    def _classify_response(self, text: str) -> None:
        lowered = text.lower()
        if any(marker.lower() in lowered for marker in LOGIN_MARKERS):
            raise MSNSwitchAuthError(
                "API access denied. Add the Home Assistant host IP to "
                "System → API Whitelist on the MSNSwitch web UI."
            )

    def _parse_status_text(self, text: str) -> dict[str, Any]:
        if not text or text.lstrip().startswith("<"):
            raise MSNSwitchConnectionError(
                f"Unexpected response from MSNSwitch: {text[:200]}"
            )

        try:
            return parse_msnswitch_json(text)
        except (ValueError, TypeError) as err:
            raise MSNSwitchConnectionError(
                f"Invalid JSON from MSNSwitch: {text[:200]}"
            ) from err

    async def _fetch(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        body: bytes | None = None,
    ) -> str:
        headers: dict[str, str] = {}
        if body is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            headers["Content-Length"] = str(len(body))

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

        self._classify_response(text)

        if response.status >= 400:
            raise MSNSwitchConnectionError(
                f"MSNSwitch returned HTTP {response.status}: {text[:200]}"
            )

        return text

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        password_key: str = "password",
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        body = self._auth_body(password_key=password_key)
        text = await self._fetch(method, url, params=params, body=body)
        return self._parse_status_text(text)

    async def get_status(self) -> dict[str, Any]:
        """Fetch device status including outlets and connection checkers."""
        last_err: Exception | None = None
        url = f"{self._base_url}{API_STATUS}"

        for password_key in ("password", "passwd"):
            for method, body in (
                ("POST", self._auth_body(password_key=password_key)),
                ("GET", None),
            ):
                try:
                    if method == "GET":
                        text = await self._fetch(
                            "GET",
                            url,
                            params=self._auth_fields(password_key=password_key),
                        )
                    else:
                        text = await self._fetch("POST", url, body=body)
                    return self._parse_status_text(text)
                except MSNSwitchAuthError:
                    raise
                except MSNSwitchConnectionError as err:
                    last_err = err
                    _LOGGER.debug(
                        "Status via %s %s (password_key=%s) failed: %s",
                        method,
                        API_STATUS,
                        password_key,
                        err,
                    )

        if last_err:
            raise last_err
        raise MSNSwitchConnectionError("Could not read MSNSwitch status")

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
