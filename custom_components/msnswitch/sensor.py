"""Sensor platform for MSNSwitch connection checkers."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_ASSIGN, ATTR_HOST, ATTR_IP, ATTR_TIMEOUT, DOMAIN
from .coordinator import MSNSwitchCoordinator
from .entity import (
    MSNSwitchEntity,
    active_connections,
    checker_display_name,
)

CHECKER_TARGETS = ("outlet1", "outlet2")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up checker sensors from the latest status payload."""
    coordinator: MSNSwitchCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(_build_checker_entities(coordinator))


def _build_checker_entities(
    coordinator: MSNSwitchCoordinator,
) -> list[SensorEntity]:
    entities: list[SensorEntity] = []
    status = coordinator.data or {}
    for slot_index, checker in active_connections(status):
        slug = _checker_slug(checker, slot_index)
        display = checker_display_name(checker, slot_index)
        entities.append(
            MSNSwitchResponseSensor(coordinator, checker, slug, slot_index, display)
        )
        entities.append(
            MSNSwitchPacketLossSensor(coordinator, checker, slug, slot_index, display)
        )
        entities.append(
            MSNSwitchTimeoutSensor(coordinator, checker, slug, slot_index, display)
        )
    return entities


def _checker_slug(checker: dict[str, Any], slot_index: int) -> str:
    label = checker_display_name(checker, slot_index)
    slug = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    return f"slot{slot_index}_{slug}" if slug else f"slot{slot_index}"


class MSNSwitchCheckerSensor(MSNSwitchEntity, SensorEntity):
    """Base sensor for one connection checker."""

    def __init__(
        self,
        coordinator: MSNSwitchCoordinator,
        checker: dict[str, Any],
        slug: str,
        slot_index: int,
        display_name: str,
        suffix: str,
        sensor_name: str,
    ) -> None:
        super().__init__(coordinator, f"checker_{slug}_{suffix}")
        self._slot_index = slot_index
        self._display_name = display_name

    def _current_checker(self) -> dict[str, Any] | None:
        for index, checker in active_connections(self.coordinator.data or {}):
            if index == self._slot_index:
                return checker
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        checker = self._current_checker()
        if checker is None:
            return {"slot_index": self._slot_index + 1}
        assign = str(checker.get("assign") or "").strip()
        outlet_target = None
        if assign == "OUTLET1":
            outlet_target = CHECKER_TARGETS[0]
        elif assign == "OUTLET2":
            outlet_target = CHECKER_TARGETS[1]
        elif assign == "BOTH":
            outlet_target = "outlet_all"
        return {
            "slot_index": self._slot_index + 1,
            ATTR_ASSIGN: assign or "NONE",
            ATTR_HOST: checker.get("host"),
            ATTR_IP: checker.get("ip"),
            "label": checker.get("label"),
            "checker_name": checker_display_name(checker, self._slot_index),
            "outlet_target": outlet_target,
        }


class MSNSwitchResponseSensor(MSNSwitchCheckerSensor):
    """Response time for a connection checker."""

    _attr_native_unit_of_measurement = UnitOfTime.MILLISECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:timer-outline"

    def __init__(
        self,
        coordinator: MSNSwitchCoordinator,
        checker: dict[str, Any],
        slug: str,
        slot_index: int,
        display_name: str,
    ) -> None:
        super().__init__(
            coordinator,
            checker,
            slug,
            slot_index,
            display_name,
            "response",
            f"{display_name} response time",
        )
        self._attr_name = f"{display_name} response time"

    @property
    def native_value(self) -> int | None:
        checker = self._current_checker()
        if checker is None:
            return None
        resp = checker.get("resp")
        try:
            return int(resp) if resp is not None else None
        except (TypeError, ValueError):
            return None


class MSNSwitchPacketLossSensor(MSNSwitchCheckerSensor):
    """Packet loss percentage for a connection checker."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:signal-variant"

    def __init__(
        self,
        coordinator: MSNSwitchCoordinator,
        checker: dict[str, Any],
        slug: str,
        slot_index: int,
        display_name: str,
    ) -> None:
        super().__init__(
            coordinator,
            checker,
            slug,
            slot_index,
            display_name,
            "lost",
            f"{display_name} packet loss",
        )
        self._attr_name = f"{display_name} packet loss"

    @property
    def native_value(self) -> int | None:
        checker = self._current_checker()
        if checker is None:
            return None
        lost = checker.get("lost")
        try:
            return int(lost) if lost is not None else None
        except (TypeError, ValueError):
            return None


class MSNSwitchTimeoutSensor(MSNSwitchCheckerSensor):
    """Consecutive timeout count for a connection checker."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:alert-circle-outline"

    def __init__(
        self,
        coordinator: MSNSwitchCoordinator,
        checker: dict[str, Any],
        slug: str,
        slot_index: int,
        display_name: str,
    ) -> None:
        super().__init__(
            coordinator,
            checker,
            slug,
            slot_index,
            display_name,
            "timeout",
            f"{display_name} timeouts",
        )
        self._attr_name = f"{display_name} timeouts"

    @property
    def native_value(self) -> int | None:
        checker = self._current_checker()
        if checker is None:
            return None
        timeout = checker.get("timeout")
        try:
            return int(timeout) if timeout is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs = super().extra_state_attributes
        attrs[ATTR_TIMEOUT] = self.native_value
        return attrs
