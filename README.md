# ECO-WORTHY BW19 for Home Assistant

Monitor the ECO-WORTHY BW19 600 W / 12 V pure sine wave inverter-charger over Bluetooth. This unofficial integration exposes battery voltage, battery current, and AC voltage as sensors. It requests status once a minute and disconnects after each reading. It does not expose settings or controls.

The initial release was tested with Home Assistant Core 2026.11.1 and an ESPHome Bluetooth proxy. The inverter must be within reach of a connectable Bluetooth adapter or an ESPHome proxy with active connections enabled. Supported units advertise a Bluetooth name starting with `ECO-WORTHY 19_`.

## Install with HACS

1. In **HACS → ⋮ → Custom repositories**, add `https://github.com/nickwilkie/ecoworthy-bw19-ha` and select **Integration** as the type.
2. Download **ECO-WORTHY BW19** in HACS, then restart Home Assistant.
3. In **Settings → Devices & services**, accept the discovered inverter. If it isn't listed, select **Add integration → ECO-WORTHY BW19** and enter the inverter's Bluetooth address.

If this integration is already installed manually, download it into the same location through HACS and restart. Leave the existing Home Assistant device entry in place to retain its entity IDs and history.

For a manual install, copy `custom_components/ecoworthy_bw19` from a release into `/config/custom_components/`, restart Home Assistant, and follow step 3.

If setup keeps retrying, move the Bluetooth adapter or proxy closer to the inverter and close the ECO-WORTHY app while testing. The app may be holding the connection.

## Publish an update

Make changes in `custom_components/ecoworthy_bw19`, then bump `version` in its `manifest.json`. Publish a GitHub Release with a matching version tag (for example, `v0.1.1` for manifest version `0.1.1`). HACS will offer that release as an update. Install it in HACS and restart Home Assistant when prompted.
