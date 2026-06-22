"""Button platform for MSNSwitch outlet reset."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MSNSwitchConnectionError
from .const import DOMAIN
from .coordinator import MSNSwitchCoordinator
from .entity import MSNSwitchEntity, outlet_display_name

_LOGGER = logging.getLogger(__name__)

OUTLET_TARGETS = ("outlet1", "outlet2")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MSNSwitch reset buttons."""
    coordinator: MSNSwitchCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[ButtonEntity] = [
        MSNSwitchResetButton(coordinator, index, target)
        for index, target in enumerate(OUTLET_TARGETS)
    ]
    entities.append(MSNSwitchResetAllButton(coordinator))
    async_add_entities(entities)


class MSNSwitchResetButton(MSNSwitchEntity, ButtonEntity):
    """Power-cycle one outlet (reset)."""

    _attr_icon = "mdi:power-cycle"

    def __init__(
        self,
        coordinator: MSNSwitchCoordinator,
        outlet_index: int,
        target: str,
    ) -> None:
        super().__init__(coordinator, f"{target}_reset")
        self._outlet_index = outlet_index
        self._target = target

    @property
    def name(self) -> str:
        label = outlet_display_name(self.coordinator.data or {}, self._outlet_index)
        return f"Reset {label}"

    async def async_press(self) -> None:
        try:
            await self.coordinator.api.control(self._target, "reset")
        except MSNSwitchConnectionError as err:
            _LOGGER.error("Reset failed for %s: %s", self._target, err)
            raise
        await self.coordinator.async_request_refresh()


class MSNSwitchResetAllButton(MSNSwitchEntity, ButtonEntity):
    """Power-cycle both outlets."""

    _attr_icon = "mdi:power-cycle"

    def __init__(self, coordinator: MSNSwitchCoordinator) -> None:
        super().__init__(coordinator, "outlet_all_reset", "Reset all outlets")

    async def async_press(self) -> None:
        try:
            await self.coordinator.api.control("outlet_all", "reset")
        except MSNSwitchConnectionError as err:
            _LOGGER.error("Reset all failed: %s", err)
            raise
        await self.coordinator.async_request_refresh()
