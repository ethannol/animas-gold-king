"""Comparability and quality-control preparation of the raw snapshot.

Reads data/raw/ (never modified) and writes data/derived/:

    samples.csv          routine water-column results for the metals, pH and specific
                         conductance: canonical units, censoring bounds, reach, paired
                         daily discharge; one row per source result that survived
    qc_samples.csv       quality-control rows (blanks, replicates, spikes), same columns
    sample_flow.csv      instantaneous discharge recorded with a sample
    excluded.csv         every excluded source row with the rule that removed it
    exclusion_log.csv    one line per rule with rows before and after
    discharge_daily.csv  daily mean discharge per gauge (long)
    sites.csv            station metadata with reach and role

Nothing is dropped silently and no join may change the row count.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from cairn import checked_merge, recount, unique_key

from animas.units import CHARACTERISTICS, UnitError, factor_to_canonical, fraction_class

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"

COLS = {
    "org": "OrganizationIdentifier",
    "org_name": "OrganizationFormalName",
    "site_id": "MonitoringLocationIdentifier",
    "site_name": "MonitoringLocationName",
    "activity_id": "ActivityIdentifier",
    "activity_type": "ActivityTypeCode",
    "media": "ActivityMediaName",
    "media_sub": "ActivityMediaSubdivisionName",
    "date": "ActivityStartDate",
    "time": "ActivityStartTime/Time",
    "characteristic": "CharacteristicName",
    "fraction_raw": "ResultSampleFractionText",
    "value_raw": "ResultMeasureValue",
    "unit_raw": "ResultMeasure/MeasureUnitCode",
    "qualifier": "MeasureQualifierCode",
    "status": "ResultStatusIdentifier",
    "value_type": "ResultValueTypeName",
    "detect_cond": "ResultDetectionConditionText",
    "dl_type": "DetectionQuantitationLimitTypeName",
    "dl_raw": "DetectionQuantitationLimitMeasure/MeasureValue",
    "dl_unit_raw": "DetectionQuantitationLimitMeasure/MeasureUnitCode",
    "pcode": "USGSPCode",
    "method_id": "ResultAnalyticalMethod/MethodIdentifier",
    "method_name": "ResultAnalyticalMethod/MethodName",
    "lab": "LaboratoryName",
    "result_id": "ResultIdentifier",
    "provider": "ProviderName",
}
NONDETECT = {"Not Detected", "Not Detected at Detection Limit", "*Non-detect", "Detected Not Quantified"}
NOT_REPORTED = {"Not Reported"}
QC_PREFIX = "Quality Control"
ROUTINE_TYPES = {"Sample-Routine", "Sample", "Field Msr/Obs"}


class ExclusionLog:
    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.excluded: list[pd.DataFrame] = []

    def step(self, name: str, rule: str, before: pd.DataFrame, kept: pd.Series,
             *, destination: str = "excluded") -> pd.DataFrame:
        if not isinstance(kept, pd.Series):
            kept = pd.Series(np.asarray(kept), index=before.index)
        kept = kept.fillna(False).astype(bool)
        dropped = before.loc[~kept]
        self.rows.append({"step": name, "rule": rule, "rows_before": int(len(before)),
                          "rows_after": int(kept.sum()), "rows_removed": int((~kept).sum()),
                          "destination": destination})
        if len(dropped) and destination == "excluded":
            self.excluded.append(dropped.assign(exclusion_step=name))
        return before.loc[kept]

    def frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)

    def excluded_frame(self) -> pd.DataFrame:
        if not self.excluded:
            return pd.DataFrame()
        return pd.concat(self.excluded, ignore_index=True)


def load_query() -> dict:
    return json.loads((RAW / "query.json").read_text())


def site_table(q: dict) -> pd.DataFrame:
    rows = []
    for reach, meta in q["reaches"].items():
        for s in meta["sites"]:
            rows.append({"site_id": s, "reach": reach, "role": meta["role"], "gauge": meta["gauge"],
                         "reach_label": meta["label"]})
    return pd.DataFrame(rows)


def load_raw() -> tuple[pd.DataFrame, pd.DataFrame]:
    res = pd.read_csv(RAW / "wqp_result.csv", dtype=str, keep_default_na=False)
    res.insert(0, "raw_row", np.arange(2, len(res) + 2))  # 1-based line number in the CSV
    st = pd.read_csv(RAW / "wqp_station.csv", dtype=str, keep_default_na=False)
    return res, st


def load_discharge(q: dict) -> pd.DataFrame:
    frames = []
    for gauge in q["usgs_daily"]["gauges"]:
        d = pd.read_csv(RAW / f"usgs_daily_{gauge}.csv", dtype=str, keep_default_na=False)
        frames.append(pd.DataFrame({
            "gauge": d["monitoring_location_id"],
            "date": pd.to_datetime(d["time"]),
            "q_cfs": pd.to_numeric(d["value"].replace("", np.nan)),
            "q_approval": d["approval_status"],
            "q_qualifier": d["qualifier"],
            "q_unit": d["unit_of_measure"],
        }))
    daily = pd.concat(frames, ignore_index=True).sort_values(["gauge", "date"]).reset_index(drop=True)
    unique_key(daily, ["gauge", "date"])
    return daily


def canonicalize(res: pd.DataFrame, sites: pd.DataFrame) -> pd.DataFrame:
    d = res[["raw_row", *COLS.values()]].rename(columns={v: k for k, v in COLS.items()})
    d["date"] = pd.to_datetime(d["date"], format="%Y-%m-%d")
    d["year"] = d["date"].dt.year
    d["constituent"] = d["characteristic"].map(CHARACTERISTICS)
    d["fraction"] = [fraction_class(f, c) if isinstance(c, str) else "unknown"
                     for f, c in zip(d["fraction_raw"], d["constituent"], strict=True)]
    d["value_num"] = pd.to_numeric(d["value_raw"].replace("", np.nan), errors="coerce")
    d["dl_num"] = pd.to_numeric(d["dl_raw"].replace("", np.nan), errors="coerce")
    # Non-detects arrive four ways: a detection-condition text; a "<x" value; a reported
    # 0 with laboratory qualifier U (undetected); a reported 0 with qualifier DL and a limit.
    qual = d["qualifier"].fillna("").str.split(";")
    has_u = qual.apply(lambda xs: "U" in xs)
    zero_dl = (d["value_num"] == 0) & qual.apply(lambda xs: "DL" in xs)
    lt = d["value_raw"].str.startswith("<")
    by_text = d["detect_cond"].isin(NONDETECT)
    d["censored"] = by_text | lt | has_u | zero_dl
    d["censor_source"] = np.select([by_text, lt, has_u, zero_dl],
                                   ["detect_cond", "lt_prefix", "qualifier_U", "qualifier_DL_zero"], "")
    d["not_reported"] = d["detect_cond"].isin(NOT_REPORTED)
    d["is_qc"] = d["activity_type"].str.startswith(QC_PREFIX)
    # Units: a detected row carries its unit on the result; a censored row on the limit.
    unit_for_value = d["unit_raw"].where(d["unit_raw"] != "", d["dl_unit_raw"])
    unit_for_dl = d["dl_unit_raw"].where(d["dl_unit_raw"] != "", d["unit_raw"])

    def _factor(c, u):
        if not isinstance(c, str):
            return np.nan
        try:
            return factor_to_canonical(c, u)
        except UnitError:
            return np.nan

    d["factor_value"] = [_factor(c, u) for c, u in zip(d["constituent"], unit_for_value, strict=True)]
    d["factor_dl"] = [_factor(c, u) for c, u in zip(d["constituent"], unit_for_dl, strict=True)]
    d["value"] = d["value_num"] * d["factor_value"]
    d["rl"] = d["dl_num"] * d["factor_dl"]
    lt_num = pd.to_numeric(d["value_raw"].str.lstrip("<"), errors="coerce") * d["factor_value"]
    d["rl"] = d["rl"].where(d["rl"].notna(), lt_num.where(lt))
    d["rl_source"] = np.where(d["censored"] & d["rl"].notna(), "reported", "")
    d.loc[d["censored"], "value"] = np.nan  # a non-detect has no value, only a bound
    d = checked_merge(d, sites, on="site_id", expect="m:1", how="left", min_match_rate=1.0)
    return d


def split_tables(d: pd.DataFrame, log: ExclusionLog) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Apply every rule in order. Returns (samples, qc, flow)."""
    d = log.step("E01_media", "ActivityMediaName must be Water (sediment, soil, tissue, pore water out)",
                 d, (d["media"] == "Water") & ~d["media_sub"].isin(["Pore water"]))
    d = log.step("E02_characteristic", "CharacteristicName in the requested list", d, d["constituent"].notna())
    qc = d.loc[d["is_qc"]].copy()
    d = log.step("E03_qc", "Quality-control activities go to qc_samples.csv, not the sample table",
                 d, ~d["is_qc"], destination="qc_samples.csv")
    d = log.step("E04_activity_type", "ActivityTypeCode must be a routine sample or field measurement",
                 d, d["activity_type"].isin(ROUTINE_TYPES))
    flow = d.loc[d["constituent"] == "flow"].copy()
    d = log.step("E05_flow", "Instantaneous discharge rows go to sample_flow.csv", d,
                 d["constituent"] != "flow", destination="sample_flow.csv")
    d = log.step("E06_fraction", "Metal rows need a dissolved or total/recoverable fraction label",
                 d, d["fraction"] != "unknown")
    d = log.step("E07_not_reported", "ResultDetectionConditionText 'Not Reported' carries no value",
                 d, ~d["not_reported"])
    d = log.step("E08_unit", "Result (or limit, for non-detects) unit must convert to the canonical unit",
                 d, np.where(d["censored"], d["factor_dl"].notna(), d["factor_value"].notna()))
    d = impute_missing_limits(d)
    d = log.step("E09_value", "A detected row needs a numeric value; a non-detect needs a numeric limit",
                 d, np.where(d["censored"], d["rl"].notna(), d["value"].notna()))
    positive = np.where(d["constituent"] == "ph", True, np.where(d["censored"], d["rl"] > 0, d["value"] > 0))
    d = log.step("E10_positive", "Metals and conductance must be > 0 (log scale)", d,
                 pd.Series(positive, index=d.index))
    key = ["org", "site_id", "date", "time", "constituent", "fraction"]
    d = d.sort_values([*key, "result_id"])
    d = log.step("E11_duplicates",
                 "One result per org/site/date/time/constituent/fraction: keep the first ResultIdentifier",
                 d, ~d.duplicated(key, keep="first"))
    return d.reset_index(drop=True), qc.reset_index(drop=True), flow.reset_index(drop=True)


