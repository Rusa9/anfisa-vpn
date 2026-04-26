from __future__ import annotations

import http.server
import json
import socketserver
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote


HIDDIFY_ROOT = Path(r"C:\Users\rysla\AppData\Roaming\Hiddify\hiddify")
CONFIGS_DIR = HIDDIFY_ROOT / "configs"
DB_PATH = HIDDIFY_ROOT / "db.sqlite"
CURRENT_CONFIG_PATH = HIDDIFY_ROOT / "current-config.json"
POWERSHELL = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"


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


def patch_profile_record(profile_id: str, endpoint: str, pretty_name: str) -> None:
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
        cur.execute("UPDATE profile_entries SET name=?, type=?, url=NULL WHERE id=?", (pretty_name, "local", profile_id))
        con.commit()
        con.close()

    patch_current_config(endpoint, pretty_name)


def wait_for_new_profile(endpoint: str, pretty_name: str, baseline_id: str | None, timeout_sec: float) -> int:
    started = time.time()
    while time.time() - started < timeout_sec:
        latest_id, _latest_name = get_latest_profile_row()
        if latest_id is not None and latest_id != baseline_id:
            patch_profile_record(latest_id, endpoint, pretty_name)
            return 0
        time.sleep(0.5)
    return 1


def run_import_server(config_text: str, pretty_name: str, endpoint: str) -> int:
    baseline_id, _baseline_name = get_latest_profile_row()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = "#profile-title: %s\n%s\n" % (pretty_name, config_text)
            data = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Profile-Title", pretty_name)
            self.send_header("Content-Disposition", 'attachment; filename="anfisa_proxy.txt"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    with socketserver.TCPServer(("127.0.0.1", 0), Handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        uri = "hiddify://import/http://127.0.0.1:%d/config.txt#%s" % (port, quote(pretty_name, safe=""))
        subprocess.run([POWERSHELL, "-NoProfile", "-Command", "Start-Process '%s'" % uri], check=False)
        result = wait_for_new_profile(endpoint, pretty_name, baseline_id, 18.0)
        httpd.shutdown()
        thread.join(timeout=2)
        return result


def main() -> int:
    if len(sys.argv) < 4:
        return 2
    endpoint = sys.argv[1]
    pretty_name = sys.argv[2]
    config_text = sys.argv[3]
    return run_import_server(config_text, pretty_name, endpoint)


if __name__ == "__main__":
    raise SystemExit(main())
