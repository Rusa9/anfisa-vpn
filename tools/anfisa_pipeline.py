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

MINIMUM_USEFUL_TOTAL = 5
SOFT_TARGET_TOTAL = 12
EXPANSION_TARGET_TOTAL = 30
SMART_RUNTIME_BUDGET_SECONDS = 300
QUICK_RUNTIME_BUDGET_SECONDS = 120
REMAINING_SECONDS_FOR_NOISY_STAGE = 45
REMAINING_SECONDS_FOR_SOFT_EXPANSION = 75
LIVE_STAGE_STOP_TARGET = 3

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
TRUSTED_LOCAL_SEED_FILES = [
    LEGACY_SEED_DIR / "BEST_FOR_HIDDIFY_ranked.txt",
    LEGACY_SEED_DIR / "BEST_FOR_HIDDIFY.txt",
    LEGACY_SEED_DIR / "trojan_checked.txt",
    LEGACY_SEED_DIR / "vless_checked.txt",
    LEGACY_SEED_DIR / "ss_checked.txt",
    LEGACY_SEED_DIR / "vmess_checked.txt",
    LEGACY_SEED_DIR / "WORKING_UNIQUE_NOW.txt",
    LEGACY_SEED_DIR / "WORKING_NOW_TROJAN.txt",
]
LEGACY_TRUST_FILES = [
    LEGACY_SEED_DIR / "REAL_WORKING.txt",
    LEGACY_SEED_DIR / "REAL_WORKING_UNIQUE_BY_IP.txt",
]
REMOTE_CHECKED_SEED_URLS = [
    "https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/BLACK_VLESS_RUS_mobile.txt",
    "https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/BLACK_SS+All_RUS.txt",
    "https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/Vless-Reality-White-Lists-Rus-Mobile.txt",
    "https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/Vless-Reality-White-Lists-Rus-Mobile-2.txt",
]
SOURCE_URLS = {
    "vless": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt",
    "trojan": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/trojan.txt",
    "vmess": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vmess.txt",
    "ss": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/ss.txt",
}
RU_SNI_SOURCE_URLS = {
    "vless_ru_sni": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/vless_ru.txt",
    "trojan_ru_sni": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/trojan_ru.txt",
    "vmess_ru_sni": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/vmess_ru.txt",
    "ss_ru_sni": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/ss_ru.txt",
}
NOISY_PROTOCOL_URLS = {
    "vless_epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vless.txt",
    "trojan_epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/trojan.txt",
    "vmess_epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vmess.txt",
    "ss_epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/ss.txt",
}
NOISY_MIXED_URLS = [
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt",
    "https://raw.githubusercontent.com/ippscan/v2rayNEW-configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/ippscan/v2rayNEW-configs/main/Sub2.txt",
]
PROTOCOL_PRIORITY = {"trojan": 24, "vless": 22, "vmess": 12, "ss": 8}
TLS_LIKE_PORTS = {443, 8443, 2053, 2083, 2087, 2096}
LOW_VALUE_PORTS = {80, 8080, 8880}
SOURCE_LANE_WEIGHTS = {
    "trusted_checked": 90,
    "trusted_local_seed": 80,
    "live_primary": 70,
    "noisy_expansion": 45,
}
PROTOCOL_TIMING: dict[tuple[str, str, str], dict] = {
    ("trojan", "ws", "tls"):     {"startup_wait": 3.8, "timeout": 7},
    ("trojan", "tcp", "tls"):    {"startup_wait": 3.5, "timeout": 7},
    ("trojan", "grpc", "tls"):   {"startup_wait": 4.0, "timeout": 7},
    ("vless", "tcp", "reality"): {"startup_wait": 4.5, "timeout": 8},
    ("vless", "ws", "reality"):  {"startup_wait": 4.6, "timeout": 8},
    ("vless", "grpc", "reality"):{"startup_wait": 4.8, "timeout": 8},
    ("vless", "tcp", "tls"):     {"startup_wait": 3.8, "timeout": 7},
    ("vless", "ws", "tls"):      {"startup_wait": 4.0, "timeout": 7},
    ("vless", "grpc", "tls"):    {"startup_wait": 4.2, "timeout": 7},
    ("vmess", "ws", "tls"):      {"startup_wait": 4.0, "timeout": 8},
    ("vmess", "tcp", "tls"):     {"startup_wait": 3.8, "timeout": 8},
    ("vmess", "tcp", ""):        {"startup_wait": 3.6, "timeout": 7},
    ("vmess", "ws", ""):         {"startup_wait": 3.8, "timeout": 8},
    ("vmess", "grpc", "tls"):    {"startup_wait": 4.1, "timeout": 8},
    ("vmess", "http", ""):       {"startup_wait": 3.8, "timeout": 7},
}
PROTOCOL_TIMING_DEFAULT = {"startup_wait": 4.0, "timeout": 7}
RECOMMENDED_MAX_MS = 700
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
    source_name: str = ""


@dataclass(frozen=True)
class RemoteSourceSpec:
    name: str
    url: str
    protocol_hint: Optional[str]
    source_lane: str
    max_candidates: int


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
        if (
            f"{code}-" in upper
            or f" {code} " in upper
            or f"_{code}_" in upper
            or upper.startswith(code + "-")
            or upper.startswith(code + " ")
            or upper.startswith("[" + code + "]")
            or upper.startswith(code + "|")
            or f"({code})" in upper
        ):
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


