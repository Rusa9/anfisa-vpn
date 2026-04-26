from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path


HIDDIFY_ROOT = Path(r"C:\Users\rysla\AppData\Roaming\Hiddify\hiddify")
CONFIGS_DIR = HIDDIFY_ROOT / "configs"
DB_PATH = HIDDIFY_ROOT / "db.sqlite"
CURRENT_CONFIG_PATH = HIDDIFY_ROOT / "current-config.json"


def get_latest_profile_row() -> tuple[str, str] | tuple[None, None]:
    if not DB_PATH.exists():
        return None, None
    con = sqlite3.connect(str(DB_PATH))
    cur = con.cursor()
    cur.execute("SELECT id,name FROM profile_entries ORDER BY rowid DESC LIMIT 1")
    row = cur.fetchone()
    con.close()
    if row:
        return str(row[0]), str(row[1])
    return None, None


def patch_current_config(endpoint: str, pretty_name: str) -> None:
    if not CURRENT_CONFIG_PATH.exists():
        return
    try:
        parsed = json.loads(CURRENT_CONFIG_PATH.read_text(encoding="utf-8", errors="ignore"))
        changed = False
        old_tags: list[str] = []
        for outbound in parsed.get("outbounds", []):
            outbound_endpoint = "%s:%s" % (str(outbound.get("server", "")), str(outbound.get("server_port", "")))
            if outbound_endpoint == endpoint and outbound.get("type") in {"trojan", "vless", "vmess", "shadowsocks"}:
                old_tags.append(str(outbound.get("tag", "")))
                outbound["tag"] = pretty_name
                changed = True

        if changed:
            for outbound in parsed.get("outbounds", []):
                if outbound.get("type") in {"selector", "urltest"}:
                    items = outbound.get("outbounds", [])
                    if isinstance(items, list):
                        for index, item in enumerate(items):
                            if str(item) in old_tags:
                                items[index] = pretty_name
                        outbound["outbounds"] = items
            CURRENT_CONFIG_PATH.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def patch_profile_record(profile_id: str, endpoint: str, pretty_name: str) -> int:
    path = CONFIGS_DIR / f"{profile_id}.json"
    if path.exists():
        try:
            parsed = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            outbounds = parsed.get("outbounds", [])
            if outbounds:
                outbounds[0]["tag"] = pretty_name
                parsed["outbounds"] = outbounds
                path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    if DB_PATH.exists():
        con = sqlite3.connect(str(DB_PATH))
        cur = con.cursor()
        cur.execute("UPDATE profile_entries SET name=? WHERE id=?", (pretty_name, profile_id))
        con.commit()
        con.close()

    patch_current_config(endpoint, pretty_name)
    return 0


def patch_profile(endpoint: str, pretty_name: str, timeout_sec: float = 18.0) -> int:
    started = time.time()
    baseline_id, _baseline_name = get_latest_profile_row()
    while time.time() - started < timeout_sec:
        latest_id, _latest_name = get_latest_profile_row()
        if latest_id is not None and latest_id != baseline_id:
            return patch_profile_record(latest_id, endpoint, pretty_name)

        config_files = sorted(CONFIGS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for path in config_files:
            try:
                parsed = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                outbounds = parsed.get("outbounds", [])
                if not outbounds:
                    continue
                outbound = outbounds[0]
                outbound_endpoint = "%s:%s" % (str(outbound.get("server", "")), str(outbound.get("server_port", "")))
                if outbound_endpoint != endpoint:
                    continue
                return patch_profile_record(path.stem, endpoint, pretty_name)
            except Exception:
                continue
        time.sleep(0.8)
    return 1


def main() -> int:
    if len(sys.argv) < 3:
        return 2
    endpoint = sys.argv[1]
    pretty_name = sys.argv[2]
    timeout_sec = float(sys.argv[3]) if len(sys.argv) > 3 else 18.0
    return patch_profile(endpoint, pretty_name, timeout_sec)


if __name__ == "__main__":
    raise SystemExit(main())
