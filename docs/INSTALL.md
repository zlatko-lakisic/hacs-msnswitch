# Install MSNSwitch in Home Assistant

## Before you start

On **each** MSNSwitch web UI:

1. Open `http://<msnswitch-ip>/` and log in.
2. Go to **System → API Whitelist**.
3. Add your **Home Assistant server IP** (e.g. `10.0.10.6`).
4. Save.

Without this, the integration will show **invalid auth / Access Denied**.

---

## Option A — Install now (manual copy)

Best for testing before the repo is on GitHub or without HACS.

### From this repo (Windows + NAS share)

```powershell
cd d:\Projects\hacs-msnswitch
powershell -ExecutionPolicy Bypass -File scripts\install-to-ha.ps1
```

Default target: `\\192.168.89.25\config`. Override with `-ConfigRoot`.

### Manual copy

Copy the folder:

`custom_components/msnswitch`

to:

`<HA config>/custom_components/msnswitch`

### After copy

1. **Restart Home Assistant** (Settings → System → Restart).
2. **Settings → Devices & services → Add integration**
3. Search **MSNSwitch**
4. Enter **Host** (IP), **Username**, **Password**
5. Repeat for each physical MSNSwitch (one config entry per device).

---

## Option B — HACS (custom repository)

Use this when the repo is on GitHub: `https://github.com/zlatko-lakisic/hacs-msnswitch`

1. Install [HACS](https://hacs.xyz/docs/setup/download) if needed.
2. HACS → **⋮** → **Custom repositories**
3. Repository URL: `https://github.com/zlatko-lakisic/hacs-msnswitch`
4. Category: **Integration** → **Add**
5. HACS → **Integrations** → **Explore & download** → search **MSNSwitch** → **Download**
6. **Restart Home Assistant**
7. Add integration (same as Option A, steps 2–5)

### Updates in HACS

HACS → Integrations → MSNSwitch → **Update** (when a new [GitHub Release](RELEASE.md) is published).

---

## Option C — HACS default store (future)

To list in the public HACS store, follow [HACS publish requirements](https://hacs.xyz/docs/publish/integration/) (brand assets, etc.) and open a PR to the HACS default repository.

---

## Verify it works

After setup you should see per device:

- Switches named from the API (e.g. **Traefik**, **NAS1**)
- **UIS auto-reset** switch
- **Reset** buttons
- Checker **binary_sensor** + **sensor** entities for each configured ping target

Test the API from a whitelisted machine:

```bash
curl --http1.1 -s --url 'http://10.0.10.252/api/status' \
  --data 'user=YOUR_USER&password=YOUR_PASSWORD'
```