def infer_protocol(line: str) -> str:
    if line.startswith("trojan://"):
        return "trojan"
    if line.startswith("vless://"):
        return "vless"
    if line.startswith("vmess://"):
        return "vmess"
    if line.startswith("ss://"):
        return "ss"
    return ""


def build_primary_source_specs() -> list[RemoteSourceSpec]:
    specs: list[RemoteSourceSpec] = []
    for name, url in SOURCE_URLS.items():
        specs.append(RemoteSourceSpec(name=name, url=url, protocol_hint=name, source_lane="live_primary", max_candidates=180))
    for name, url in RU_SNI_SOURCE_URLS.items():
        protocol_hint = name.split("_", 1)[0]
        specs.append(RemoteSourceSpec(name=name, url=url, protocol_hint=protocol_hint, source_lane="live_primary", max_candidates=120))
    return specs


def build_trusted_checked_source_specs() -> list[RemoteSourceSpec]:
    return [
        RemoteSourceSpec(name="igareck_black_vless_mobile", url=REMOTE_CHECKED_SEED_URLS[0], protocol_hint=None, source_lane="trusted_checked", max_candidates=60),
        RemoteSourceSpec(name="igareck_black_ss_all", url=REMOTE_CHECKED_SEED_URLS[1], protocol_hint=None, source_lane="trusted_checked", max_candidates=60),
        RemoteSourceSpec(name="igareck_reality_mobile_1", url=REMOTE_CHECKED_SEED_URLS[2], protocol_hint=None, source_lane="trusted_checked", max_candidates=60),
        RemoteSourceSpec(name="igareck_reality_mobile_2", url=REMOTE_CHECKED_SEED_URLS[3], protocol_hint=None, source_lane="trusted_checked", max_candidates=60),
    ]


def build_noisy_source_specs() -> list[RemoteSourceSpec]:
    specs: list[RemoteSourceSpec] = []
    for name, url in NOISY_PROTOCOL_URLS.items():
        protocol_hint = name.split("_", 1)[0]
        specs.append(RemoteSourceSpec(name=name, url=url, protocol_hint=protocol_hint, source_lane="noisy_expansion", max_candidates=40))
    for index, url in enumerate(NOISY_MIXED_URLS, start=1):
        specs.append(RemoteSourceSpec(name="noisy_mixed_%d" % index, url=url, protocol_hint=None, source_lane="noisy_expansion", max_candidates=20))
    return specs


def protocol_stat_bucket() -> dict[str, int]:
    return {"vless": 0, "trojan": 0, "vmess": 0, "ss": 0}


def download_source_text(name: str, url: str, timeout: int = 20) -> tuple[str, int]:
    cache_path = RAW_DIR / ("%s.txt" % name)
    try:
        request = Request(url, headers={"User-Agent": "AnfisaVPN/0.3"})
        with urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="ignore")
        cache_path.write_text(text, encoding="utf-8")
    except Exception as exc:
        if not cache_path.exists():
            _debug_log("download %s failed (%s), no cache available" % (name, exc))
            return "", 0
        text = cache_path.read_text(encoding="utf-8", errors="ignore")
        _debug_log("download %s failed (%s), using cached source" % (name, exc))
    return text, len([line for line in text.splitlines() if normalize_line(line)])


def parse_candidates_from_lines(
    lines: list[str],
    protocol_hint: Optional[str],
    max_candidates: int,
    source_lane: str,
    source_name: str,
) -> tuple[list[Candidate], dict[str, int]]:
    parsed_counts = protocol_stat_bucket()
    candidates: list[Candidate] = []
    seen_raw: set[str] = set()
    for raw in lines:
        line = normalize_line(raw)
        if not line or line in seen_raw:
            continue
        protocol = protocol_hint or infer_protocol(line)
        if protocol == "":
            continue
        candidate = parse_basic(line, protocol)
        if candidate is None:
            continue
        candidate.source_lane = source_lane
        candidate.source_name = source_name
        seen_raw.add(line)
        candidates.append(candidate)
        parsed_counts[protocol] += 1
        if len(candidates) >= max_candidates:
            break
    return candidates, parsed_counts


def load_remote_candidates(specs: list[RemoteSourceSpec]) -> tuple[list[Candidate], dict[str, int], dict[str, int]]:
    all_candidates: list[Candidate] = []
    downloaded_counts = protocol_stat_bucket()
    parsed_counts = protocol_stat_bucket()
    for spec in specs:
        text, downloaded_lines = download_source_text(spec.name, spec.url, timeout=25)
        if text == "":
            continue
        if spec.protocol_hint is not None:
            downloaded_counts[spec.protocol_hint] += downloaded_lines
        lines = text.splitlines()
        source_candidates, source_parsed = parse_candidates_from_lines(
            lines,
            spec.protocol_hint,
            spec.max_candidates,
            spec.source_lane,
            spec.name,
        )
        all_candidates.extend(source_candidates)
        for protocol, count in source_parsed.items():
            parsed_counts[protocol] += int(count)
            if spec.protocol_hint is None:
                downloaded_counts[protocol] += int(count)
    return dedupe_candidates(all_candidates), downloaded_counts, parsed_counts