def impute_missing_limits(d: pd.DataFrame) -> pd.DataFrame:
    """Give a bound to non-detects that arrived without a reporting limit.

    Rule, in order: (1) the smallest detected value the same organisation reported for the
    same constituent and fraction in the same calendar year (the limit cannot exceed it);
    (2) otherwise the median limit that organisation recorded for that constituent and
    fraction in the earliest year it recorded any. Rows are flagged in `rl_source` so the
    analysis can count them; rows that get no bound are excluded by the next rule.
    """
    d = d.copy()
    need = d["censored"] & d["rl"].isna()
    grp = ["org", "constituent", "fraction", "year"]
    min_det = d.loc[~d["censored"]].groupby(grp)["value"].min().rename("rl_min_detect")
    d = checked_merge(d, min_det.reset_index(), on=grp, expect="m:1", how="left")
    use1 = need & d["rl_min_detect"].notna()
    d.loc[use1, "rl"] = d.loc[use1, "rl_min_detect"]
    d.loc[use1, "rl_source"] = "min_detect_same_year"
    rec = d.loc[d["rl_source"] == "reported"]
    first_year = rec.groupby(["org", "constituent", "fraction"])["year"].min().rename("first_rl_year")
    early = checked_merge(rec, first_year.reset_index(), on=["org", "constituent", "fraction"],
                          expect="m:1", how="inner")
    early = early.loc[early["year"] == early["first_rl_year"]]
    early_rl = early.groupby(["org", "constituent", "fraction"])["rl"].median().rename("rl_earliest")
    d = checked_merge(d, early_rl.reset_index(), on=["org", "constituent", "fraction"], expect="m:1", how="left")
    need2 = d["censored"] & d["rl"].isna() & d["rl_earliest"].notna()
    d.loc[need2, "rl"] = d.loc[need2, "rl_earliest"]
    d.loc[need2, "rl_source"] = "earliest_recorded_rl"
    return d.drop(columns=["rl_min_detect", "rl_earliest"])


