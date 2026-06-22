"""Config flow for MSNSwitch."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MSNSwitchApi, MSNSwitchAuthError, MSNSwitchConnectionError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class MSNSwitchConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MSNSwitch."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add one MSNSwitch by IP, username, and password."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            await self.async_set_unique_id(host.lower())
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = MSNSwitchApi(
                host=host,
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
                session=session,
            )

            try:
                await api.get_status()
            except MSNSwitchAuthError as err:
                _LOGGER.warning("MSNSwitch auth failed for %s: %s", host, err)
                errors["base"] = "invalid_auth"
            except MSNSwitchConnectionError as err:
                _LOGGER.warning("MSNSwitch connect failed for %s: %s", host, err)
                errors["base"] = "cannot_connect"
            except aiohttp.ClientError as err:
                _LOGGER.warning("MSNSwitch HTTP error for %s: %s", host, err)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"MSNSwitch {host}",
                    data={
                        CONF_HOST: host,
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
