# MSNSwitch — Home Assistant integration (HACS)

Control **Proxicast MSNSwitch** / **MSNSwitch2** devices (UIS-622, UIS-722, UIS-722b, UIS-722T) from Home Assistant.

## Features

- **One config entry per device** — add each MSNSwitch by IP, username, and password
- **Outlet switches** — turn outlet 1 and outlet 2 on/off
- **UIS switch** — enable or disable auto-reset (UIS)
- **Reset buttons** — power-cycle outlet 1, outlet 2, or both
- **Checker sensors** — response time, packet loss %, and timeout count per ping/HTTP target
- Polls the local HTTP API every 30 seconds

## Requirements

1. MSNSwitch on the same network as Home Assistant (or reachable by IP)
2. **API Whitelist** on the device: **System → API Whitelist** — add Home Assistant’s IP (e.g. `10.0.10.6`)
3. Web UI username and password (not cloud-only credentials)

## Installation (HACS)

1. Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) in HACS (category: **Integration**).
2. Install **MSNSwitch** from HACS.
3. Restart Home Assistant.
4. **Settings → Devices & services → Add integration → MSNSwitch**
5. Enter **host**, **username**, and **password**.
6. Repeat for each physical MSNSwitch.

## Manual install

Copy `custom_components/msnswitch` into your Home Assistant `config/custom_components/` folder and restart.

## Entities per device

For a status payload like:

```json
{
  "connections": [
    {"assign":"OUTLET1","label":"Traefik","host":"10.0.10.6","resp":1,"timeout":0,"lost":0},
    {"assign":"OUTLET2","label":"NAS1","host":"10.0.10.3","resp":1,"timeout":0,"lost":0}
  ],
  "status": {
    "outlet": [
      {"name":"Traefik","status":true,"reset_only":false},
      {"name":"NAS1","status":true,"reset_only":false}
    ],
    "uis": true
  }
}
```

| Entity | Type | Example name |
|--------|------|----------------|
| Traefik / NAS1 | `switch` | Outlet on/off (names from API) |
| UIS auto-reset | `switch` | UIS watchdog on/off |
| Reset Traefik / NAS1 | `button` | Power-cycle named outlet |
| Reset all outlets | `button` | Power-cycle both |
| Traefik / NAS1 / … | `binary_sensor` | Checker healthy (connectivity) |
| Per checker | `sensor` | Response time (ms), packet loss (%), timeouts |

Empty checker slots (`assign: NONE`, no host/label) are skipped automatically.

## API

Uses the MSNSwitch2 REST API:

- `POST /api/status` — read outlets and connection checkers
- `POST /api/control?target=…&action=…` — control outlets or UIS

UIS control tries target `uis`, then legacy `us` for older firmware.

## Development

Repository layout:

```
custom_components/msnswitch/
hacs.json
README.md
```

## License

MIT
