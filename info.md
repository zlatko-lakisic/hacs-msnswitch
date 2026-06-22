---
version: "1.0.0"
---
<p align="center">
  <img src="https://raw.githubusercontent.com/zlatko-lakisic/hacs-msnswitch/main/images/icon.png" alt="MSNSwitch" width="96">
</p>

# MSNSwitch

Home Assistant integration for **Proxicast MSNSwitch** / **MSNSwitch2** power switches (UIS-622, UIS-722).

- Control two AC outlets and UIS auto-reset
- Read ping checker health (response time, packet loss, timeouts)
- One config entry per device (IP + web UI credentials)

Requires the Home Assistant host IP on each unit's **System → API Whitelist**.
