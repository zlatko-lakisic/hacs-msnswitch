"""Tests for UIS-622 malformed JSON repair."""

import json
import re
from pathlib import Path

_MALFORMED_OBJECT_BOUNDARY = re.compile(r"\}\s*\{")


def _repair_msnswitch_payload(text: str) -> str:
    payload = text.strip()
    if _MALFORMED_OBJECT_BOUNDARY.search(payload):
        payload = _MALFORMED_OBJECT_BOUNDARY.sub("},{", payload)
    open_braces = payload.count("{")
    close_braces = payload.count("}")
    if open_braces > close_braces:
        payload += "}" * (open_braces - close_braces)
    return payload


def parse_msnswitch_json(text: str) -> dict:
    return json.loads(_repair_msnswitch_payload(text))


UIS_622_SAMPLE = (
    [line for line in Path(__file__).with_name("uis622_sample.json").read_text().splitlines() if line.startswith("{")][0]
)


def test_uis_622_live_sample() -> None:
    data = parse_msnswitch_json(UIS_622_SAMPLE)
    assert len(data["connections"]) == 7
    assert [o["name"] for o in data["status"]["outlet"]] == ["Router", "Modem"]


def test_valid_json_unchanged() -> None:
    valid = json.dumps(
        {
            "connections": [],
            "status": {"outlet": [], "uis": False},
        }
    )
    data = parse_msnswitch_json(valid)
    assert data["status"]["uis"] is False


if __name__ == "__main__":
    test_uis_622_live_sample()
    test_valid_json_unchanged()
    print("ok")
