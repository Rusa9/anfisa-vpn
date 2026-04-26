from __future__ import annotations

import asyncio
import argparse
import base64
import html
import json
import re
import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, unquote, urlsplit

from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
TEMP_DIR = PROJECT_ROOT / "runtime" / "temp"
USER_BLACKLIST_PATH = PROJECT_ROOT / "data" / "user_blacklist.json"
VERIFIED_HISTORY_PATH = PROJECT_ROOT / "data" / "results" / "verified_history.json"
PROXY_STATE_PATH = PROJECT_ROOT / "data" / "results" / "proxy_state.json"
GEO_CACHE_PATH = PROJECT_ROOT / "data" / "results" / "geo_cache.json"
PIPELINE_STATE_PATH = PROJECT_ROOT / "data" / "results" / "pipeline_state.json"
PIPELINE_STOP_PATH = PROJECT_ROOT / "data" / "results" / "pipeline_stop.flag"
DEBUG_LOG_PATH = PROJECT_ROOT / "data" / "results" / "debug_real_check.log"

def _debug_log(msg: str) -> None:
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass
LEGACY_SEED_FILES = [
    Path(r"C:\Users\rysla\OneDrive\Рабочий стол\VPN_готово\REAL_WORKING.txt"),
    Path(r"C:\Users\rysla\OneDrive\Рабочий стол\VPN_готово\REAL_WORKING_UNIQUE_BY_IP.txt"),
    Path(r"C:\Users\rysla\OneDrive\Рабочий стол\VPN_готово\WORKING_NOW_TROJAN.txt"),
    Path(r"C:\Users\rysla\OneDrive\Рабочий стол\VPN_готово\WORKING_UNIQUE_NOW.txt"),
    Path(r"C:\Users\rysla\OneDrive\Рабочий стол\VPN_готово\trojan_checked.txt"),
    Path(r"C:\Users\rysla\OneDrive\Рабочий стол\VPN_готово\vless_checked.txt"),
    Path(r"C:\Users\rysla\OneDrive\Рабочий стол\VPN_готово\vmess_checked.txt"),
]

HIDDIFY_CLI = Path(r"C:\Program Files\Hiddify\HiddifyCli.exe")
LEGACY_SEED_DIR = Path.home() / "OneDrive" / "Рабочий стол" / "VPN_готово"
LEGACY_SEED_FILES = [
    LEGACY_SEED_DIR / "REAL_WORKING.txt",
    LEGACY_SEED_DIR / "REAL_WORKING_UNIQUE_BY_IP.txt",
    LEGACY_SEED_DIR / "WORKING_NOW_TROJAN.txt",
    LEGACY_SEED_DIR / "WORKING_UNIQUE_NOW.txt",
    LEGACY_SEED_DIR / "trojan_checked.txt",
    LEGACY_SEED_DIR / "vless_checked.txt",
    LEGACY_SEED_DIR / "vmess_checked.txt",
]
TRUSTED_SEED_FILES = LEGACY_SEED_FILES[:4]
CHECKED_SEED_FILES = LEGACY_SEED_FILES[4:]
REMOTE_CHECKED_SEED_URLS = [
    "https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/BLACK_VLESS_RUS_mobile.txt",
    "https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/BLACK_SS+All_RUS.txt",
]
SOURCE_URLS = {
    "vless": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt",
    "trojan": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/trojan.txt",
    "vmess": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vmess.txt",
    "ss": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/ss.txt",
}
PROTOCOL_PRIORITY = {"trojan": 24, "vless": 22, "vmess": 12, "ss": 8}
TLS_LIKE_PORTS = {443, 8443, 2053, 2083, 2087, 2096}
LOW_VALUE_PORTS = {80, 8080, 8880}
PROTOCOL_TIMING: dict[tuple[str, str, str], dict] = {
    ("trojan", "ws", "tls"):     {"startup_wait": 3.5, "timeout": 9},
    ("trojan", "tcp", "tls"):    {"startup_wait": 3.0, "timeout": 8},
    ("trojan", "grpc", "tls"):   {"startup_wait": 3.5, "timeout": 9},
    ("vless", "tcp", "reality"): {"startup_wait": 5.5, "timeout": 12},
    ("vless", "ws", "reality"):  {"startup_wait": 5.5, "timeout": 12},
    ("vless", "grpc", "reality"):{"startup_wait": 6.0, "timeout": 13},
    ("vless", "tcp", "tls"):     {"startup_wait": 3.5, "timeout": 9},
    ("vless", "ws", "tls"):      {"startup_wait": 3.5, "timeout": 9},
    ("vless", "grpc", "tls"):    {"startup_wait": 4.0, "timeout": 10},
    ("vmess", "ws", "tls"):      {"startup_wait": 4.5, "timeout": 11},
    ("vmess", "tcp", "tls"):     {"startup_wait": 4.0, "timeout": 10},
    ("vmess", "tcp", ""):        {"startup_wait": 4.0, "timeout": 10},
    ("vmess", "ws", ""):         {"startup_wait": 4.5, "timeout": 11},
    ("vmess", "grpc", "tls"):    {"startup_wait": 4.5, "timeout": 11},
    ("vmess", "http", ""):       {"startup_wait": 4.0, "timeout": 10},
}
PROTOCOL_TIMING_DEFAULT = {"startup_wait": 4.0, "timeout": 10}
RECOMMENDED_MAX_MS = 300
COUNTRY_KEYWORDS = {
    "netherlands": "Netherlands",
    "holland": "Netherlands",
    "germany": "Germany",
    "france": "France",
    "poland": "Poland",
    "sweden": "Sweden",
    "finland": "Finland",
    "estonia": "Estonia",
    "belarus": "Belarus",
    "czech": "Czechia",
    "canada": "Canada",
    "turkey": "Turkey",
    "japan": "Japan",
    "italy": "Italy",
    "usa": "United States",
    "united states": "United States",
    "uk ": "United Kingdom",
    "united kingdom": "United Kingdom",
    "england": "United Kingdom",
    "russia": "Russia",
    "moscow": "Russia",
    "saint petersburg": "Russia",
    "greece": "Greece",
    "norway": "Norway",
    "kazakhstan": "Kazakhstan",
    "romania": "Romania",
    "switzerland": "Switzerland",
}
COUNTRY_CODES = {
    "DE": "Germany",
    "NL": "Netherlands",
    "PL": "Poland",
    "FR": "France",
    "SE": "Sweden",
    "FI": "Finland",
    "EE": "Estonia",
    "RU": "Russia",
    "BY": "Belarus",
    "CZ": "Czechia",
    "CA": "Canada",
    "US": "United States",
    "UK": "United Kingdom",
    "TR": "Turkey",
    "JP": "Japan",
    "IT": "Italy",
    "KZ": "Kazakhstan",
    "RO": "Romania",
    "NO": "Norway",
    "CH": "Switzerland",
}
FLAG_REGIONS = {
    "🇩🇪": "Germany",
    "🇳🇱": "Netherlands",
    "🇵🇱": "Poland",
    "🇫🇷": "France",
    "🇸🇪": "Sweden",
    "🇫🇮": "Finland",
    "🇪🇪": "Estonia",
    "🇷🇺": "Russia",
    "🇧🇾": "Belarus",
    "🇨🇿": "Czechia",
    "🇨🇦": "Canada",
    "🇺🇸": "United States",
    "🇬🇧": "United Kingdom",
    "🇹🇷": "Turkey",
    "🇯🇵": "Japan",
    "🇮🇹": "Italy",
    "🇰🇿": "Kazakhstan",
    "🇷🇴": "Romania",
    "🇳🇴": "Norway",
    "🇨🇭": "Switzerland",
}


@dataclass
class Candidate:
    raw: str
    protocol: str
    host: str
    port: int
    tag: str
    region: str
    security: str = ""
    network: str = ""
    host_header: str = ""
    sni: str = ""
    path: str = ""
    score: int = 0
    quick_reachable: bool = False
    quick_latency_ms: Optional[int] = None
    source_lane: str = "live"


