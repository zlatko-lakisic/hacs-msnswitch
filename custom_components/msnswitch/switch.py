"""Switch platform for MSNSwitch outlets and UIS."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MSNSwitchConnectionError
from .const import DOMAIN
from .coordinator import MSNSwitchCoordinator
from .entity import MSNSwitchEntity, outlet_data, outlet_display_name, uis_enabled

_LOGGER = logging.getLogger(__name__)

OUTLET_TARGETS = ("outlet1", "outlet2")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MSNSwitch switches."""
    coordinator: MSNSwitchCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SwitchEntity] = [
        MSNSwitchOutletSwitch(coordinator, index, target)
        for index, target in enumerate(OUTLET_TARGETS)
    ]
    entities.append(MSNSwitchUISSwitch(coordinator))
    async_add_entities(entities)


class MSNSwitchOutletSwitch(MSNSwitchEntity, SwitchEntity):
    """Switch for a single MSNSwitch AC outlet."""

    def __init__(
        self,
        coordinator: MSNSwitchCoordinator,
        outlet_index: int,
        target: str,
    ) -> None:
        super().__init__(coordinator, f"{target}_switch")
        self._outlet_index = outlet_index
        self._target = target

    @property
    def name(self) -> str:
        return outlet_display_name(self.coordinator.data or {}, self._outlet_index)

    @property
    def is_on(self) -> bool | None:
        outlet = outlet_data(self.coordinator.data or {}, self._outlet_index)
        if outlet is None:
            return None
        return bool(outlet.get("status", False))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        outlet = outlet_data(self.coordinator.data or {}, self._outlet_index)
        if outlet is None:
            return {"outlet_index": self._outlet_index + 1, "api_target": self._target}
        return {
            "outlet_index": self._outlet_index + 1,
            "api_target": self._target,
            "configured_name": outlet.get("name"),
            "reset_only": outlet.get("reset_only"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_control("on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_control("off")

    async def _async_control(self, action: str) -> None:
        try:
            await self.coordinator.api.control(self._target, action)
        except MSNSwitchConnectionError as err:
            _LOGGER.error("Outlet control failed: %s", err)
            raise
        await self.coordinator.async_request_refresh()


class MSNSwitchUISSwitch(MSNSwitchEntity, SwitchEntity):
    """Switch to enable or disable UIS auto-reset."""

    _attr_icon = "mdi:restart-alert"

    def __init__(self, coordinator: MSNSwitchCoordinator) -> None:
        super().__init__(coordinator, "uis_switch", "UIS auto-reset")

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return uis_enabled(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_control("on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_control("off")

    async def _async_control(self, action: str) -> None:
        try:
            await self.coordinator.api.control_uis(action)
        except MSNSwitchConnectionError as err:
            _LOGGER.error("UIS control failed: %s", err)
            raise
        await self.coordinator.async_request_refresh()
