"""Test UIS-622 malformed JSON repair."""

import json
import re

_MALFORMED_OBJECT_BOUNDARY = re.compile(r"\}\s*\{")


def parse_msnswitch_json(text: str) -> dict:
    payload = text.strip()
    try:
        data = json.loads(payload)
    except ValueError:
        repaired = _MALFORMED_OBJECT_BOUNDARY.sub("},{", payload)
        data = json.loads(repaired)
    return data


UIS_622 = (
    '{"connections": [{"assign":"OUTLET1","label":"Router","host":"10.0.10.1",'
    '"ip":"10.0.10.1","resp":1,"timeout":2,"lost":0}'
    '{"assign":"OUTLET1","label":"Google DNS","host":"8.8.8.8","ip":"8.8.8.8",'
    '"resp":5,"timeout":3,"lost":0}'
    '{"assign":"OUTLET2","label":"Google DNS","host":"8.8.8.8","ip":"8.8.8.8",'
    '"resp":5,"timeout":4,"lost":0}'
    '{"assign":"NONE","label":"","host":"","ip":"null","resp":0,"timeout":0,"lost":0}'
    '{"assign":"NONE","label":"","host":"10.0.10.1","ip":"10.0.10.1","resp":1,'
    '"timeout":3,"lost":0}'
    '{"assign":"NONE","label":"","host":"","ip":"null","resp":0,"timeout":0,"lost":0}'
    '{"assign":"NONE","label":"","host":"","ip":"null","resp":0,"timeout":0,"lost":0}],'
    '"status":{"outlet":[{"name":"Router","status":true,"reset_only":false}'
    '{"name":"Modem","status":true,"reset_only":false}],"uis":true}}'
)


def test_uis_622() -> None:
    data = parse_msnswitch_json(UIS_622)
    assert len(data["connections"]) == 7
    assert data["status"]["outlet"][1]["name"] == "Modem"
    print("ok", data["status"]["outlet"])


if __name__ == "__main__":
    test_uis_622()
