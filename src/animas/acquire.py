"""Download the public snapshot (Water Quality Portal results and stations, USGS daily
discharge) described by data/raw/query.json, and write data/raw/manifest.json.

Modelled on the groundwater-audit sibling's checksummed WQP acquisition module. The
query lives in a JSON file so the retrieval is reproducible; the downloaded files are
never modified by the rest of the pipeline. Network access is needed only here.

    uv run python scripts/download.py            # download into data/raw/
    uv run python scripts/download.py --verify   # recompute checksums of the snapshot
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
QUERY = RAW / "query.json"
MANIFEST = RAW / "manifest.json"
WQP_FILES = {"result": "wqp_result.csv", "station": "wqp_station.csv"}
LEGACY_DV = "https://waterservices.usgs.gov/nwis/dv/"
TIMEOUT = 900

ATTRIBUTION = (
    "Water-quality data retrieved from the Water Quality Portal "
    "(https://www.waterqualitydata.us), a cooperative service of the USGS, EPA and NWQMC, "
    "accessed {date}. Records come from USGS NWIS and from EPA WQX/STORET submissions by "
    "Colorado River Watch (CORIVWCH_WQX), the Animas River Stakeholders Group (ARSG), "
    "EPA Region 8 (USEPA_REGION8, BPMWQX), the Colorado Department of Public Health and "
    "Environment (21COL001, 21COL001_WQX) and the Southern Ute Indian Tribe (SOUTHUTE). "
    "Daily discharge from the USGS Water Data API (https://api.waterdata.usgs.gov). "
    "USGS data are public-domain U.S. Government works."
)


def load_query() -> dict[str, Any]:
    return json.loads(QUERY.read_text())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_csv_rows(data: bytes) -> int:
    text = io.StringIO(data.decode("utf-8", errors="replace"), newline="")
    return max(sum(1 for _ in csv.reader(text)) - 1, 0)


def all_sites(q: dict[str, Any]) -> list[str]:
    seen: list[str] = []
    for reach in q["reaches"].values():
        for s in reach["sites"]:
            if s not in seen:
                seen.append(s)
    return seen


def wqp_params(q: dict[str, Any], which: str, profile: str | None = None) -> list[tuple[str, str]]:
    """Parameter list for a WQP request; multi-valued keys are repeated."""
    w = q["wqp"]
    params: list[tuple[str, str]] = [("siteid", ";".join(all_sites(q)))]
    for k, v in w["params"].items():
        if isinstance(v, list):
            params.extend((k, item) for item in v)
        else:
            params.append((k, v))
    if which == "result":
        params.append(("dataProfile", profile or w["result_profile"]))
    return params


def _record(r: requests.Response, data: bytes) -> dict[str, Any]:
    return {
        "url": r.url,
        "http_status": r.status_code,
        "headers": dict(r.headers),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
        "rows_excluding_header": count_csv_rows(data),
    }


def fetch(url: str, params: list[tuple[str, str]] | dict[str, Any]) -> tuple[requests.Response, bytes]:
    print(f"GET {url} {params}", file=sys.stderr)
    r = requests.get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r, r.content


def download_wqp(q: dict[str, Any], manifest: dict[str, Any]) -> None:
    w = q["wqp"]
    for which, fname in WQP_FILES.items():
        r, data = fetch(w["base_url"] + w["endpoints"][which], wqp_params(q, which))
        (RAW / fname).write_bytes(data)
        manifest["files"][fname] = {"kind": f"wqp_{which}", **_record(r, data)}
        print(f"  -> {fname}: {len(data)} bytes, {manifest['files'][fname]['rows_excluding_header']} rows",
              file=sys.stderr)


def probe_wqx3(q: dict[str, Any], manifest: dict[str, Any]) -> None:
    """Same result query on the WQX3 'fullPhysChem' profile; counted, not kept."""
    w = q["wqp"]
    url = w["base_url"] + "/wqx3/Result/search"
    try:
        r, data = fetch(url, wqp_params(q, "result", profile="fullPhysChem"))
        rec = _record(r, data)
        tail = data[-400:].decode("utf-8", errors="replace")
        rec["ends_with_error_sentinel"] = "ERROR" in tail.upper()
        manifest["probes"]["wqx3_fullPhysChem"] = rec
    except requests.RequestException as e:  # record the failure, do not abort
        manifest["probes"]["wqx3_fullPhysChem"] = {"url": url, "error": str(e)}


def download_daily(q: dict[str, Any], manifest: dict[str, Any]) -> None:
    d = q["usgs_daily"]
    limit = int(d["params"]["limit"])
    for gauge in d["gauges"]:
        params = {**d["params"], "monitoring_location_id": gauge}
        r, data = fetch(d["base_url"], params)
        rows = count_csv_rows(data)
        if rows >= limit:
            raise RuntimeError(f"{gauge}: page limit {limit} reached; add paging before trusting this")
        fname = f"usgs_daily_{gauge}.csv"
        (RAW / fname).write_bytes(data)
        manifest["files"][fname] = {"kind": "usgs_daily_discharge", "gauge": gauge, **_record(r, data)}
        print(f"  -> {fname}: {rows} rows", file=sys.stderr)


def probe_legacy_dv(q: dict[str, Any], manifest: dict[str, Any]) -> None:
    gauge = q["usgs_daily"]["gauges"][0].replace("USGS-", "")
    params = {"format": "json", "sites": gauge, "parameterCd": "00060",
              "startDT": "2015-08-01", "endDT": "2015-08-10"}
    try:
        r, data = fetch(LEGACY_DV, params)
        n = None
        try:
            ts = json.loads(data)["value"]["timeSeries"]
            n = len(ts[0]["values"][0]["value"]) if ts else 0
        except (KeyError, IndexError, ValueError):
            pass
        manifest["probes"]["legacy_waterservices_dv"] = {
            "url": r.url, "http_status": r.status_code, "bytes": len(data), "values_returned": n,
            "note": "legacy endpoint still answered; not used for the snapshot",
        }
    except requests.RequestException as e:
        manifest["probes"]["legacy_waterservices_dv"] = {"url": LEGACY_DV, "error": str(e)}


def download() -> None:
    q = load_query()
    today = dt.date.today().isoformat()
    manifest: dict[str, Any] = {
        "download_date_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "query_sha256": sha256_file(QUERY),
        "attribution": ATTRIBUTION.format(date=today),
        "files": {},
        "probes": {},
    }
    download_wqp(q, manifest)
    probe_wqx3(q, manifest)
    download_daily(q, manifest)
    probe_legacy_dv(q, manifest)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {MANIFEST}", file=sys.stderr)


def verify(quiet: bool = False) -> dict[str, bool]:
    """Recompute every checksum in the manifest; returns {filename: ok}."""
    manifest = json.loads(MANIFEST.read_text())
    out: dict[str, bool] = {}
    for fname, meta in manifest["files"].items():
        p = RAW / fname
        ok = p.is_file() and sha256_file(p) == meta["sha256"]
        out[fname] = ok
        if not quiet:
            print(f"{'OK      ' if ok else 'MISMATCH'} {fname}")
    return out
