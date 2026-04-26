# Anfisa VPN

Windows desktop prototype for finding, filtering, and opening public proxy configs in Hiddify.

## What it does

- downloads public `VLESS`, `VMess`, `Trojan`, and `SS` config pools
- runs a fast prefilter before a heavier `HiddifyCli`-based runtime check
- separates results into:
  - `Fresh`
  - `History`
  - `Recommended`
- supports opening configs directly in Hiddify with Anfisa-branded naming
- provides `Saved` and `Blocked` local lists

## Current focus

The main unfinished area is `Smart Test` stability and runtime speed. The UI and Hiddify import flow are already much closer to product quality than the checker itself.

## Project structure

- `project.godot` — Godot project entry
- `scenes/` — Godot scenes
- `scripts/` — UI and app logic
- `tools/` — Python pipeline and Hiddify helpers
- `assets/` — local assets and branding
- `webui/` — bundled web assets used by the local workflow

## Run locally

Use either:

- `RUN_ANFISA_VPN.cmd`
- `run_anfisa_vpn.ps1`

Or open `project.godot` in Godot and run it from the editor.

## Notes

- This repo intentionally does **not** commit generated runtime results, raw downloaded proxy pools, or local user state.
- The current implementation is optimized around honest reporting and recovery-first behavior rather than pretending weak public pools are reliable.

## Source inspiration

Primary upstream source that inspired the proxy aggregation side:

- [kort0881/vpn-vless-configs-russia](https://github.com/kort0881/vpn-vless-configs-russia)
