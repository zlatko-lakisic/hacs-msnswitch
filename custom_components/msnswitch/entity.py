"""Shared helpers for MSNSwitch entities."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MSNSwitchCoordinator


def device_info(coordinator: MSNSwitchCoordinator) -> DeviceInfo:
    """Return device registry entry for one MSNSwitch."""
    host = coordinator.api.host
    return DeviceInfo(
        identifiers={(DOMAIN, host)},
        name=f"MSNSwitch {host}",
        manufacturer="Proxicast / Megatec",
        model="MSNSwitch (UIS-622 / UIS-722)",
        configuration_url=f"http://{host}/",
    )


def outlets(status: dict[str, Any]) -> list[dict[str, Any]]:
    """Return configured outlet dicts from status payload."""
    raw = status.get("status", {}).get("outlet", [])
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def outlet_data(status: dict[str, Any], index: int) -> dict[str, Any] | None:
    """Return outlet dict at index (0 or 1) from status payload."""
    items = outlets(status)
    if index >= len(items):
        return None
    return items[index]


def outlet_display_name(status: dict[str, Any], index: int) -> str:
    """Human name for an outlet (e.g. Traefik, NAS1)."""
    outlet = outlet_data(status, index)
    if outlet is None:
        return f"Outlet {index + 1}"
    name = str(outlet.get("name") or "").strip()
    return name or f"Outlet {index + 1}"


def uis_enabled(status: dict[str, Any]) -> bool:
    """Return whether UIS auto-reset is enabled."""
    uis = status.get("status", {}).get("uis")
    if isinstance(uis, bool):
        return uis
    if isinstance(uis, dict):
        return bool(uis.get("status", False))
    return False


def connections(status: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all connection checker slots from status payload."""
    raw = status.get("connections", [])
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _clean_field(value: Any) -> str:
    text = str(value or "").strip()
    if text.lower() in ("null", "none", "unknown", "unavailable"):
        return ""
    return text


def is_checker_active(checker: dict[str, Any]) -> bool:
    """True when a checker slot is configured (skip empty UIS slots)."""
    host = _clean_field(checker.get("host"))
    label = _clean_field(checker.get("label"))
    ip = _clean_field(checker.get("ip"))
    assign = _clean_field(checker.get("assign"))
    if host or label:
        return True
    if ip:
        return True
    return assign not in ("", "NONE")


def active_connections(status: dict[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    """Return (slot_index, checker) for configured checker slots only."""
    return [
        (index, checker)
        for index, checker in enumerate(connections(status))
        if is_checker_active(checker)
    ]


def checker_display_name(checker: dict[str, Any], slot_index: int) -> str:
    """Display name for a checker (label, host, assign, or slot)."""
    label = _clean_field(checker.get("label"))
    host = _clean_field(checker.get("host"))
    ip = _clean_field(checker.get("ip"))
    assign = _clean_field(checker.get("assign"))

    if label:
        return label
    if host:
        return host
    if ip:
        return ip
    if assign and assign != "NONE":
        return assign
    return f"Checker slot {slot_index + 1}"


def checker_is_healthy(checker: dict[str, Any]) -> bool:
    """True when checker reports no timeouts and no packet loss."""
    try:
        timeout = int(checker.get("timeout") or 0)
        lost = int(checker.get("lost") or 0)
    except (TypeError, ValueError):
        return False
    return timeout == 0 and lost == 0


class MSNSwitchEntity(CoordinatorEntity[MSNSwitchCoordinator]):
    """Base entity for MSNSwitch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MSNSwitchCoordinator,
        entity_suffix: str,
        name: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        host = coordinator.api.host
        self._attr_unique_id = f"{host}_{entity_suffix}"
        if name is not None:
            self._attr_name = name
        self._attr_device_info = device_info(coordinator)
