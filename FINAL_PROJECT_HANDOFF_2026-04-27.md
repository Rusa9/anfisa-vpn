# Anfisa VPN - Final Project Handoff (2026-04-27)

## Workspace
- Repo: `C:\Users\rysla\AnfisaVPN`
- Old seed/materials: `C:\Users\rysla\OneDrive\Рабочий стол\VPN_готово`
- Do not touch: `where-memory-stays`

## What the app is now
Windows desktop app on Godot + Python.

Main files:
- `tools/anfisa_pipeline.py`
- `scripts/anfisa_app.gd`
- `tools/hiddify_named_import.py`
- `tools/hiddify_profile_patch.py`

Purpose:
- collect public proxy configs
- filter/rank them
- validate them on this exact PC through `HiddifyCli`
- show only usable results in the app
- open/import them into `Hiddify`

## Current source strategy
Primary live:
- `https://github.com/kort0881/vpn-vless-configs-russia`
- `https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt`
- `https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/trojan.txt`
- `https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vmess.txt`
- `https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/ss.txt`
- `https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/vless_ru.txt`
- `https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/trojan_ru.txt`
- `https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/vmess_ru.txt`
- `https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/ss_ru.txt`

Trusted checked:
- `https://github.com/igareck/vpn-configs-for-russia`
- `https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/BLACK_VLESS_RUS_mobile.txt`
- `https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/BLACK_SS+All_RUS.txt`
- `https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/Vless-Reality-White-Lists-Rus-Mobile.txt`
- `https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/Vless-Reality-White-Lists-Rus-Mobile-2.txt`

Noisy expansion:
- `https://github.com/Epodonios/v2ray-configs`
- `https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vless.txt`
- `https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/trojan.txt`
- `https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vmess.txt`
- `https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/ss.txt`
- `https://github.com/MatinGhanbari/v2ray-configs`
- `https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt`
- `https://github.com/ippscan/v2rayNEW-configs`
- `https://raw.githubusercontent.com/ippscan/v2rayNEW-configs/main/Sub1.txt`
- `https://raw.githubusercontent.com/ippscan/v2rayNEW-configs/main/Sub2.txt`

Local seeds used:
- `BEST_FOR_HIDDIFY.txt`
- `BEST_FOR_HIDDIFY_ranked.txt`
- `trojan_checked.txt`
- `vless_checked.txt`
- `ss_checked.txt`
- `vmess_checked.txt`
- `WORKING_UNIQUE_NOW.txt`
- `WORKING_NOW_TROJAN.txt`

## Important fixes already made
### Pipeline / validation
- Added staged source lanes: `live_primary`, `trusted_checked`, `trusted_local_seed`, `verified_history`, `seed_unconfirmed`, `noisy_expansion`.
- Switched `HiddifyCli` runtime-check from broken `-d` settings mode to separate working directories via `-D`.
- Each real-check now runs in isolated temp folders under `runtime/temp/run_*`.
- Added runtime log capture for each `HiddifyCli` run.
- Fixed false-positive output: unconfirmed/history rows no longer masquerade as primary verified results.
- Added history recheck on this PC before reusing old working entries.
- Added country fallback from tag when `exit_ip` geo is missing.
- Release path now prioritizes `VLESS` and `Trojan`; `VMESS/SS` are effectively de-prioritized for real verified output.
- `Smart` now behaves more like `Quick+`: history and trusted checked come before noisy live expansion.

### UI
- Added `verification_tier` awareness in badges.
- Stats now separate `Fresh`, `Seed`, `History`, `Unconfirmed`, `Visible`.
- Country display is better when geo lookup fails.

## Very important runtime findings
### 1. Hiddify import works
Import is not the main problem.

Relevant file:
- `tools/hiddify_named_import.py`

It successfully creates local Hiddify profiles and patches their names.

### 2. The real problem was twofold
- Anfisa previously showed many configs that were not actually device-confirmed.
- `HiddifyCli` runtime-check was partially broken by invalid launch mode and polluted local runtime files.

