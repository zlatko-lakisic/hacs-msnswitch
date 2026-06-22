"""Binary sensor platform for MSNSwitch checker health."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MSNSwitchCoordinator
from .entity import (
    MSNSwitchEntity,
    active_connections,
    checker_display_name,
    checker_is_healthy,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up checker connectivity binary sensors."""
    coordinator: MSNSwitchCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = []
    for slot_index, checker in active_connections(coordinator.data or {}):
        slug = _checker_slug(checker, slot_index)
        display = checker_display_name(checker, slot_index)
        entities.append(
            MSNSwitchCheckerBinarySensor(coordinator, checker, slug, slot_index, display)
        )
    async_add_entities(entities)


def _checker_slug(checker: dict[str, Any], slot_index: int) -> str:
    label = checker_display_name(checker, slot_index)
    slug = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    return f"slot{slot_index}_{slug}" if slug else f"slot{slot_index}"


class MSNSwitchCheckerBinarySensor(MSNSwitchEntity, BinarySensorEntity):
    """Whether a UIS checker target is healthy (no timeouts / packet loss)."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: MSNSwitchCoordinator,
        checker: dict[str, Any],
        slug: str,
        slot_index: int,
        display_name: str,
    ) -> None:
        super().__init__(coordinator, f"checker_{slug}_healthy")
        self._slot_index = slot_index
        self._attr_name = display_name

    def _current_checker(self) -> dict[str, Any] | None:
        for index, checker in active_connections(self.coordinator.data or {}):
            if index == self._slot_index:
                return checker
        return None

    @property
    def is_on(self) -> bool | None:
        checker = self._current_checker()
        if checker is None:
            return None
        return checker_is_healthy(checker)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        checker = self._current_checker()
        if checker is None:
            return {"slot_index": self._slot_index + 1}
        return {
            "slot_index": self._slot_index + 1,
            "assign": checker.get("assign"),
            "host": checker.get("host"),
            "ip": checker.get("ip"),
            "label": checker.get("label"),
            "response_ms": checker.get("resp"),
            "timeout_count": checker.get("timeout"),
            "packet_loss_pct": checker.get("lost"),
        }