def load_local_seed_candidates() -> tuple[list[Candidate], dict[str, int]]:
    candidates: list[Candidate] = []
    parsed_counts = protocol_stat_bucket()
    file_limits = {
        "BEST_FOR_HIDDIFY_ranked.txt": 40,
        "BEST_FOR_HIDDIFY.txt": 40,
        "trojan_checked.txt": 25,
        "vless_checked.txt": 25,
        "ss_checked.txt": 25,
        "vmess_checked.txt": 25,
        "WORKING_UNIQUE_NOW.txt": 12,
        "WORKING_NOW_TROJAN.txt": 12,
        "REAL_WORKING.txt": 0,
        "REAL_WORKING_UNIQUE_BY_IP.txt": 0,
    }
    for path in TRUSTED_LOCAL_SEED_FILES + LEGACY_TRUST_FILES:
        if not path.exists():
            continue
        if path.stat().st_size <= 0:
            continue
        limit = int(file_limits.get(path.name, 20))
        if limit <= 0:
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        source_candidates, source_parsed = parse_candidates_from_lines(
            lines,
            None,
            limit,
            "trusted_local_seed",
            path.name,
        )
        candidates.extend(source_candidates)
        for protocol, count in source_parsed.items():
            parsed_counts[protocol] += int(count)
    return dedupe_candidates(candidates), parsed_counts


def load_history_recheck_candidates(history_items: list[dict], source_lane: str = "verified_history") -> list[Candidate]:
    candidates: list[Candidate] = []
    for item in history_items:
        raw = normalize_line(str(item.get("config", "")))
        if raw == "":
            continue
        protocol = infer_protocol(raw)
        if protocol == "":
            continue
        candidate = parse_basic(raw, protocol)
        if candidate is None:
            continue
        candidate.source_lane = source_lane
        candidate.source_name = "history"
        quick_ms = item.get("quick_latency_ms", None)
        try:
            if quick_ms is not None:
                candidate.quick_latency_ms = int(quick_ms)
        except Exception:
            candidate.quick_latency_ms = None
        candidate.score = max(candidate.score, int(item.get("score", 0)))
        if str(item.get("region", "")) not in {"", "Unknown"}:
            candidate.region = str(item.get("region"))
        candidates.append(candidate)
    return dedupe_candidates(candidates)


def dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    deduped: list[Candidate] = []
    seen_raw: set[str] = set()
    seen_endpoint: set[str] = set()
    for candidate in candidates:
        endpoint = "%s|%s:%s" % (candidate.protocol, candidate.host, candidate.port)
        if candidate.raw in seen_raw:
            continue
        if endpoint in seen_endpoint:
            continue
        seen_raw.add(candidate.raw)
        seen_endpoint.add(endpoint)
        deduped.append(candidate)
    return deduped


def build_unconfirmed_seed_history(
    trusted_candidates: list[Candidate],
    current_items: list[dict],
    target_min_unique: int,
    geo_cache: dict,
) -> list[dict]:
    result = list(current_items)
    if len(result) >= target_min_unique:
        return annotate_result_countries(result, geo_cache)
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
            "source_lane": "seed_unconfirmed",
            "verification_tier": "seed_unconfirmed",
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
    if candidate.source_lane == "trusted_checked" and candidate.protocol == "vless" and candidate.security in {"", "none"} and candidate.network == "ws":
        score += 26
    if candidate.source_lane == "trusted_checked" and candidate.protocol == "trojan" and candidate.network == "ws":
        score += 8
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
    if candidate.source_lane == "trusted_checked":
        score += 12
    elif candidate.source_lane == "trusted_local_seed":
        score += 10
    elif candidate.source_lane == "live_primary":
        score += 6

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


def sample_proxy_latency(proxy_port: int, timeout: int, url: str, attempts: int = 2, pause_sec: float = 0.2) -> tuple[bool, Optional[int]]:
    samples: list[int] = []
    ok_any = False
    for attempt in range(attempts):
        ok, total_ms = curl_url_ok(proxy_port, timeout, url)
        if ok:
            ok_any = True
            if total_ms is not None:
                samples.append(int(total_ms))
        if attempt < attempts - 1:
            time.sleep(pause_sec)
    if not ok_any:
        return False, None
    return True, min(samples) if samples else None


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
    baseline = real_latency_ms if real_latency_ms is not None else quick_latency_ms
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
    if real_latency_ms is not None:
        return int(real_latency_ms)
    if quick_latency_ms is not None:
        return int(quick_latency_ms)
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
    lane_weight = SOURCE_LANE_WEIGHTS.get(candidate.source_lane, 0)
    return (-lane_weight, -trust, -candidate.score, candidate.quick_latency_ms or 99999)


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


def summarize_candidates(candidates: list[Candidate]) -> dict[str, int]:
    counts = protocol_stat_bucket()
    for candidate in candidates:
        counts[candidate.protocol] = int(counts.get(candidate.protocol, 0)) + 1
    return counts