### 3. HiddifyCli is still fragile
There is still a stubborn external `HiddifyCli.exe` process that often survives normal kill attempts and can interfere with validation.

Observed before:
- `Hiddify.exe` PID `34476`
- `HiddifyCli.exe` PID `4252`

Both sometimes return access denied on kill.

## Latest verified state
### Quick Recovery (latest successful shape)
Command:
```powershell
python tools\anfisa_pipeline.py --mode quick_recovery --real-limit 20
```

Recent result:
- `checked_total = 4`
- `visible_total = 4`
- `working_unique_exit_ip = 4`
- runtime about `96s`

Best current device-confirmed examples:
- `Russia` `212.41.28.109:4443` `real_latency_ms ~ 262`
- `Germany` `srv162.towersflowerss.com:443` `real_latency_ms ~ 322`
- `Austria` `srv152.towersflowerss.com:64534` `real_latency_ms ~ 469`
- `Netherlands` `193.39.143.101:65000` `real_latency_ms ~ 471`

### Smart Test (latest)
Command:
```powershell
python tools\anfisa_pipeline.py --mode smart --real-limit 30
```

Recent result:
- `checked_total = 27`
- `fresh_live_total = 1`
- `visible_total = 6`
- runtime about `297s`

Notable result:
- one live-confirmed `SS` from noisy expansion appeared around `314ms`
- several retained confirmed `VLESS` remained usable but mostly above `300ms`

## Why the user still sometimes sees 0
If the app run lands on a bad batch/day, `Smart Test` can still spend budget on bad families and return `0`.

Typical fail reasons in `latest.json`:
- `tls_fail`
- `port_not_ready`
- `ipify_fail`

Typical runtime symptoms in `data/results/debug_real_check.log`:
- remote TLS handshake failure
- delayed port readiness
- some checked families fully dead on this machine

So `0` now usually means "honest failure on this PC", not "UI bug".

## What to do next if more work is needed
Highest-value continuation:
1. Make `Smart Test` fully `Quick-first` in final product behavior.
   - Current code already moved in this direction, but still needs tighter hard-stops and less live waste.
   - If no `<=300ms` winners appear in the first stage, stop trying broad live pools.
   - Move straight to the best-performing checked VLESS families.
2. Build a strict local golden pool.
   - Persist only configs that achieved both `cloudflare_http` and `ipify_https`.
   - Start every future run from that pool.
3. Add a hard latency filter mode.
   - Release mode should optionally keep only `real_latency_ms <= 300`.
   - If fewer than 3 exist, fall back to `<=500`.
4. Reduce family waste.
   - Auto-blacklist families after repeated `tls_fail`.
   - Recheck only previously successful families first.
5. Consider disabling `VMESS` and `SS` in normal verified mode entirely.
   - Keep them only in experimental/noisy lane.
6. Improve region naming.
   - Add better parsing for tags like `BE`, `AT`, `CZ`, `NL`, `FR`, `FI`, etc.
7. Optionally add a "Release Mode" toggle in UI:
   - `Verified only`
   - `<=300ms only`
   - `Use golden pool first`

## Current product truth
This project is no longer lying about obviously dead configs.

It is now good at:
- finding some real working configs on this machine
- importing them into Hiddify
- preserving and rechecking previously confirmed ones

It is still weak at:
- reliably finding `5-20` diverse proxies under `300ms`
- surviving bad public-pool days without dropping to low counts

## Files and logs to inspect first
- `tools/anfisa_pipeline.py`
- `scripts/anfisa_app.gd`
- `data/results/latest.json`
- `data/results/debug_real_check.log`
- `data/results/verified_history.json`
- `data/results/proxy_state.json`
- `C:\Users\rysla\AppData\Roaming\Hiddify\hiddify\box.log`
- `C:\Users\rysla\AppData\Roaming\Hiddify\hiddify\current-config.json`

## Recommended immediate command
```powershell
python tools\anfisa_pipeline.py --mode quick_recovery --real-limit 20
```

That is the current most reliable baseline.