def ensure_dirs() -> None:
    for path in [RAW_DIR, RESULTS_DIR, TEMP_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def reset_pipeline_control_files() -> None:
    if PIPELINE_STOP_PATH.exists():
        PIPELINE_STOP_PATH.unlink(missing_ok=True)


def should_stop() -> bool:
    return PIPELINE_STOP_PATH.exists()


def write_pipeline_state(**kwargs) -> None:
    current = {}
    if PIPELINE_STATE_PATH.exists():
        try:
            current = json.loads(PIPELINE_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            current = {}
    current.update(kwargs)
    PIPELINE_STATE_PATH.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")


def compute_stage_progress(base_progress: int, span: int, completed: int, total: int) -> int:
    if total <= 0:
        return base_progress
    ratio = max(0.0, min(1.0, float(completed) / float(total)))
    return int(base_progress + ratio * span)


def normalize_line(line: str) -> str:
    return html.unescape(line.strip().strip("`").strip("'").strip('"'))


def first(query: dict, key: str) -> str:
    values = query.get(key, [])
    return values[0].strip() if values else ""


def is_truthy_query_value(value: str) -> bool:
    lowered = (value or "").strip().lower()
    return lowered in {"1", "true", "yes", "on"}


def guess_region(tag: str) -> str:
    decoded = unquote(tag)
    lowered = decoded.lower()
    for key, value in COUNTRY_KEYWORDS.items():
        if key in lowered:
            return value
    for flag, value in FLAG_REGIONS.items():
        if flag in decoded:
            return value
    upper = decoded.upper()
    for code, value in COUNTRY_CODES.items():
        if f"{code}-" in upper or f" {code} " in upper or f"_{code}_" in upper or upper.startswith(code + "-"):
            return value
    return "Unknown"


def parse_vless(line: str) -> Optional[Candidate]:
    parsed = urlsplit(line)
    query = parse_qs(parsed.query, keep_blank_values=True)
    host = (parsed.hostname or "").strip().lower()
    if not host or not parsed.port or not parsed.username:
        return None

    tag = unquote(parsed.fragment or host)
    return Candidate(
        raw=line,
        protocol="vless",
        host=host,
        port=parsed.port,
        tag=tag,
        region=guess_region(tag),
        security=first(query, "security"),
        network=first(query, "type") or "tcp",
        host_header=first(query, "host"),
        sni=first(query, "sni"),
        path=first(query, "path"),
    )


def parse_trojan(line: str) -> Optional[Candidate]:
    parsed = urlsplit(line)
    query = parse_qs(parsed.query, keep_blank_values=True)
    host = (parsed.hostname or "").strip().lower()
    if not host or not parsed.port or not parsed.username:
        return None

    tag = unquote(parsed.fragment or host)
    return Candidate(
        raw=line,
        protocol="trojan",
        host=host,
        port=parsed.port,
        tag=tag,
        region=guess_region(tag),
        security=first(query, "security") or "tls",
        network=first(query, "type") or "tcp",
        host_header=first(query, "host"),
        sni=first(query, "sni"),
        path=first(query, "path"),
    )


def parse_vmess(line: str) -> Optional[Candidate]:
    if not line.startswith("vmess://"):
        return None
    try:
        encoded = line[len("vmess://"):].split("#")[0].strip()
        padded = encoded + "=" * ((4 - len(encoded) % 4) % 4)
        obj = json.loads(base64.b64decode(padded).decode("utf-8", errors="ignore"))
    except Exception:
        return None

    host = str(obj.get("add", "")).strip().lower()
    try:
        port = int(obj.get("port", 0))
    except (ValueError, TypeError):
        return None
    if not host or not port:
        return None

    frag_tag = ""
    if "#" in line:
        frag_tag = unquote(line.split("#", 1)[1]).strip()
    tag = frag_tag or str(obj.get("ps", host)).strip() or host
    network = str(obj.get("net", "tcp")).strip() or "tcp"
    tls_value = str(obj.get("tls", "")).strip().lower()
    security = "tls" if tls_value in {"tls", "xtls"} else ""
    sni = str(obj.get("sni", "")).strip() or str(obj.get("add", "")).strip()
    host_header = str(obj.get("host", "")).strip()
    path = str(obj.get("path", "")).strip()
    return Candidate(
        raw=line,
        protocol="vmess",
        host=host,
        port=port,
        tag=tag,
        region=guess_region(tag),
        security=security,
        network=network,
        host_header=host_header,
        sni=sni,
        path=path,
    )


def parse_basic(line: str, protocol: str) -> Optional[Candidate]:
    if protocol == "vless":
        return parse_vless(line)
    if protocol == "trojan":
        return parse_trojan(line)
    if protocol == "vmess":
        return parse_vmess(line)
    if line.startswith(f"{protocol}://"):
        parsed = urlsplit(line)
        host = (parsed.hostname or "").strip().lower()
        if host and parsed.port:
            tag = unquote(parsed.fragment or host)
            return Candidate(raw=line, protocol=protocol, host=host, port=parsed.port, tag=tag, region=guess_region(tag))
    return None


def download_sources() -> dict:
    downloaded = {}
    proxy_handler = None
    try:
        from urllib.request import ProxyHandler
        proxy_handler = ProxyHandler()
    except Exception:
        pass
    for protocol, url in SOURCE_URLS.items():
        try:
            request = Request(url, headers={"User-Agent": "AnfisaVPN/0.1"})
            with urlopen(request, timeout=25) as response:
                text = response.read().decode("utf-8", errors="ignore")
            (RAW_DIR / f"{protocol}.txt").write_text(text, encoding="utf-8")
            downloaded[protocol] = len(text.splitlines())
        except Exception as exc:
            cached_path = RAW_DIR / f"{protocol}.txt"
            if cached_path.exists():
                cached_lines = len(cached_path.read_text(encoding="utf-8", errors="ignore").splitlines())
                downloaded[protocol] = cached_lines
                _debug_log("download %s failed (%s), using cached %d lines" % (protocol, exc, cached_lines))
            else:
                downloaded[protocol] = 0
                _debug_log("download %s failed (%s), no cache available" % (protocol, exc))
    return downloaded


def load_candidates(max_per_protocol: int = 700) -> tuple[list[Candidate], dict]:
    parsed_counts = {}
    all_candidates: list[Candidate] = []
    for protocol in SOURCE_URLS.keys():
        path = RAW_DIR / f"{protocol}.txt"
        seen: set[str] = set()
        count = 0
        if not path.exists():
            parsed_counts[protocol] = 0
            continue
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = normalize_line(raw)
            if not line or line in seen:
                continue
            seen.add(line)
            candidate = parse_basic(line, protocol)
            if candidate is None:
                continue
            all_candidates.append(candidate)
            count += 1
            if count >= max_per_protocol:
                break
        parsed_counts[protocol] = count
    return all_candidates, parsed_counts


def load_seed_candidates(limit_per_file: int = 30, paths: Optional[list[Path]] = None, source_lane: str = "trusted_seed") -> list[Candidate]:
    seeds: list[Candidate] = []
    seen: set[str] = set()
    for path in paths or LEGACY_SEED_FILES:
        if not path.exists():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        count = 0
        for raw in lines:
            line = normalize_line(raw)
            if not line or line in seen:
                continue
            candidate = parse_basic(line, "trojan" if line.startswith("trojan://") else "vless" if line.startswith("vless://") else "vmess" if line.startswith("vmess://") else "ss")
            if candidate is None:
                continue
            candidate.source_lane = source_lane
            seen.add(line)
            seeds.append(candidate)
            count += 1
            if count >= limit_per_file:
                break
    return seeds


def load_remote_seed_candidates(urls: list[str], limit_per_url: int = 60, source_lane: str = "checked_seed") -> list[Candidate]:
    seeds: list[Candidate] = []
    seen: set[str] = set()
    for url in urls:
        try:
            request = Request(url, headers={"User-Agent": "AnfisaVPN/0.2"})
            with urlopen(request, timeout=15) as response:
                text = response.read().decode("utf-8", errors="ignore")
        except Exception as exc:
            _debug_log("remote seed failed %s (%s)" % (url, exc))
            continue
        count = 0
        for raw in text.splitlines():
            line = normalize_line(raw)
            if not line or line in seen:
                continue
            proto = "trojan" if line.startswith("trojan://") else "vless" if line.startswith("vless://") else "vmess" if line.startswith("vmess://") else "ss" if line.startswith("ss://") else ""
            if proto == "":
                continue
            candidate = parse_basic(line, proto)
            if candidate is None:
                continue
            candidate.source_lane = source_lane
            seen.add(line)
            seeds.append(candidate)
            count += 1
            if count >= limit_per_url:
                break
    return seeds


def build_unconfirmed_seed_history(
    trusted_candidates: list[Candidate],
    current_items: list[dict],
    target_min_unique: int,
    geo_cache: dict,
) -> list[dict]:
    result = list(current_items)
    seen_endpoints = {str(item.get("endpoint", "")) for item in result}
    seen_configs = {str(item.get("config", "")) for item in result}
    for candidate in trusted_candidates:
        endpoint = f"{candidate.host}:{candidate.port}"
        if endpoint in seen_endpoints or candidate.raw in seen_configs:
            continue
        quick_ms = candidate.quick_latency_ms
        item = {
            "config": candidate.raw,
            "protocol": candidate.protocol,
            "region": candidate.region,
            "source_region": candidate.region,
            "tag": candidate.tag,
            "endpoint": endpoint,
            "family_key": family_key_from_candidate(candidate),
            "exit_ip": None,
            "quick_latency_ms": quick_ms,
            "real_latency_ms": None,
            "effective_latency_ms": effective_latency_ms(quick_ms, None),
            "quality_tier": classify_quality(quick_ms, None),
            "recommended": (quick_ms is not None and quick_ms <= RECOMMENDED_MAX_MS),
            "score": candidate.score,
            "checks": {},
            "open_mode": "clipboard_then_hiddify",
            "passed": False,
            "reason": "trusted_seed_unconfirmed",
            "source_kind": "history",
            "retained_from_trusted_seed_file": True,
            "retained_without_live_confirmation": True,
        }
        if item["region"] != "Unknown":
            item["exit_country"] = item["region"]
        result.append(item)
        seen_endpoints.add(endpoint)
        seen_configs.add(candidate.raw)
        if len(result) >= target_min_unique:
            break
    return annotate_result_countries(result, geo_cache)


def score_candidate(candidate: Candidate) -> int:
    score = PROTOCOL_PRIORITY.get(candidate.protocol, 0)
    if candidate.security == "reality":
        score += 28
    elif candidate.security == "tls":
        score += 20
    elif candidate.security in {"none", ""}:
        score += 4

    if candidate.network in {"tcp", "grpc"}:
        score += 10
    elif candidate.network in {"ws", "httpupgrade", "xhttp"}:
        score += 6
    if candidate.protocol == "trojan" and candidate.network == "ws" and candidate.security == "tls":
        score += 14
    if candidate.protocol == "trojan" and candidate.security == "reality":
        score -= 8

    if candidate.sni:
        score += 4
    if candidate.host_header:
        score += 3
    if candidate.port in TLS_LIKE_PORTS:
        score += 5
    if candidate.port in LOW_VALUE_PORTS:
        score -= 5

    lowered = candidate.raw.lower()
    if "@shh_proxy" in lowered or "@ghalagyann" in lowered:
        score -= 10
    if len(candidate.raw) > 520:
        score -= 12
    if len(candidate.path) > 160:
        score -= 6
    return score


async def probe_endpoint(host: str, port: int, timeout: float) -> tuple[bool, Optional[int]]:
    start = time.perf_counter()
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host=host, port=port, family=socket.AF_UNSPEC), timeout=timeout)
        latency_ms = int((time.perf_counter() - start) * 1000)
        writer.close()
        await writer.wait_closed()
        return True, latency_ms
    except Exception:
        return False, None


