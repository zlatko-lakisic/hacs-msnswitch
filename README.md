# MSNSwitch — Home Assistant integration (HACS)

[![Validate](https://github.com/zlatko-lakisic/hacs-msnswitch/actions/workflows/validate.yml/badge.svg)](https://github.com/zlatko-lakisic/hacs-msnswitch/actions/workflows/validate.yml)

Control **Proxicast MSNSwitch** / **MSNSwitch2** devices (UIS-622, UIS-722) from Home Assistant.

## Features

- **One config entry per device** — IP, username, password
- **Named outlets** from the API (e.g. Traefik, NAS1)
- **UIS auto-reset** switch
- **Reset buttons** per outlet and all outlets
- **Checker health** — connectivity binary sensors plus response time, packet loss, timeouts
- Polls the local HTTP API every 30 seconds

## Requirements

- Home Assistant **2023.8** or newer
- MSNSwitch reachable on your LAN
- Home Assistant IP on each unit’s **System → API Whitelist**

## Installation

See **[docs/INSTALL.md](docs/INSTALL.md)** for full steps.

**Quick install on your NAS HA config:**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-to-ha.ps1
```

Then restart HA and add **MSNSwitch** under Settings → Devices & services.

**HACS (custom repo):** add `https://github.com/zlatko-lakisic/hacs-msnswitch` as an Integration repository, install, restart.

## Releasing new versions

See **[docs/RELEASE.md](docs/RELEASE.md)**.

```bash
gh release create v1.0.1 --title "v1.0.1" --notes "Changelog."
```

## Repository layout

```
hacs-msnswitch/
├── .github/workflows/       # HACS validate + release zip
├── custom_components/
│   └── msnswitch/           # Integration (required HACS path)
├── docs/
│   ├── INSTALL.md
│   └── RELEASE.md
├── scripts/
│   └── install-to-ha.ps1    # Copy integration to HA config share
├── hacs.json                # HACS metadata
├── info.md                  # HACS info panel
├── LICENSE
└── README.md
```

## API

- `POST /api/status` — outlets and connection checkers
- `POST /api/control?target=…&action=…` — outlets (`outlet1`, `outlet2`, `outlet_all`) or UIS (`uis` / legacy `us`)

## License

MIT — see [LICENSE](LICENSE).
