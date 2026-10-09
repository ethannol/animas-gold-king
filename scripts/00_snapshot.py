"""Step 0: check the committed snapshot against its manifest (no network) and record
the provenance numbers the report quotes."""

import json

from cairn import record

from animas import acquire

manifest = json.loads(acquire.MANIFEST.read_text())
ok = acquire.verify(quiet=True)
if not all(ok.values()):
    raise SystemExit(f"snapshot checksum mismatch: {[k for k, v in ok.items() if not v]}")
record("snapshot.n_files", len(ok))
record("snapshot.download_date", manifest["download_date_utc"][:10])
f = manifest["files"]
record("snapshot.wqp_result_rows", f["wqp_result.csv"]["rows_excluding_header"], unit="rows")
record("snapshot.wqp_result_mb", round(f["wqp_result.csv"]["bytes"] / 1e6, 1), unit="MB")
record("snapshot.wqp_nwis_rows", int(f["wqp_result.csv"]["headers"]["NWIS-Result-Count"]), unit="rows")
record("snapshot.wqp_storet_rows", int(f["wqp_result.csv"]["headers"]["STORET-Result-Count"]), unit="rows")
record("snapshot.wqp_sites", int(f["wqp_result.csv"]["headers"]["Total-Site-Count"]))
record("snapshot.wqx3_rows", manifest["probes"]["wqx3_fullPhysChem"]["rows_excluding_header"], unit="rows",
       note="same query on the WQX3 fullPhysChem profile; equals the STORET count, i.e. no NWIS rows")
record("snapshot.wqx3_missing_rows",
       f["wqp_result.csv"]["rows_excluding_header"] - manifest["probes"]["wqx3_fullPhysChem"]["rows_excluding_header"],
       unit="rows")
daily = {k: v for k, v in f.items() if v["kind"] == "usgs_daily_discharge"}
record("snapshot.n_gauges", len(daily))
record("snapshot.daily_rows_total", sum(v["rows_excluding_header"] for v in daily.values()), unit="rows")
record("snapshot.daily_rows_min", min(v["rows_excluding_header"] for v in daily.values()), unit="rows")
record("snapshot.daily_rows_max", max(v["rows_excluding_header"] for v in daily.values()), unit="rows")
record("snapshot.api_version", f["usgs_daily_USGS-09358550.csv"]["headers"].get("api-version", "unknown"))
record("snapshot.legacy_dv_status", manifest["probes"]["legacy_waterservices_dv"].get("http_status", "error"))
print("snapshot ok")