async def quick_filter(candidates: list[Candidate], timeout: float = 1.3, concurrency: int = 180) -> tuple[list[Candidate], dict]:
    semaphore = asyncio.Semaphore(concurrency)
    reachable_counts = {key: 0 for key in SOURCE_URLS.keys()}
    seen_endpoints: set[str] = set()
    filtered: list[Candidate] = []

    async def worker(candidate: Candidate) -> None:
        key = f"{candidate.protocol}|{candidate.host}|{candidate.port}"
        if key in seen_endpoints:
            return
        seen_endpoints.add(key)
        async with semaphore:
            ok, latency_ms = await probe_endpoint(candidate.host, candidate.port, timeout)
        if ok:
            candidate.quick_reachable = True
            candidate.quick_latency_ms = latency_ms
            candidate.score = score_candidate(candidate) + max(0, 18 - min((latency_ms or 999) // 50, 18))
            filtered.append(candidate)
            reachable_counts[candidate.protocol] += 1

    await asyncio.gather(*[worker(candidate) for candidate in candidates])
    filtered.sort(key=lambda item: (-item.score, item.quick_latency_ms or 9999))
    return filtered, reachable_counts


def build_hiddify_outbound(candidate: Candidate) -> Optional[dict]:
    parsed = urlsplit(candidate.raw)
    query = parse_qs(parsed.query, keep_blank_values=True)

    if candidate.protocol == "vless":
        outbound: dict = {
            "type": "vless",
            "tag": candidate.tag,
            "server": candidate.host,
            "server_port": candidate.port,
            "uuid": unquote(parsed.username or ""),
            "packet_encoding": "xudp",
        }
        flow = first(query, "flow")
        if flow:
            outbound["flow"] = flow

        security = first(query, "security")
        fingerprint = first(query, "fp")
        sni = first(query, "sni") or first(query, "host")
        if security in {"tls", "reality"}:
            tls: dict = {"enabled": True}
            if sni:
                tls["server_name"] = sni
            if fingerprint:
                tls["utls"] = {"enabled": True, "fingerprint": fingerprint}
            if is_truthy_query_value(first(query, "allowInsecure")) or is_truthy_query_value(first(query, "insecure")):
                tls["insecure"] = True
            if security == "reality":
                public_key = first(query, "pbk")
                if not public_key:
                    return None
                reality: dict = {"enabled": True, "public_key": public_key}
                short_id = first(query, "sid")
                if short_id:
                    reality["short_id"] = short_id
                tls["reality"] = reality
            outbound["tls"] = tls

        network = first(query, "type") or "tcp"
        if network == "ws":
            transport = {"type": "ws", "path": first(query, "path") or "/"}
            host_header = first(query, "host")
            if host_header:
                transport["headers"] = {"Host": host_header}
            outbound["transport"] = transport
        elif network == "grpc":
            service_name = first(query, "serviceName") or first(query, "service_name")
            transport = {"type": "grpc"}
            if service_name:
                transport["service_name"] = service_name
            outbound["transport"] = transport
        elif network == "httpupgrade":
            transport = {"type": "httpupgrade", "path": first(query, "path") or "/"}
            host_header = first(query, "host")
            if host_header:
                transport["headers"] = {"Host": host_header}
            outbound["transport"] = transport
        elif network not in {"tcp", "xhttp", "splithttp"}:
            return None
        return outbound

    if candidate.protocol == "trojan":
        outbound = {
            "type": "trojan",
            "tag": candidate.tag,
            "server": candidate.host,
            "server_port": candidate.port,
            "password": unquote(parsed.username or ""),
        }
        tls: dict = {"enabled": True}
        sni = first(query, "sni") or first(query, "host")
        if sni:
            tls["server_name"] = sni
        fingerprint = first(query, "fp")
        if fingerprint:
            tls["utls"] = {"enabled": True, "fingerprint": fingerprint}
        if is_truthy_query_value(first(query, "allowInsecure")) or is_truthy_query_value(first(query, "insecure")):
            tls["insecure"] = True
        outbound["tls"] = tls

        network = first(query, "type") or "tcp"
        if network == "ws":
            transport = {"type": "ws", "path": first(query, "path") or "/"}
            host_header = first(query, "host")
            if host_header:
                transport["headers"] = {"Host": host_header}
            outbound["transport"] = transport
        elif network == "grpc":
            transport = {"type": "grpc"}
            service_name = first(query, "serviceName") or first(query, "service_name")
            if service_name:
                transport["service_name"] = service_name
            outbound["transport"] = transport
        elif network != "tcp":
            return None
        return outbound

    if candidate.protocol == "vmess":
        try:
            encoded = candidate.raw[len("vmess://"):].split("#")[0].strip()
            padded = encoded + "=" * ((4 - len(encoded) % 4) % 4)
            obj = json.loads(base64.b64decode(padded).decode("utf-8", errors="ignore"))
        except Exception:
            return None

        uuid = str(obj.get("id", "")).strip()
        if not uuid:
            return None
        security_raw = str(obj.get("scy", "auto")).strip() or "auto"
        alter_id = 0
        try:
            alter_id = int(obj.get("aid", 0) or 0)
        except (ValueError, TypeError):
            alter_id = 0

        outbound = {
            "type": "vmess",
            "tag": candidate.tag,
            "server": candidate.host,
            "server_port": candidate.port,
            "uuid": uuid,
            "security": security_raw,
            "alter_id": alter_id,
        }

        tls_value = str(obj.get("tls", "")).strip().lower()
        if tls_value in {"tls", "xtls"}:
            tls: dict = {"enabled": True}
            sni = str(obj.get("sni", "")).strip() or str(obj.get("add", "")).strip()
            if sni:
                tls["server_name"] = sni
            fp = str(obj.get("fp", "")).strip()
            if fp:
                tls["utls"] = {"enabled": True, "fingerprint": fp}
            skip_verify = obj.get("skip-cert-verify", obj.get("allowInsecure", obj.get("insecure", False)))
            if is_truthy_query_value(str(skip_verify)) or skip_verify is True:
                tls["insecure"] = True
            outbound["tls"] = tls

        network = str(obj.get("net", "tcp")).strip() or "tcp"
        if network == "ws":
            transport: dict = {"type": "ws", "path": str(obj.get("path", "/")).strip() or "/"}
            host_header = str(obj.get("host", "")).strip()
            if host_header:
                transport["headers"] = {"Host": host_header}
            outbound["transport"] = transport
        elif network == "grpc":
            service_name = str(obj.get("path", "")).strip()
            grpc_transport: dict = {"type": "grpc"}
            if service_name:
                grpc_transport["service_name"] = service_name
            outbound["transport"] = grpc_transport
        elif network == "httpupgrade":
            hu_transport: dict = {"type": "httpupgrade", "path": str(obj.get("path", "/")).strip() or "/"}
            host_header = str(obj.get("host", "")).strip()
            if host_header:
                hu_transport["headers"] = {"Host": host_header}
            outbound["transport"] = hu_transport
        elif network == "h2":
            h2_transport: dict = {"type": "http", "path": str(obj.get("path", "/")).strip() or "/"}
            host_header = str(obj.get("host", "")).strip()
            if host_header:
                h2_transport["host"] = [host_header]
            outbound["transport"] = h2_transport
        elif network not in {"tcp", "http"}:
            return None
        return outbound

    if candidate.protocol == "ss":
        parsed_ss = urlsplit(candidate.raw)
        userinfo = parsed_ss.username or ""
        password_part = parsed_ss.password
        method = ""
        password = ""
        if password_part:
            method = unquote(userinfo)
            password = unquote(password_part)
        else:
            try:
                padded = userinfo + "=" * ((4 - len(userinfo) % 4) % 4)
                decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
                if ":" in decoded:
                    method, password = decoded.split(":", 1)
            except Exception:
                return None
        if not method or not password:
            return None
        outbound = {
            "type": "shadowsocks",
            "tag": candidate.tag,
            "server": candidate.host,
            "server_port": candidate.port,
            "method": method,
            "password": password,
        }
        plugin = first(query, "plugin") if query else None
        if plugin:
            return None
        return outbound

    return None


def get_protocol_timing(candidate: Candidate) -> dict:
    network = (candidate.network or "tcp").strip()
    security = (candidate.security or "").strip()
    key = (candidate.protocol, network, security)
    return PROTOCOL_TIMING.get(key, PROTOCOL_TIMING_DEFAULT)


def curl_http_ok(proxy_port: int, timeout: int) -> bool:
    command = [
        "curl.exe",
        "-sS",
        "--max-time",
        str(timeout),
        "--proxy",
        f"http://127.0.0.1:{proxy_port}",
        "-o",
        "NUL",
        "-w",
        "%{http_code}",
        "http://cp.cloudflare.com/",
    ]
    proc = subprocess.run(command, capture_output=True, text=True)
    code = (proc.stdout or "").strip()
    return proc.returncode == 0 and code.isdigit() and 200 <= int(code) < 400


def curl_url_ok(proxy_port: int, timeout: int, url: str) -> tuple[bool, Optional[int]]:
    command = [
        "curl.exe",
        "-sS",
        "--max-time",
        str(timeout),
        "--proxy",
        f"http://127.0.0.1:{proxy_port}",
        "-o",
        "NUL",
        "-w",
        "%{http_code}",
        url,
    ]
    started = time.perf_counter()
    proc = subprocess.run(command, capture_output=True, text=True)
    code = (proc.stdout or "").strip()
    total_ms = int((time.perf_counter() - started) * 1000)
    ok = proc.returncode == 0 and code.isdigit() and 200 <= int(code) < 400
    return ok, total_ms


def classify_fail_reason(cloudflare_ok: bool, exit_ip: Optional[str], quick_latency_ms: Optional[int], candidate: Candidate) -> str:
    if exit_ip:
        return "unknown_runtime_fail"
    if cloudflare_ok:
        return "ipify_fail"
    if candidate.security in {"tls", "reality"}:
        return "tls_fail"
    if quick_latency_ms is not None and quick_latency_ms <= 220:
        return "ipify_fail"
    return "http_fail"


def curl_ip(proxy_port: int, timeout: int) -> Optional[str]:
    command = [
        "curl.exe",
        "-sS",
        "--max-time",
        str(timeout),
        "--proxy",
        f"http://127.0.0.1:{proxy_port}",
        "https://api.ipify.org",
    ]
    proc = subprocess.run(command, capture_output=True, text=True)
    value = (proc.stdout or "").strip()
    if proc.returncode == 0 and value and re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", value):
        return value
    return None


def curl_ip_timed(proxy_port: int, timeout: int) -> tuple[Optional[str], Optional[int]]:
    command = [
        "curl.exe",
        "-sS",
        "--max-time",
        str(timeout),
        "--proxy",
        f"http://127.0.0.1:{proxy_port}",
        "https://api.ipify.org",
    ]
    started = time.perf_counter()
    proc = subprocess.run(command, capture_output=True, text=True)
    total_ms = int((time.perf_counter() - started) * 1000)
    value = (proc.stdout or "").strip()
    if proc.returncode == 0 and value and re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", value):
        return value, total_ms
    return None, None


def wait_for_port(port: int, timeout: float = 5.0) -> bool:
    """Actively poll until HiddifyCli opens the proxy port."""
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except (ConnectionRefusedError, OSError, socket.timeout):
            time.sleep(0.3)
    return False


def classify_quality(quick_latency_ms: Optional[int], real_latency_ms: Optional[int]) -> str:
    if quick_latency_ms is None and real_latency_ms is None:
        return "unknown"
    baseline = quick_latency_ms if quick_latency_ms is not None else real_latency_ms
    if baseline is None:
        return "unknown"
    if baseline <= 150:
        return "excellent"
    if baseline <= 220:
        return "good"
    if baseline <= 300:
        return "usable"
    if baseline <= 700:
        return "slow"
    return "bad"


def effective_latency_ms(quick_latency_ms: Optional[int], real_latency_ms: Optional[int]) -> Optional[int]:
    if quick_latency_ms is not None:
        return int(quick_latency_ms)
    if real_latency_ms is not None:
        return int(real_latency_ms)
    return None


def is_recommended_record(record: dict) -> bool:
    latency_value = effective_latency_ms(record.get("quick_latency_ms"), record.get("real_latency_ms"))
    if latency_value is None:
        return False
    return latency_value <= RECOMMENDED_MAX_MS


def limit_family_candidates(candidates: list[Candidate], max_per_family: int = 2) -> list[Candidate]:
    kept: list[Candidate] = []
    counts: dict[str, int] = {}
    for candidate in candidates:
        fam = family_key_from_candidate(candidate)
        count = counts.get(fam, 0)
        if count >= max_per_family:
            continue
        counts[fam] = count + 1
        kept.append(candidate)
    return kept


def normalize_result_record(item: dict) -> dict:
    record = dict(item)
    real_latency_ms = record.get("real_latency_ms", None)
    try:
        if real_latency_ms is not None:
            real_latency_ms = int(real_latency_ms)
    except Exception:
        real_latency_ms = None
    quick_latency_ms = record.get("quick_latency_ms", None)
    try:
        if quick_latency_ms is not None:
            quick_latency_ms = int(quick_latency_ms)
    except Exception:
        quick_latency_ms = None
    quality_tier = classify_quality(quick_latency_ms, real_latency_ms)
    record["quality_tier"] = quality_tier
    record["effective_latency_ms"] = effective_latency_ms(quick_latency_ms, real_latency_ms)
    record["recommended"] = is_recommended_record(record)
    return record


def load_geo_cache() -> dict:
    if GEO_CACHE_PATH.exists():
        try:
            return json.loads(GEO_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_geo_cache(cache: dict) -> None:
    GEO_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def family_key_from_candidate(candidate: Candidate) -> str:
    token = candidate.sni or candidate.host_header or candidate.host
    return f"{candidate.protocol}|{token.lower()}"


def load_proxy_state() -> dict:
    if PROXY_STATE_PATH.exists():
        try:
            return json.loads(PROXY_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"endpoints": {}, "families": {}}


def save_proxy_state(state: dict) -> None:
    PROXY_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def get_entry_trust(entry: dict) -> int:
    return int(entry.get("consecutive_success", 0)) * 30 + int(entry.get("success_count", 0)) * 8 - int(entry.get("fail_count", 0)) * 6


def candidate_priority(candidate: Candidate, state: dict) -> tuple:
    endpoint = f"{candidate.host}:{candidate.port}"
    family_key = family_key_from_candidate(candidate)
    ep_state = state.get("endpoints", {}).get(endpoint, {})
    fam_state = state.get("families", {}).get(family_key, {})
    trust = get_entry_trust(ep_state) + get_entry_trust(fam_state)
    return (-trust, -candidate.score, candidate.quick_latency_ms or 99999)


def apply_cooldown(candidates: list[Candidate], state: dict, now_ts: int) -> list[Candidate]:
    filtered: list[Candidate] = []
    endpoints_state = state.get("endpoints", {})
    families_state = state.get("families", {})
    for candidate in candidates:
        endpoint = f"{candidate.host}:{candidate.port}"
        family_key = family_key_from_candidate(candidate)
        ep_state = endpoints_state.get(endpoint, {})
        fam_state = families_state.get(family_key, {})
        ep_cooldown = int(ep_state.get("cooldown_until", 0))
        fam_cooldown = int(fam_state.get("cooldown_until", 0))
        ep_trust = get_entry_trust(ep_state)
        fam_trust = get_entry_trust(fam_state)
        if ep_cooldown > now_ts and ep_trust < 40:
            continue
        if fam_cooldown > now_ts and fam_trust < 40:
            continue
        filtered.append(candidate)
    filtered.sort(key=lambda item: candidate_priority(item, state))
    return filtered


def update_proxy_state(state: dict, records: list[dict]) -> dict:
    endpoints = state.setdefault("endpoints", {})
    families = state.setdefault("families", {})
    now_ts = int(time.time())
    for record in records:
        endpoint = str(record.get("endpoint", ""))
        family_key = str(record.get("family_key", ""))
        for bucket, key in ((endpoints, endpoint), (families, family_key)):
            if key == "":
                continue
            entry = bucket.setdefault(key, {})
            entry["success_count"] = int(entry.get("success_count", 0))
            entry["fail_count"] = int(entry.get("fail_count", 0))
            entry["consecutive_success"] = int(entry.get("consecutive_success", 0))
            entry["consecutive_fail"] = int(entry.get("consecutive_fail", 0))
            fail_reason = str(record.get("fail_reason", ""))
            if bucket is families:
                reason_counts = entry.setdefault("family_fail_reason_counts", {})
            else:
                reason_counts = None
            if record.get("passed"):
                entry["success_count"] += 1
                entry["consecutive_success"] += 1
                entry["consecutive_fail"] = 0
                entry["cooldown_until"] = 0
                entry["last_good_at"] = now_ts
                entry["last_latency_ms"] = record.get("real_latency_ms")
            else:
                entry["fail_count"] += 1
                entry["consecutive_fail"] += 1
                entry["consecutive_success"] = 0
                if fail_reason != "":
                    entry["last_fail_reason"] = fail_reason
                    if reason_counts is not None:
                        reason_counts[fail_reason] = int(reason_counts.get(fail_reason, 0)) + 1
                cooldown = 0
                if entry["consecutive_fail"] >= 2:
                    cooldown = min(1800, 5 * 60 * entry["consecutive_fail"])
                if fail_reason in {"tls_fail", "port_not_ready"} and entry["consecutive_fail"] >= 2:
                    cooldown = max(cooldown, min(3600, 10 * 60 * entry["consecutive_fail"]))
                entry["cooldown_until"] = now_ts + cooldown
                entry["last_fail_at"] = now_ts
    return state


def run_single_real_check(candidate: Candidate, index: int, timeout: int, startup_wait: float, port_start: int) -> dict:
    _debug_log(f"START #{index} lane={candidate.source_lane} {candidate.protocol} {candidate.host}:{candidate.port} quick={candidate.quick_latency_ms}ms")
    outbound = build_hiddify_outbound(candidate)
    if outbound is None:
        _debug_log(f"SKIP #{index} unsupported_outbound")
        return {
            "passed": False,
            "protocol": candidate.protocol,
            "region": candidate.region,
            "source_region": candidate.region,
            "tag": candidate.tag,
            "endpoint": f"{candidate.host}:{candidate.port}",
            "family_key": family_key_from_candidate(candidate),
            "quick_latency_ms": candidate.quick_latency_ms,
            "source_lane": candidate.source_lane,
            "fail_reason": "unsupported_outbound",
            "reason": "unsupported_outbound",
        }

    timing = get_protocol_timing(candidate)
    effective_timeout = max(timeout, int(timing["timeout"]))
    effective_startup_wait = max(startup_wait, float(timing["startup_wait"]))

    config_path = TEMP_DIR / f"candidate_{index}.json"
    config_path.write_text(json.dumps({"outbounds": [outbound]}, ensure_ascii=False, indent=2), encoding="utf-8")
    proxy_port = port_start + index
    dns_port = 16450 + index + 1
    clash_api_port = 6756 + index + 1
    hiddify_settings = {
        "log-level": "warn",
        "enable-clash-api": True,
        "clash-api-port": clash_api_port,
        "region": "",
        "block-ads": False,
        "mixed-port": proxy_port,
        "local-dns-port": dns_port,
        "mtu": 9000,
        "strict-route": True,
        "tun-stack": "mixed",
        "remote-dns-address": "1.1.1.1",
        "direct-dns-address": "1.1.1.1",
        "connection-test-url": "http://cp.cloudflare.com/",
        "enable-tun": False,
        "set-system-proxy": False,
    }
    hiddify_settings_path = TEMP_DIR / f"hiddify_settings_{index}.json"
    hiddify_settings_path.write_text(json.dumps(hiddify_settings, ensure_ascii=False), encoding="utf-8")

    def attempt_once() -> dict:
        proc = subprocess.Popen(
            [
                str(HIDDIFY_CLI),
                "run",
                "-c",
                str(config_path),
                "-d",
                str(hiddify_settings_path),
                "--in-proxy-port",
                str(proxy_port),
                "--web-port",
                str(clash_api_port),
                "--dns-direct",
                "1.1.1.1",
                "--dns-remote",
                "1.1.1.1",
                "--log",
                "warn",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        fail_base = {
            "config": candidate.raw,
            "protocol": candidate.protocol,
            "region": candidate.region,
            "source_region": candidate.region,
            "tag": candidate.tag,
            "endpoint": f"{candidate.host}:{candidate.port}",
            "family_key": family_key_from_candidate(candidate),
            "exit_ip": None,
            "quick_latency_ms": candidate.quick_latency_ms,
            "real_latency_ms": None,
            "effective_latency_ms": effective_latency_ms(candidate.quick_latency_ms, None),
            "quality_tier": "unknown",
            "recommended": False,
            "score": candidate.score,
            "checks": {},
            "open_mode": "clipboard_then_hiddify",
            "source_lane": candidate.source_lane,
            "passed": False,
            "fail_reason": "unknown_runtime_fail",
        }
        try:
            if not wait_for_port(proxy_port, effective_startup_wait + 2.0):
                _debug_log(f"FAIL #{index} port_not_ready on :{proxy_port}")
                return {**fail_base, "reason": "port_not_ready", "fail_reason": "port_not_ready"}
            _debug_log(f"PORT #{index} ready on :{proxy_port}, waiting 1.0s grace")
            time.sleep(1.0)
            probe_timeout = min(effective_timeout, 2)
            cloudflare_ok, cloudflare_ms = curl_url_ok(proxy_port, probe_timeout, "http://cp.cloudflare.com/")
            _debug_log(f"CF #{index} ok={cloudflare_ok} ms={cloudflare_ms}")
            exit_ip, ipify_ms = curl_ip_timed(proxy_port, probe_timeout)
            _debug_log(f"IP #{index} exit_ip={exit_ip} ms={ipify_ms}")
            passing_checks = [f for f in [cloudflare_ok, bool(exit_ip)] if f]
            successful_latencies = [
                ms for ok, ms in [
                    (cloudflare_ok, cloudflare_ms),
                    (bool(exit_ip), ipify_ms),
                ] if ok and ms is not None
            ]
            real_latency_ms = min(successful_latencies) if successful_latencies else None
            quality_tier = classify_quality(candidate.quick_latency_ms, real_latency_ms)
            passed = bool(exit_ip) and (cloudflare_ok or (candidate.quick_latency_ms or 9999) <= 180)
            recommended = passed and is_recommended_record(
                {
                    "quick_latency_ms": candidate.quick_latency_ms,
                    "real_latency_ms": real_latency_ms,
                }
            )
            fail_reason = "" if passed else classify_fail_reason(cloudflare_ok, exit_ip, candidate.quick_latency_ms, candidate)
            return {
                "config": candidate.raw,
                "protocol": candidate.protocol,
                "region": candidate.region,
                "source_region": candidate.region,
                "tag": candidate.tag,
                "endpoint": f"{candidate.host}:{candidate.port}",
                "family_key": family_key_from_candidate(candidate),
                "exit_ip": exit_ip,
                "quick_latency_ms": candidate.quick_latency_ms,
                "real_latency_ms": real_latency_ms,
                "effective_latency_ms": effective_latency_ms(candidate.quick_latency_ms, real_latency_ms),
                "quality_tier": quality_tier,
                "recommended": recommended,
                "score": candidate.score,
                "checks": {
                    "cloudflare_http": cloudflare_ok,
                    "ipify_https": bool(exit_ip),
                },
                "open_mode": "clipboard_then_hiddify",
                "source_lane": candidate.source_lane,
                "passed": passed,
                "fail_reason": fail_reason,
                "reason": "ok" if passed else "checks_failed",
            }
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)

    result = attempt_once()
    passed = result.get("passed", False)
    reason = result.get("reason", "?")
    _debug_log(f"RESULT #{index} lane={candidate.source_lane} passed={passed} reason={reason} fail_reason={result.get('fail_reason','')} latency={result.get('real_latency_ms')}")
    if not passed:
        quick_ms = candidate.quick_latency_ms or 9999
        if quick_ms <= 220:
            _debug_log(f"RETRY #{index} (quick={quick_ms}ms)")
            time.sleep(0.8)
            retry = attempt_once()
            if retry.get("passed", False):
                _debug_log(f"RETRY_OK #{index}")
                retry["reason"] = "ok_after_retry"
                return retry
            _debug_log(f"RETRY_FAIL #{index}")
    return result


def real_check(
    candidates: list[Candidate],
    timeout: int = 10,
    startup_wait: float = 4.0,
    port_start: int = 2550,
    max_workers: int = 4,
) -> tuple[list[dict], list[dict]]:
    records: list[dict] = []
    if not HIDDIFY_CLI.exists():
        return [], []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(run_single_real_check, candidate, index, timeout, startup_wait, port_start)
            for index, candidate in enumerate(candidates)
        ]
        for future in as_completed(futures):
            result = future.result()
            records.append(result)
    records.sort(key=lambda item: (not item.get("passed", False), item.get("real_latency_ms") or 99999, item.get("quick_latency_ms") or 99999))
    working = [item for item in records if item.get("passed", False)]
    return records, working


def dedupe_by_exit_ip(results: list[dict]) -> list[dict]:
    unique: list[dict] = []
    seen: set[str] = set()
    for result in results:
        exit_ip = result.get("exit_ip")
        if exit_ip is None:
            unique.append(result)
            continue
        if exit_ip in seen:
            continue
        seen.add(exit_ip)
        unique.append(result)
    return unique


def lookup_exit_country(ip_address: str) -> str:
    return "Unknown"


def lookup_exit_country_cached(ip_address: str, cache: dict) -> str:
    if not ip_address:
        return "Unknown"
    if ip_address in cache:
        return str(cache[ip_address])
    try:
        request = Request("https://ipwho.is/%s" % ip_address, headers={"User-Agent": "AnfisaVPN/0.1"})
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8", errors="ignore"))
        if payload.get("success") and payload.get("country"):
            cache[ip_address] = str(payload.get("country"))
            return str(payload.get("country"))
    except Exception:
        pass
    cache[ip_address] = "Unknown"
    return "Unknown"


def parse_country_list(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    parts = [item.strip() for item in raw_value.split(",")]
    normalized = []
    for item in parts:
        if not item:
            continue
        upper = item.upper()
        if upper in COUNTRY_CODES:
            normalized.append(COUNTRY_CODES[upper])
        else:
            normalized.append(item.title())
    return normalized


def apply_country_filters(candidates: list[Candidate], include_countries: list[str], exclude_countries: list[str]) -> list[Candidate]:
    filtered: list[Candidate] = []
    for candidate in candidates:
        region = candidate.region
        if include_countries and region not in include_countries:
            continue
        if exclude_countries and region in exclude_countries:
            continue
        filtered.append(candidate)
    return filtered


def load_user_blacklist() -> dict:
    if USER_BLACKLIST_PATH.exists():
        try:
            return json.loads(USER_BLACKLIST_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "blocked_configs": [],
        "blocked_endpoints": [],
        "blocked_tag_substrings": [],
        "blocked_host_substrings": [],
    }


def apply_user_blacklist(candidates: list[Candidate], blacklist: dict) -> list[Candidate]:
    blocked_configs = set(blacklist.get("blocked_configs", []))
    blocked_endpoints = set(blacklist.get("blocked_endpoints", []))
    blocked_tag_substrings = [str(x).lower() for x in blacklist.get("blocked_tag_substrings", [])]
    blocked_host_substrings = [str(x).lower() for x in blacklist.get("blocked_host_substrings", [])]
    filtered: list[Candidate] = []
    for candidate in candidates:
        endpoint = f"{candidate.host}:{candidate.port}"
        lowered_tag = candidate.tag.lower()
        if candidate.raw in blocked_configs:
            continue
        if endpoint in blocked_endpoints:
            continue
        if any(part in lowered_tag for part in blocked_tag_substrings):
            continue
        if any(part in candidate.host.lower() for part in blocked_host_substrings):
            continue
        if any(part in candidate.host_header.lower() for part in blocked_host_substrings):
            continue
        if any(part in candidate.sni.lower() for part in blocked_host_substrings):
            continue
        filtered.append(candidate)
    return filtered


def is_result_blocked(result: dict, blacklist: dict) -> bool:
    blocked_configs = set(blacklist.get("blocked_configs", []))
    blocked_endpoints = set(blacklist.get("blocked_endpoints", []))
    blocked_tag_substrings = [str(x).lower() for x in blacklist.get("blocked_tag_substrings", [])]
    blocked_host_substrings = [str(x).lower() for x in blacklist.get("blocked_host_substrings", [])]
    config_text = str(result.get("config", ""))
    endpoint = str(result.get("endpoint", ""))
    tag = str(result.get("tag", "")).lower()
    if config_text in blocked_configs:
        return True
    if endpoint in blocked_endpoints:
        return True
    if any(part in tag for part in blocked_tag_substrings):
        return True
    if any(part in config_text.lower() for part in blocked_host_substrings):
        return True
    return False


def load_verified_history() -> list[dict]:
    if VERIFIED_HISTORY_PATH.exists():
        try:
            data = json.loads(VERIFIED_HISTORY_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [normalize_result_record(item) for item in data]
        except Exception:
            pass
    return []


def save_verified_history(records: list[dict]) -> None:
    VERIFIED_HISTORY_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def merge_verified_history(existing: list[dict], new_items: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for item in existing + new_items:
        endpoint = str(item.get("endpoint", ""))
        if endpoint == "":
            continue
        if not bool(item.get("recommended", False)):
            continue
        merged[endpoint] = item
    result = list(merged.values())
    result.sort(key=lambda item: item.get("effective_latency_ms", item.get("quick_latency_ms", 99999)))
    return result


def load_previous_latest() -> list[dict]:
    latest_path = RESULTS_DIR / "latest.json"
    if latest_path.exists():
        try:
            payload = json.loads(latest_path.read_text(encoding="utf-8"))
            data = payload.get("recommended_results", payload.get("displayed_results", payload.get("working", [])))
            if isinstance(data, list):
                return [normalize_result_record(item) for item in data]
        except Exception:
            pass
    return []


def annotate_result_countries(items: list[dict], geo_cache: dict) -> list[dict]:
    for item in items:
        item["exit_country"] = lookup_exit_country_cached(str(item.get("exit_ip", "")), geo_cache)
        if item.get("source_region", "Unknown") == "Unknown" and item["exit_country"] != "Unknown":
            item["region"] = item["exit_country"]
    return items


def mark_source(items: list[dict], source_kind: str) -> list[dict]:
    for item in items:
        item["source_kind"] = source_kind
    return items


def enrich_with_history_retention(
    current_items: list[dict],
    verified_history: list[dict],
    filtered_candidates: list[Candidate],
    target_min_unique: int = 4,
    previous_items: list[dict] | None = None,
    blacklist: dict | None = None,
) -> list[dict]:
    if len(current_items) >= target_min_unique:
        return current_items

    current_endpoints = {str(item.get("endpoint", "")) for item in current_items}
    current_exit_ips = {str(item.get("exit_ip", "")) for item in current_items}
    alive_endpoints = {f"{candidate.host}:{candidate.port}" for candidate in filtered_candidates}
    allow_unconfirmed_history = len(current_items) == 0
    result = list(current_items)

    if previous_items:
        for item in previous_items:
            if blacklist and is_result_blocked(item, blacklist):
                continue
            if not bool(item.get("recommended", False)):
                continue
            endpoint = str(item.get("endpoint", ""))
            exit_ip = str(item.get("exit_ip", ""))
            if endpoint in current_endpoints or exit_ip in current_exit_ips:
                continue
            retained = dict(item)
            retained["retained_from_history"] = True
            retained["retained_from_previous_latest"] = True
            result.append(retained)
            current_endpoints.add(endpoint)
            current_exit_ips.add(exit_ip)
            if len(result) >= target_min_unique:
                return result

    for item in verified_history:
        if blacklist and is_result_blocked(item, blacklist):
            continue
        if not bool(item.get("recommended", False)):
            continue
        endpoint = str(item.get("endpoint", ""))
        exit_ip = str(item.get("exit_ip", ""))
        if endpoint in current_endpoints:
            continue
        if endpoint not in alive_endpoints and not allow_unconfirmed_history:
            continue
        if exit_ip in current_exit_ips:
            continue
        retained = dict(item)
        retained["retained_from_history"] = True
        retained["retained_without_live_confirmation"] = endpoint not in alive_endpoints
        result.append(retained)
        current_endpoints.add(endpoint)
        current_exit_ips.add(exit_ip)
        if len(result) >= target_min_unique:
            break
    return result


def expand_with_non_unique_fallback(unique_items: list[dict], all_working: list[dict], target_count: int = 3) -> list[dict]:
    if len(unique_items) >= target_count:
        return unique_items
    result = list(unique_items)
    seen_configs = {str(item.get("config", "")) for item in result}
    for item in all_working:
        config_text = str(item.get("config", ""))
        if config_text in seen_configs:
            continue
        extra = dict(item)
        extra["duplicate_exit_ip"] = True
        result.append(extra)
        seen_configs.add(config_text)
        if len(result) >= target_count:
            break
    return result


def process_real_batches(
    candidates: list[Candidate],
    args,
    initial_checked: int = 0,
    stage_label: str = "real_check",
    stop_after_recommended: int = 0,
) -> tuple[list[dict], list[dict], int]:
    all_records: list[dict] = []
    all_working: list[dict] = []
    checked_total = initial_checked
    worker_count = 1 if int(args.real_workers) <= 2 else 2
    batch_size = max(1, min(3, worker_count * 2))
    next_port_start = 2550 + initial_checked * 4 + 10
    batch_index = 0
    for offset in range(0, len(candidates), batch_size):
        if should_stop():
            write_pipeline_state(status="stopped", stage="stopped", progress=0, message="Stopped by user")
            break
        batch = candidates[offset : offset + batch_size]
        batch_index += 1
        batch_completed = min(offset, len(candidates))
        write_pipeline_state(
            status="running",
            stage=stage_label,
            message="Running batch %d" % batch_index,
            checked_total=checked_total,
            progress=compute_stage_progress(40 if stage_label == "real_check_stage_1" else 72, 28 if stage_label == "real_check_stage_1" else 16, batch_completed, len(candidates)),
        )
        records, working = real_check(batch, max_workers=worker_count, port_start=next_port_start)
        next_port_start += len(batch) + 20
        time.sleep(0.7)  # let previous HiddifyCli processes fully release ports
        checked_total += len(batch)
        all_records.extend(records)
        all_working.extend(working)
        if stop_after_recommended > 0:
            unique_recommended = dedupe_by_exit_ip([item for item in all_working if item.get("recommended", False)])
            if len(unique_recommended) >= stop_after_recommended:
                _debug_log("EARLY_STOP %s after %d recommended" % (stage_label, len(unique_recommended)))
                write_pipeline_state(
                    status="running",
                    stage=stage_label,
                    message="Early stop after enough recommended proxies",
                    checked_total=checked_total,
                    fresh_recommended_total=len(unique_recommended),
                    progress=compute_stage_progress(40 if stage_label == "real_check_stage_1" else 72, 28 if stage_label == "real_check_stage_1" else 16, offset + len(batch), len(candidates)),
                )
                break
        write_pipeline_state(
            status="running",
            stage=stage_label,
            message="Finished batch %d" % batch_index,
            checked_total=checked_total,
            fresh_working_total=len(all_working),
            progress=compute_stage_progress(40 if stage_label == "real_check_stage_1" else 72, 28 if stage_label == "real_check_stage_1" else 16, offset + len(batch), len(candidates)),
        )
    return all_records, all_working, checked_total


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--countries", default="")
    parser.add_argument("--exclude-countries", default="")
    parser.add_argument("--real-limit", type=int, default=44)
    parser.add_argument("--real-workers", type=int, default=2)
    parser.add_argument("--mode", choices=["smart", "quick_recovery"], default="smart")
    args = parser.parse_args()

    ensure_dirs()
    if DEBUG_LOG_PATH.exists():
        DEBUG_LOG_PATH.unlink(missing_ok=True)
    _debug_log("=== Pipeline started ===")
    started = time.strftime("%Y-%m-%d %H:%M:%S")
    include_countries = parse_country_list(args.countries)
    exclude_countries = parse_country_list(args.exclude_countries)
    user_blacklist = load_user_blacklist()
    verified_history = load_verified_history()
    previous_latest = load_previous_latest()
    proxy_state = load_proxy_state()
    geo_cache = load_geo_cache()
    now_ts = int(time.time())

    downloaded = {"vless": 0, "trojan": 0, "vmess": 0, "ss": 0}
    all_candidates: list[Candidate] = []
    parsed_counts = {"vless": 0, "trojan": 0, "vmess": 0, "ss": 0}
    if args.mode != "quick_recovery":
        write_pipeline_state(status="running", stage="download", progress=5, message="Downloading sources", started_at=started, mode=args.mode)
        downloaded = download_sources()
        all_candidates, parsed_counts = load_candidates()
    else:
        write_pipeline_state(status="running", stage="download", progress=5, message="Preparing quick recovery", started_at=started, mode=args.mode)
    trusted_seed_candidates = load_seed_candidates(limit_per_file=12, paths=TRUSTED_SEED_FILES, source_lane="trusted_seed")
    checked_seed_candidates = load_seed_candidates(limit_per_file=18, paths=CHECKED_SEED_FILES, source_lane="checked_seed")
    checked_seed_candidates.extend(load_remote_seed_candidates(REMOTE_CHECKED_SEED_URLS, limit_per_url=40, source_lane="checked_seed"))
    write_pipeline_state(status="running", stage="quick_filter", progress=20, message="Quick filtering", downloaded_lines=downloaded)
    all_candidates = apply_user_blacklist(all_candidates, user_blacklist)
    trusted_seed_candidates = apply_user_blacklist(trusted_seed_candidates, user_blacklist)
    checked_seed_candidates = apply_user_blacklist(checked_seed_candidates, user_blacklist)
    if args.mode != "quick_recovery":
        filtered, quick_counts = asyncio.run(quick_filter(all_candidates))
        for item in filtered:
            item.source_lane = "live"
    else:
        filtered = []
        quick_counts = {"vless": 0, "trojan": 0, "vmess": 0, "ss": 0}
    trusted_seed_filtered, _ = asyncio.run(quick_filter(trusted_seed_candidates))
    checked_seed_filtered, _ = asyncio.run(quick_filter(checked_seed_candidates))
    if args.mode == "quick_recovery":
        parsed_counts = {
            "vless": len([c for c in trusted_seed_candidates + checked_seed_candidates if c.protocol == "vless"]),
            "trojan": len([c for c in trusted_seed_candidates + checked_seed_candidates if c.protocol == "trojan"]),
            "vmess": len([c for c in trusted_seed_candidates + checked_seed_candidates if c.protocol == "vmess"]),
            "ss": len([c for c in trusted_seed_candidates + checked_seed_candidates if c.protocol == "ss"]),
        }
        quick_counts = {
            "vless": len([c for c in trusted_seed_filtered + checked_seed_filtered if c.protocol == "vless"]),
            "trojan": len([c for c in trusted_seed_filtered + checked_seed_filtered if c.protocol == "trojan"]),
            "vmess": len([c for c in trusted_seed_filtered + checked_seed_filtered if c.protocol == "vmess"]),
            "ss": len([c for c in trusted_seed_filtered + checked_seed_filtered if c.protocol == "ss"]),
        }
    filtered = apply_country_filters(filtered, include_countries, exclude_countries)
    trusted_seed_filtered = apply_country_filters(trusted_seed_filtered, include_countries, exclude_countries)
    checked_seed_filtered = apply_country_filters(checked_seed_filtered, include_countries, exclude_countries)
    filtered_before_cooldown = list(filtered)
    filtered = apply_cooldown(filtered, proxy_state, now_ts)
    history_endpoints = {str(item.get("endpoint", "")) for item in verified_history}
    history_candidates = [item for item in filtered_before_cooldown if f"{item.host}:{item.port}" in history_endpoints]
    history_candidates.sort(key=lambda item: candidate_priority(item, proxy_state))
    trojan_ws_pool = limit_family_candidates([item for item in filtered if item.protocol == "trojan" and item.network == "ws" and item.security == "tls"], 2)[:50]
    trojan_other_pool = limit_family_candidates([item for item in filtered if item.protocol == "trojan" and item not in trojan_ws_pool], 2)[:25]
    vless_pool = limit_family_candidates([item for item in filtered if item.protocol == "vless"], 2)[:40]
    vmess_pool = limit_family_candidates([item for item in filtered if item.protocol == "vmess"], 2)[:35]
    ss_pool = limit_family_candidates([item for item in filtered if item.protocol == "ss"], 2)[:25]
    # Interleave protocols for diversity in real_pool (round-robin)
    protocol_pools = [trojan_ws_pool, vless_pool, vmess_pool, ss_pool, trojan_other_pool]
    interleaved: list[Candidate] = []
    max_pool_len = max((len(p) for p in protocol_pools), default=0)
    for idx in range(max_pool_len):
        for pool in protocol_pools:
            if idx < len(pool):
                interleaved.append(pool[idx])
    trusted_seed_by_proto: dict[str, list[Candidate]] = {}
    checked_seed_by_proto: dict[str, list[Candidate]] = {}
    for s in trusted_seed_filtered:
        trusted_seed_by_proto.setdefault(s.protocol, []).append(s)
    for s in checked_seed_filtered:
        checked_seed_by_proto.setdefault(s.protocol, []).append(s)
    limited_trusted_seeds: list[Candidate] = []
    for proto in ("trojan", "vless", "vmess", "ss"):
        limited_trusted_seeds.extend(trusted_seed_by_proto.get(proto, [])[:3])
    limited_checked_seeds: list[Candidate] = []
    for proto in ("trojan", "vless", "vmess", "ss"):
        limited_checked_seeds.extend(checked_seed_by_proto.get(proto, [])[:2])
    live_pool: list[Candidate] = []
    seen_pool: set[str] = set()
    for candidate in interleaved:
        endpoint = f"{candidate.host}:{candidate.port}"
        if endpoint in seen_pool:
            continue
        seen_pool.add(endpoint)
        live_pool.append(candidate)
    live_real_limit = 0 if args.mode == "quick_recovery" else min(int(args.real_limit), 12)
    real_pool = live_pool[: live_real_limit]
    seed_fallback_pool: list[Candidate] = []
    seed_seen: set[str] = set()
    for candidate in limited_trusted_seeds + limited_checked_seeds:
        endpoint = f"{candidate.host}:{candidate.port}"
        if endpoint in seed_seen:
            continue
        seed_seen.add(endpoint)
        if endpoint in seen_pool:
            continue
        seed_fallback_pool.append(candidate)
    _debug_log(
        "POOL trusted_seed=%d checked_seed=%d live=%d real_pool=%d first=%s"
        % (
            len(limited_trusted_seeds),
            len(limited_checked_seeds),
            len(live_pool),
            len(real_pool),
            ", ".join("%s:%s:%s" % (item.protocol, item.host, item.port) for item in real_pool[: min(8, len(real_pool))]),
        )
    )
    write_pipeline_state(
        status="running",
        stage="planning",
        progress=35,
        message="Prepared candidate pool",
        candidate_pool=len(live_pool),
        initial_real_pool=len(real_pool),
        live_real_limit=live_real_limit,
    )
    if args.mode == "quick_recovery":
        target_min_unique = 3
    elif args.real_limit <= 28:
        target_min_unique = 2
    else:
        target_min_unique = 3
    if real_pool:
        live_records, live_working_all, checked_total = process_real_batches(
            real_pool,
            args,
            initial_checked=0,
            stage_label="real_check_stage_1",
            stop_after_recommended=target_min_unique,
        )
    else:
        live_records, live_working_all, checked_total = [], [], 0
    all_records = list(live_records)
    fresh_unique_all = dedupe_by_exit_ip(live_working_all)
    fresh_unique_all = annotate_result_countries(fresh_unique_all, geo_cache)
    fresh_results = [dict(item) for item in fresh_unique_all]
    mark_source(fresh_results, "fresh")
    recommended_fresh_results = [dict(item) for item in fresh_results if item.get("recommended", False)]
    retained_results: list[dict] = []
    if len(recommended_fresh_results) < target_min_unique and seed_fallback_pool:
        write_pipeline_state(
            status="running",
            stage="trusted_seed_fallback",
            progress=72,
            message="Trying trusted seed fallback",
            checked_total=checked_total,
            fresh_recommended_total=len(recommended_fresh_results),
        )
        seed_extra_pool = seed_fallback_pool[: (max(6, target_min_unique * 4) if args.mode == "smart" else max(8, target_min_unique * 5))]
        seed_records, seed_working, checked_total = process_real_batches(
            seed_extra_pool,
            args,
            initial_checked=checked_total,
            stage_label="trusted_seed_fallback",
            stop_after_recommended=target_min_unique,
        )
        all_records.extend(seed_records)
        seed_unique = dedupe_by_exit_ip(seed_working)
        seed_unique = annotate_result_countries(seed_unique, geo_cache)
        retained_results = [dict(item) for item in seed_unique if item.get("recommended", False)]
        for item in retained_results:
            item["retained_from_trusted_seed"] = True
        mark_source(retained_results, "history")

    if len(recommended_fresh_results) + len(retained_results) < target_min_unique:
        write_pipeline_state(
            status="running",
            stage="history_fallback",
            progress=88,
            message="Trying final history fallback",
            checked_total=checked_total,
            fresh_recommended_total=len(recommended_fresh_results),
            retained_total=len(retained_results),
        )
        retained_combined = enrich_with_history_retention(
            list(recommended_fresh_results) + list(retained_results),
            verified_history,
            filtered,
            previous_items=previous_latest,
            blacklist=user_blacklist,
            target_min_unique=target_min_unique,
        )
        retained_results = [dict(item) for item in retained_combined if item.get("source_kind", "history") == "history" or item.get("retained_from_history") or item.get("retained_from_trusted_seed")]
        mark_source(retained_results, "history")
    if len(recommended_fresh_results) + len(retained_results) < target_min_unique:
        write_pipeline_state(
            status="running",
            stage="trusted_seed_restore",
            progress=94,
            message="Recovering trusted local seed entries",
            checked_total=checked_total,
            fresh_recommended_total=len(recommended_fresh_results),
            retained_total=len(retained_results),
        )
        trusted_seed_restore = build_unconfirmed_seed_history(
            trusted_seed_filtered,
            list(retained_results),
            target_min_unique,
            geo_cache,
        )
        retained_results = [dict(item) for item in trusted_seed_restore if item.get("source_kind", "history") == "history"]
        mark_source(retained_results, "history")
    proxy_state = update_proxy_state(proxy_state, all_records)
    save_proxy_state(proxy_state)
    recommended_results = list(recommended_fresh_results) + list(retained_results)
    displayed_results = list(recommended_results)
    displayed_results = annotate_result_countries(displayed_results, geo_cache)
    displayed_results.sort(key=lambda item: (item.get("effective_latency_ms", item.get("quick_latency_ms", 99999)), item.get("real_latency_ms", 99999)))
    save_geo_cache(geo_cache)
    save_verified_history(merge_verified_history(verified_history, recommended_fresh_results))

    fresh_passing_total = len(fresh_results)
    fresh_recommended_total = len(recommended_fresh_results)
    retained_total = len(retained_results)
    recommended_visible_total = len(displayed_results)
    all_passing_results = [dict(item) for item in dedupe_by_exit_ip([record for record in all_records if record.get("passed", False)])]
    all_passing_results = annotate_result_countries(all_passing_results, geo_cache)
    slow_hidden_total = len([item for item in all_passing_results if not item.get("recommended", False)])
    fail_reason_counts: dict[str, int] = {}
    for item in all_records:
        fail_reason = str(item.get("fail_reason", "")).strip()
        if fail_reason == "":
            continue
        fail_reason_counts[fail_reason] = int(fail_reason_counts.get(fail_reason, 0)) + 1

    output = {
        "meta": {
            "project": "Anfisa VPN",
            "started_at": started,
            "source_repo": "kort0881/vpn-vless-configs-russia",
            "mode": args.mode,
            "countries_filter": include_countries,
            "exclude_countries": exclude_countries,
            "user_blacklist_path": str(USER_BLACKLIST_PATH),
        },
        "stats": {
            "downloaded_lines": downloaded,
            "parsed_candidates": parsed_counts,
            "quick_alive": quick_counts,
            "checked_total": checked_total,
            "real_checked": checked_total,
            "fresh_passing_total": fresh_passing_total,
            "fresh_working_total": fresh_passing_total,
            "fresh_recommended_total": fresh_recommended_total,
            "slow_hidden_total": slow_hidden_total,
            "fresh_slow_total": slow_hidden_total,
            "retained_total": retained_total,
            "recommended_visible_total": recommended_visible_total,
            "visible_total": recommended_visible_total,
            "working_total": recommended_visible_total,
            "working_unique_exit_ip": len({str(item.get("exit_ip", "")) for item in displayed_results if str(item.get("exit_ip", "")) != ""}),
            "retained_from_history": retained_total,
            "recommended_count": fresh_recommended_total,
            "fail_reason_counts": fail_reason_counts,
        },
        "fresh_results": fresh_results,
        "retained_results": retained_results,
        "recommended_results": recommended_results,
        "all_passing_results": all_passing_results,
        "displayed_results": displayed_results,
        "working": displayed_results,
        "top_candidates": [asdict(item) for item in filtered[:18]],
    }

    latest_path = RESULTS_DIR / "latest.json"
    latest_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    write_pipeline_state(
        status="completed",
        stage="done",
        progress=100,
        message="Pipeline completed",
        checked_total=checked_total,
        fresh_passing_total=fresh_passing_total,
        fresh_working_total=fresh_passing_total,
        fresh_recommended_total=fresh_recommended_total,
        retained_total=retained_total,
        recommended_visible_total=recommended_visible_total,
        visible_total=recommended_visible_total,
        slow_hidden=slow_hidden_total,
    )
    print(json.dumps(output, ensure_ascii=True))


if __name__ == "__main__":
    main()