def build_protocol_balanced_pool(
    candidates: list[Candidate],
    total_limit: int,
    per_protocol_limit: int,
    protocol_order: tuple[str, ...] = ("vless", "trojan", "ss", "vmess"),
) -> list[Candidate]:
    groups: dict[str, list[Candidate]] = {protocol: [] for protocol in protocol_order}
    for candidate in candidates:
        groups.setdefault(candidate.protocol, []).append(candidate)
    ordered: list[Candidate] = []
    per_protocol_counts: dict[str, int] = {}
    index = 0
    max_len = max((len(items) for items in groups.values()), default=0)
    while len(ordered) < total_limit and index < max_len:
        progressed = False
        for protocol in protocol_order:
            items = groups.get(protocol, [])
            if index >= len(items):
                continue
            if per_protocol_counts.get(protocol, 0) >= per_protocol_limit:
                continue
            ordered.append(items[index])
            per_protocol_counts[protocol] = int(per_protocol_counts.get(protocol, 0)) + 1
            progressed = True
            if len(ordered) >= total_limit:
                break
        if not progressed:
            break
        index += 1
    return ordered


def keep_release_protocols(candidates: list[Candidate]) -> list[Candidate]:
    return [candidate for candidate in candidates if candidate.protocol in {"vless", "trojan"}]


def runtime_budget_seconds(mode: str) -> int:
    return QUICK_RUNTIME_BUDGET_SECONDS if mode == "quick_recovery" else SMART_RUNTIME_BUDGET_SECONDS


def runtime_remaining_seconds(started_monotonic: float, mode: str) -> int:
    elapsed = int(time.perf_counter() - started_monotonic)
    return max(0, runtime_budget_seconds(mode) - elapsed)


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


