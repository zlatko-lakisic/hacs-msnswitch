"""Data update coordinator for MSNSwitch."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MSNSwitchApi, MSNSwitchAuthError, MSNSwitchConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MSNSwitchCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll MSNSwitch status API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api: MSNSwitchApi,
        config_entry: ConfigEntry,
    ) -> None:
        self.api = api
        self.config_entry = config_entry
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{api.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.get_status()
        except MSNSwitchAuthError as err:
            raise UpdateFailed(str(err)) from err
        except MSNSwitchConnectionError as err:
            raise UpdateFailed(str(err)) from err