def attach_discharge(samples: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    """Left-join the paired gauge's daily mean discharge on the sample date (m:1).

    Row count is preserved; samples on days without a daily value get NaN discharge and
    `has_q = False`. A duplicate (gauge, date) in `daily` makes checked_merge raise.
    """
    cols = ["gauge", "date", "q_cfs", "q_approval", "q_qualifier"]
    out = checked_merge(samples, daily[cols], on=["gauge", "date"], expect="m:1", how="left")
    recount(samples, out, "samples+discharge", expect="same")
    out["has_q"] = out["q_cfs"].notna()
    return out


OUTPUT_COLS = [
    "raw_row", "result_id", "org", "org_name", "site_id", "site_name", "reach", "reach_label", "role",
    "gauge", "activity_id", "activity_type", "date", "year", "time", "characteristic", "constituent",
    "fraction_raw", "fraction", "value_raw", "unit_raw", "value", "censored", "rl", "dl_raw",
    "dl_unit_raw", "dl_type", "detect_cond", "censor_source", "rl_source", "qualifier", "status", "value_type", "pcode",
    "method_id", "method_name", "lab", "provider",
]


def run() -> dict:
    DERIVED.mkdir(parents=True, exist_ok=True)
    q = load_query()
    sites = site_table(q)
    res, st = load_raw()
    daily = load_discharge(q)
    log = ExclusionLog()
    d = canonicalize(res, sites)
    samples, qc, flow = split_tables(d, log)
    samples = attach_discharge(samples, daily)
    out_cols = [*OUTPUT_COLS, "q_cfs", "q_approval", "q_qualifier", "has_q"]
    samples[out_cols].to_csv(DERIVED / "samples.csv", index=False)
    qc[OUTPUT_COLS].to_csv(DERIVED / "qc_samples.csv", index=False)
    flow[OUTPUT_COLS].to_csv(DERIVED / "sample_flow.csv", index=False)
    log.frame().to_csv(DERIVED / "exclusion_log.csv", index=False)
    exc = log.excluded_frame()
    exc_cols = [c for c in [*OUTPUT_COLS, "media", "media_sub", "exclusion_step"] if c in exc.columns]
    exc[exc_cols].to_csv(DERIVED / "excluded.csv", index=False)
    daily.to_csv(DERIVED / "discharge_daily.csv", index=False)
    st_cols = ["MonitoringLocationIdentifier", "MonitoringLocationName", "OrganizationIdentifier",
               "MonitoringLocationTypeName", "LatitudeMeasure", "LongitudeMeasure", "HUCEightDigitCode"]
    sites_out = checked_merge(sites, st[st_cols].rename(columns={"MonitoringLocationIdentifier": "site_id"}),
                              on="site_id", expect="1:1", how="left")
    sites_out.to_csv(DERIVED / "sites.csv", index=False)
    return {
        "raw_rows": int(len(res)), "sample_rows": int(len(samples)), "qc_rows": int(len(qc)),
        "flow_rows": int(len(flow)), "excluded_rows": int(len(exc)), "daily_rows": int(len(daily)),
        "n_sites_with_data": int(samples["site_id"].nunique()), "n_orgs": int(samples["org"].nunique()),
        "share_with_q": float(samples["has_q"].mean()),
    }