def cleanup_stale_hiddify_cli() -> None:
    try:
        subprocess.run(
            ["taskkill", "/IM", "HiddifyCli.exe", "/F", "/T"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except Exception:
        pass
    time.sleep(0.8)


def read_tail_text(path: Path, max_chars: int = 600) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


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

    run_dir = TEMP_DIR / f"run_{index}"
    run_dir.mkdir(parents=True, exist_ok=True)
    for leftover in ("current-config.json", "clash.db", "box.log", "app.log"):
        try:
            (run_dir / leftover).unlink(missing_ok=True)
        except Exception:
            pass

    config_path = run_dir / f"candidate_{index}.json"
    config_path.write_text(json.dumps({"outbounds": [outbound]}, ensure_ascii=False, indent=2), encoding="utf-8")
    proxy_port = port_start + index
    dns_port = 16450 + index + 1
    clash_api_port = 6756 + index + 1
    runtime_log_path = run_dir / f"hiddify_runtime_{index}.log"

    def attempt_once() -> dict:
        log_handle = open(runtime_log_path, "w", encoding="utf-8", errors="ignore")
        proc = subprocess.Popen(
            [
                str(HIDDIFY_CLI),
                "run",
                "-c",
                str(config_path),
                "-D",
                str(run_dir),
                "--in-proxy-port",
                str(proxy_port),
                "--web-port",
                str(clash_api_port),
                "--dns-direct",
                "1.1.1.1",
                "--dns-remote",
                "1.1.1.1",
                "--fragment-size",
                "2-4",
                "--fragment-sleep",
                "2-4",
                "--log",
                "warn",
            ],
            cwd=str(run_dir),
            stdout=log_handle,
            stderr=subprocess.STDOUT,
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
                runtime_tail = read_tail_text(runtime_log_path)
                if runtime_tail != "":
                    _debug_log(f"RUNTIME #{index} {runtime_tail}")
                _debug_log(f"FAIL #{index} port_not_ready on :{proxy_port}")
                return {**fail_base, "reason": "port_not_ready", "fail_reason": "port_not_ready"}
            _debug_log(f"PORT #{index} ready on :{proxy_port}, waiting 0.8s grace")
            time.sleep(0.8)
            probe_timeout = min(effective_timeout, 2)
            cloudflare_ok, cloudflare_ms = sample_proxy_latency(proxy_port, probe_timeout, "http://cp.cloudflare.com/", attempts=2, pause_sec=0.15)
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
            passed = bool(cloudflare_ok or exit_ip)
            recommended = passed and is_recommended_record(
                {
                    "quick_latency_ms": candidate.quick_latency_ms,
                    "real_latency_ms": real_latency_ms,
                }
            )
            fail_reason = "" if passed else classify_fail_reason(cloudflare_ok, exit_ip, candidate.quick_latency_ms, candidate)
            if not passed:
                runtime_tail = read_tail_text(runtime_log_path)
                if runtime_tail != "":
                    _debug_log(f"RUNTIME #{index} {runtime_tail}")
            stored_quick_ms = candidate.quick_latency_ms
            if real_latency_ms is not None and stored_quick_ms is not None:
                stored_quick_ms = min(int(stored_quick_ms), int(real_latency_ms))
            elif real_latency_ms is not None:
                stored_quick_ms = int(real_latency_ms)
            return {
                "config": candidate.raw,
                "protocol": candidate.protocol,
                "region": candidate.region,
                "source_region": candidate.region,
                "tag": candidate.tag,
                "endpoint": f"{candidate.host}:{candidate.port}",
                "family_key": family_key_from_candidate(candidate),
                "exit_ip": exit_ip,
                "quick_latency_ms": stored_quick_ms,
                "real_latency_ms": real_latency_ms,
                "effective_latency_ms": effective_latency_ms(stored_quick_ms, real_latency_ms),
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
            log_handle.close()

    result = attempt_once()
    passed = result.get("passed", False)
    reason = result.get("reason", "?")
    _debug_log(f"RESULT #{index} lane={candidate.source_lane} passed={passed} reason={reason} fail_reason={result.get('fail_reason','')} latency={result.get('real_latency_ms')}")
    if not passed:
        quick_ms = candidate.quick_latency_ms or 9999
        if quick_ms <= 260:
            _debug_log(f"RETRY #{index} (quick={quick_ms}ms)")
            time.sleep(0.6)
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
                filtered: list[dict] = []
                for item in data:
                    record = normalize_result_record(item)
                    if not bool(record.get("passed", False)):
                        continue
                    if str(record.get("verification_tier", "")) == "seed_unconfirmed":
                        continue
                    filtered.append(record)
                return filtered
        except Exception:
            pass
    return []


def annotate_result_countries(items: list[dict], geo_cache: dict) -> list[dict]:
    for item in items:
        exit_country = lookup_exit_country_cached(str(item.get("exit_ip", "")), geo_cache)
        if exit_country == "Unknown":
            fallback_region = str(item.get("region", item.get("source_region", "Unknown")))
            if fallback_region != "" and fallback_region != "Unknown":
                exit_country = fallback_region
        item["exit_country"] = exit_country
        if item.get("source_region", "Unknown") == "Unknown" and item["exit_country"] != "Unknown":
            item["region"] = item["exit_country"]
    return items


def mark_source(
    items: list[dict],
    source_kind: str,
    source_lane: Optional[str] = None,
    verification_tier: Optional[str] = None,
) -> list[dict]:
    for item in items:
        item["source_kind"] = source_kind
        if source_lane is not None:
            item["source_lane"] = source_lane
        else:
            item["source_lane"] = str(item.get("source_lane", source_kind))
        if verification_tier is not None:
            item["verification_tier"] = verification_tier
        elif "verification_tier" not in item:
            item["verification_tier"] = "history_retained" if source_kind == "history" else "live_confirmed"
    return items


def enrich_with_history_retention(
    current_items: list[dict],
    verified_history: list[dict],
    filtered_candidates: list[Candidate],
    target_min_unique: int = 4,
    previous_items: list[dict] | None = None,
    blacklist: dict | None = None,
    failed_endpoints: set[str] | None = None,
) -> list[dict]:
    if len(current_items) >= target_min_unique:
        return current_items

    current_endpoints = {str(item.get("endpoint", "")) for item in current_items}
    current_exit_ips = {str(item.get("exit_ip", "")) for item in current_items}
    alive_endpoints = {f"{candidate.host}:{candidate.port}" for candidate in filtered_candidates}
    blocked_failed = failed_endpoints or set()
    result = list(current_items)

    if previous_items:
        for item in previous_items:
            if blacklist and is_result_blocked(item, blacklist):
                continue
            if not bool(item.get("passed", False)):
                continue
            if str(item.get("verification_tier", "")) == "seed_unconfirmed":
                continue
            if not bool(item.get("recommended", False)):
                continue
            endpoint = str(item.get("endpoint", ""))
            exit_ip = str(item.get("exit_ip", ""))
            if endpoint in blocked_failed:
                continue
            if endpoint not in alive_endpoints:
                continue
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
        if not bool(item.get("passed", False)):
            continue
        if not bool(item.get("recommended", False)):
            continue
        endpoint = str(item.get("endpoint", ""))
        exit_ip = str(item.get("exit_ip", ""))
        if endpoint in blocked_failed:
            continue
        if endpoint in current_endpoints:
            continue
        if endpoint not in alive_endpoints:
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


def extract_visible_confirmed(results: list[dict], geo_cache: dict) -> list[dict]:
    unique = dedupe_by_exit_ip(results)
    unique = annotate_result_countries(unique, geo_cache)
    return [dict(item) for item in unique if item.get("recommended", False)]


def result_sort_key(item: dict) -> tuple:
    tier_priority = {
        "live_confirmed": 0,
        "seed_confirmed": 1,
        "history_retained": 2,
        "seed_unconfirmed": 3,
    }
    return (
        tier_priority.get(str(item.get("verification_tier", "")), 9),
        int(item.get("effective_latency_ms", item.get("quick_latency_ms", 99999)) or 99999),
        int(item.get("score", 0)) * -1,
    )


def dedupe_results_for_display(results: list[dict]) -> list[dict]:
    ordered = sorted([dict(item) for item in results], key=result_sort_key)
    seen_endpoints: set[str] = set()
    seen_exit_ips: set[str] = set()
    deduped: list[dict] = []
    for item in ordered:
        endpoint = str(item.get("endpoint", ""))
        exit_ip = str(item.get("exit_ip", ""))
        if endpoint != "" and endpoint in seen_endpoints:
            continue
        if exit_ip != "" and exit_ip in seen_exit_ips:
            continue
        deduped.append(item)
        if endpoint != "":
            seen_endpoints.add(endpoint)
        if exit_ip != "":
            seen_exit_ips.add(exit_ip)
    return deduped


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
    started_monotonic = time.perf_counter()
    include_countries = parse_country_list(args.countries)
    exclude_countries = parse_country_list(args.exclude_countries)
    user_blacklist = load_user_blacklist()
    verified_history = load_verified_history()
    previous_latest = load_previous_latest()
    proxy_state = load_proxy_state()
    geo_cache = load_geo_cache()
    now_ts = int(time.time())

    downloaded = protocol_stat_bucket()
    parsed_counts = protocol_stat_bucket()
    quick_counts = protocol_stat_bucket()

    def merge_bucket(target: dict[str, int], extra: dict[str, int]) -> None:
        for protocol, count in extra.items():
            target[protocol] = int(target.get(protocol, 0)) + int(count)

    def prepare_candidates(candidates: list[Candidate]) -> tuple[list[Candidate], dict[str, int]]:
        cleaned = dedupe_candidates(apply_user_blacklist(candidates, user_blacklist))
        cleaned = apply_country_filters(cleaned, include_countries, exclude_countries)
        cleaned = [candidate for candidate in cleaned if build_hiddify_outbound(candidate) is not None]
        if not cleaned:
            return [], protocol_stat_bucket()
        filtered_candidates, quick_stats = asyncio.run(quick_filter(cleaned))
        filtered_candidates = apply_cooldown(filtered_candidates, proxy_state, now_ts)
        return filtered_candidates, quick_stats

    if args.mode != "quick_recovery":
        write_pipeline_state(status="running", stage="download", progress=5, message="Downloading staged sources", started_at=started, mode=args.mode)
        live_candidates_raw, live_downloaded, live_parsed = load_remote_candidates(build_primary_source_specs())
        merge_bucket(downloaded, live_downloaded)
        merge_bucket(parsed_counts, live_parsed)
    else:
        write_pipeline_state(status="running", stage="download", progress=5, message="Preparing quick recovery", started_at=started, mode=args.mode)
        live_candidates_raw = []

    trusted_checked_raw, checked_downloaded, checked_parsed = load_remote_candidates(build_trusted_checked_source_specs())
    trusted_local_raw, local_parsed = load_local_seed_candidates()
    merge_bucket(downloaded, checked_downloaded)
    merge_bucket(parsed_counts, checked_parsed)
    merge_bucket(parsed_counts, local_parsed)

    write_pipeline_state(status="running", stage="quick_filter", progress=20, message="Quick filtering staged pools", downloaded_lines=downloaded)

    live_filtered, live_quick = prepare_candidates(live_candidates_raw)
    trusted_checked_filtered, checked_quick = prepare_candidates(trusted_checked_raw)
    trusted_local_filtered, local_quick = prepare_candidates(trusted_local_raw)
    merge_bucket(quick_counts, live_quick)
    merge_bucket(quick_counts, checked_quick)
    merge_bucket(quick_counts, local_quick)

    live_filtered = keep_release_protocols(live_filtered)
    trusted_checked_filtered = keep_release_protocols(trusted_checked_filtered)
    trusted_local_filtered = keep_release_protocols(trusted_local_filtered)

    combined_filtered_candidates = dedupe_candidates(list(live_filtered) + list(trusted_checked_filtered) + list(trusted_local_filtered))
    live_pool = build_protocol_balanced_pool(limit_family_candidates(live_filtered, 2), min(int(args.real_limit), 6), 3)
    trusted_checked_pool = build_protocol_balanced_pool(limit_family_candidates(trusted_checked_filtered, 2), 32 if args.mode == "quick_recovery" else 32, 10 if args.mode == "quick_recovery" else 10)
    trusted_local_pool = build_protocol_balanced_pool(limit_family_candidates(trusted_local_filtered, 2), 8, 3)

    _debug_log(
        "POOL live=%d checked=%d local=%d first_live=%s"
        % (
            len(live_pool),
            len(trusted_checked_pool),
            len(trusted_local_pool),
            ", ".join("%s:%s:%s" % (item.protocol, item.host, item.port) for item in live_pool[: min(6, len(live_pool))]),
        )
    )
    write_pipeline_state(
        status="running",
        stage="planning",
        progress=35,
        message="Prepared staged candidate pools",
        candidate_pool=len(combined_filtered_candidates),
        initial_real_pool=len(live_pool),
    )

    cleanup_stale_hiddify_cli()

    all_records: list[dict] = []
    fresh_results: list[dict] = []
    seed_confirmed_results: list[dict] = []
    history_confirmed_results: list[dict] = []
    retained_history_results: list[dict] = []
    unconfirmed_seed_results: list[dict] = []
    checked_total = 0
    confirmed_visible: list[dict] = []

    history_recheck_raw = load_history_recheck_candidates(previous_latest + verified_history)
    history_recheck_filtered, history_recheck_quick = prepare_candidates(history_recheck_raw)
    history_recheck_filtered = keep_release_protocols(history_recheck_filtered)
    merge_bucket(quick_counts, history_recheck_quick)
    history_recheck_pool = build_protocol_balanced_pool(limit_family_candidates(history_recheck_filtered, 1), 8, 4, ("trojan", "vless"))

    if history_recheck_pool and runtime_remaining_seconds(started_monotonic, args.mode) > 20:
        write_pipeline_state(
            status="running",
            stage="history_recheck",
            progress=46,
            message="Rechecking last confirmed proxies first",
            checked_total=checked_total,
            fresh_recommended_total=len(confirmed_visible),
        )
        history_records, history_working, checked_total = process_real_batches(
            history_recheck_pool,
            args,
            initial_checked=checked_total,
            stage_label="history_recheck",
            stop_after_recommended=max(0, MINIMUM_USEFUL_TOTAL - len(confirmed_visible)),
        )
        all_records.extend(history_records)
        stage_history = extract_visible_confirmed(history_working, geo_cache)
        mark_source(stage_history, "history", source_lane="verified_history", verification_tier="history_retained")
        history_confirmed_results.extend(stage_history)
        confirmed_visible = [dict(item) for item in dedupe_by_exit_ip(confirmed_visible + stage_history)]

    if len(confirmed_visible) < SOFT_TARGET_TOTAL and trusted_checked_pool and runtime_remaining_seconds(started_monotonic, args.mode) > 30:
        write_pipeline_state(
            status="running",
            stage="trusted_checked",
            progress=72,
            message="Trying trusted checked pool",
            checked_total=checked_total,
            fresh_recommended_total=len(confirmed_visible),
        )
        checked_records, checked_working, checked_total = process_real_batches(
            trusted_checked_pool,
            args,
            initial_checked=checked_total,
            stage_label="trusted_checked",
            stop_after_recommended=max(0, MINIMUM_USEFUL_TOTAL - len(confirmed_visible)),
        )
        all_records.extend(checked_records)
        stage_checked = extract_visible_confirmed(checked_working, geo_cache)
        mark_source(stage_checked, "history", verification_tier="seed_confirmed")
        seed_confirmed_results.extend(stage_checked)
        confirmed_visible = [dict(item) for item in dedupe_by_exit_ip(confirmed_visible + stage_checked)]

    if live_pool and len(confirmed_visible) < MINIMUM_USEFUL_TOTAL:
        live_records, live_working_all, checked_total = process_real_batches(
            live_pool,
            args,
            initial_checked=checked_total,
            stage_label="real_check_stage_1",
            stop_after_recommended=max(0, LIVE_STAGE_STOP_TARGET - len(confirmed_visible)),
        )
        all_records.extend(live_records)
        stage_fresh = extract_visible_confirmed(live_working_all, geo_cache)
        mark_source(stage_fresh, "fresh", verification_tier="live_confirmed")
        fresh_results.extend(stage_fresh)
        confirmed_visible = [dict(item) for item in dedupe_by_exit_ip(confirmed_visible + stage_fresh)]

    if len(confirmed_visible) < SOFT_TARGET_TOTAL and trusted_local_pool and runtime_remaining_seconds(started_monotonic, args.mode) > 30:
        write_pipeline_state(
            status="running",
            stage="trusted_local_seed",
            progress=78,
            message="Trying trusted local seed pool",
            checked_total=checked_total,
            fresh_recommended_total=len(confirmed_visible),
        )
        local_records, local_working, checked_total = process_real_batches(
            trusted_local_pool,
            args,
            initial_checked=checked_total,
            stage_label="trusted_local_seed",
            stop_after_recommended=max(0, MINIMUM_USEFUL_TOTAL - len(confirmed_visible)),
        )
        all_records.extend(local_records)
        stage_local = extract_visible_confirmed(local_working, geo_cache)
        mark_source(stage_local, "history", verification_tier="seed_confirmed")
        seed_confirmed_results.extend(stage_local)
        confirmed_visible = [dict(item) for item in dedupe_by_exit_ip(confirmed_visible + stage_local)]

    noisy_filtered: list[Candidate] = []
    if (
        args.mode != "quick_recovery"
        and len(confirmed_visible) < MINIMUM_USEFUL_TOTAL
        and runtime_remaining_seconds(started_monotonic, args.mode) >= REMAINING_SECONDS_FOR_NOISY_STAGE
    ) or (
        args.mode != "quick_recovery"
        and len(confirmed_visible) < SOFT_TARGET_TOTAL
        and runtime_remaining_seconds(started_monotonic, args.mode) >= REMAINING_SECONDS_FOR_SOFT_EXPANSION
    ):
        write_pipeline_state(
            status="running",
            stage="noisy_expansion_download",
            progress=82,
            message="Expanding into noisy live pools",
            checked_total=checked_total,
            fresh_recommended_total=len(confirmed_visible),
        )
        noisy_candidates_raw, noisy_downloaded, noisy_parsed = load_remote_candidates(build_noisy_source_specs())
        merge_bucket(downloaded, noisy_downloaded)
        merge_bucket(parsed_counts, noisy_parsed)
        noisy_filtered, noisy_quick = prepare_candidates(noisy_candidates_raw)
        merge_bucket(quick_counts, noisy_quick)
        combined_filtered_candidates = dedupe_candidates(combined_filtered_candidates + noisy_filtered)
        noisy_pool = build_protocol_balanced_pool(limit_family_candidates(noisy_filtered, 2), 12, 4)
        if noisy_pool:
            noisy_records, noisy_working, checked_total = process_real_batches(
                noisy_pool,
                args,
                initial_checked=checked_total,
                stage_label="noisy_expansion",
                stop_after_recommended=max(0, SOFT_TARGET_TOTAL - len(confirmed_visible)),
            )
            all_records.extend(noisy_records)
            stage_noisy = extract_visible_confirmed(noisy_working, geo_cache)
            mark_source(stage_noisy, "fresh", verification_tier="live_confirmed")
            fresh_results.extend(stage_noisy)
            confirmed_visible = [dict(item) for item in dedupe_by_exit_ip(confirmed_visible + stage_noisy)]

    history_target = max(len(confirmed_visible), SOFT_TARGET_TOTAL)
    failed_endpoints = {
        str(item.get("endpoint", ""))
        for item in all_records
        if str(item.get("endpoint", "")) != "" and not bool(item.get("passed", False))
    }
    retained_combined = enrich_with_history_retention(
        list(confirmed_visible),
        verified_history,
        combined_filtered_candidates,
        target_min_unique=history_target,
        previous_items=previous_latest,
        blacklist=user_blacklist,
        failed_endpoints=failed_endpoints,
    )
    confirmed_endpoints = {str(item.get("endpoint", "")) for item in confirmed_visible}
    retained_history_results = [dict(item) for item in retained_combined if str(item.get("endpoint", "")) not in confirmed_endpoints]
    mark_source(retained_history_results, "history", source_lane="verified_history", verification_tier="history_retained")

    visible_with_history = list(confirmed_visible) + list(retained_history_results)
    if args.mode == "quick_recovery" and len(visible_with_history) < SOFT_TARGET_TOTAL:
        write_pipeline_state(
            status="running",
            stage="trusted_seed_restore",
            progress=94,
            message="Recovering unconfirmed trusted seeds",
            checked_total=checked_total,
            fresh_recommended_total=len(fresh_results),
            retained_total=len(retained_history_results),
        )
        restored = build_unconfirmed_seed_history(
            trusted_local_filtered,
            list(visible_with_history),
            SOFT_TARGET_TOTAL,
            geo_cache,
        )
        visible_endpoints = {str(item.get("endpoint", "")) for item in visible_with_history}
        unconfirmed_seed_results = [
            dict(item)
            for item in restored
            if str(item.get("endpoint", "")) not in visible_endpoints and bool(item.get("recommended", False))
        ]
        mark_source(unconfirmed_seed_results, "history", source_lane="seed_unconfirmed", verification_tier="seed_unconfirmed")

    fresh_results = [dict(item) for item in dedupe_by_exit_ip(fresh_results)]
    seed_confirmed_results = [dict(item) for item in dedupe_by_exit_ip(seed_confirmed_results)]
    history_confirmed_results = [dict(item) for item in dedupe_by_exit_ip(history_confirmed_results)]
    retained_results = dedupe_results_for_display(list(seed_confirmed_results) + list(history_confirmed_results) + list(retained_history_results) + list(unconfirmed_seed_results))
    recommended_results = [
        dict(item)
        for item in list(fresh_results) + list(seed_confirmed_results) + list(history_confirmed_results)
        if bool(item.get("recommended", False))
    ]
    recommended_results = dedupe_results_for_display(recommended_results)
    displayed_results = annotate_result_countries(list(recommended_results), geo_cache)
    displayed_results = dedupe_results_for_display(displayed_results)

    proxy_state = update_proxy_state(proxy_state, all_records)
    save_proxy_state(proxy_state)
    save_geo_cache(geo_cache)
    save_verified_history(merge_verified_history(verified_history, fresh_results + seed_confirmed_results))

    fresh_passing_total = len(fresh_results)
    fresh_recommended_total = len(fresh_results)
    retained_total = len(retained_results)
    recommended_visible_total = len(displayed_results)
    runtime_seconds = int(time.perf_counter() - started_monotonic)
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
            "source_repo": "staged-mixed-pools",
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
            "fresh_live_total": fresh_recommended_total,
            "seed_confirmed_total": len(seed_confirmed_results),
            "history_total": len(history_confirmed_results) + len(retained_history_results),
            "unconfirmed_seed_total": len(unconfirmed_seed_results),
            "slow_hidden_total": slow_hidden_total,
            "fresh_slow_total": slow_hidden_total,
            "retained_total": retained_total,
            "recommended_visible_total": recommended_visible_total,
            "visible_total": recommended_visible_total,
            "working_total": recommended_visible_total,
            "working_unique_exit_ip": len({str(item.get("exit_ip", "")) for item in displayed_results if str(item.get("exit_ip", "")) != ""}),
            "retained_from_history": len(history_confirmed_results) + len(retained_history_results),
            "recommended_count": recommended_visible_total,
            "target_visible_total": SOFT_TARGET_TOTAL,
            "runtime_seconds": runtime_seconds,
            "fail_reason_counts": fail_reason_counts,
        },
        "fresh_results": fresh_results,
        "retained_results": retained_results,
        "recommended_results": recommended_results,
        "all_passing_results": all_passing_results,
        "displayed_results": displayed_results,
        "working": displayed_results,
        "top_candidates": [asdict(item) for item in combined_filtered_candidates[:18]],
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
        fresh_live_total=fresh_recommended_total,
        seed_confirmed_total=len(seed_confirmed_results),
        history_total=len(history_confirmed_results) + len(retained_history_results),
        unconfirmed_seed_total=len(unconfirmed_seed_results),
        retained_total=retained_total,
        recommended_visible_total=recommended_visible_total,
        visible_total=recommended_visible_total,
        runtime_seconds=runtime_seconds,
        slow_hidden=slow_hidden_total,
    )
    print(json.dumps(output, ensure_ascii=True))


if __name__ == "__main__":
    main()
