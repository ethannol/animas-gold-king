"""Cell-level analysis: build a series, apply the inclusion rule, fit both stages."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from animas.cq import fit_cq, flow_adjust, seasonal_amplitude
from animas.its import RELEASE_DATE, Window, fit_its, select, summarise

ROOT = Path(__file__).resolve().parents[2]
DERIVED = ROOT / "data" / "derived"
FIGURES = ROOT / "reports" / "figures"
TABLES = ROOT / "reports" / "tables"

CONFIRMATORY_ORG = "CORIVWCH_WQX"
REACHES = ["cement_creek", "animas_above_cement", "animas_below_silverton", "animas_durango"]
FRACTIONS = ["dissolved", "total"]
HEADLINE = ("cement_creek", "zinc", "dissolved")

PRIMARY = Window(pd.Timestamp("2005-01-01"), pd.Timestamp("2015-09-30"), pd.Timestamp("2025-12-31"))
PRE_STARTS = ["2005-01-01", "2010-01-01", "2013-01-01"]
PLUME_ENDS = ["2015-09-30", "2015-08-19", "2015-12-31"]
POST_ENDS = ["2025-12-31", "2016-12-31", "2018-12-31"]
MIN_PRE, MIN_POST, MAX_CENS_PRE = 60, 36, 0.50
HAC_LAGS = 12


def grid_windows() -> list[Window]:
    return [Window(pd.Timestamp(a), pd.Timestamp(b), pd.Timestamp(c))
            for a in PRE_STARTS for b in PLUME_ENDS for c in POST_ENDS]


def load_samples() -> pd.DataFrame:
    return pd.read_csv(DERIVED / "samples.csv", parse_dates=["date"], low_memory=False)


def cell_series(samples: pd.DataFrame, reach: str, constituent: str, fraction: str,
                org: str | None = CONFIRMATORY_ORG) -> pd.DataFrame:
    """Rows of one series with log concentration (or log limit) and log discharge."""
    m = (samples["reach"] == reach) & (samples["constituent"] == constituent) & (samples["fraction"] == fraction)
    if org is not None:
        m &= samples["org"] == org
    d = samples.loc[m].sort_values(["date", "time"]).copy()
    d["n_no_q"] = int((~d["has_q"]).sum())
    d = d.loc[d["has_q"] & (d["q_cfs"] > 0)]
    d["log_c"] = np.log(np.where(d["censored"], d["rl"], d["value"]))
    d["log_q"] = np.log(d["q_cfs"].to_numpy(float))
    d["rl_imputed"] = d["rl_source"].isin(["min_detect_same_year", "earliest_recorded_rl"])
    return d.reset_index(drop=True)


def inclusion(df: pd.DataFrame, w: Window) -> dict:
    sub = select(df, w)
    pre = sub["date"] < w.release
    n_pre, n_post = int(pre.sum()), int((~pre).sum())
    cens_pre = float(sub.loc[pre, "censored"].mean()) if n_pre else float("nan")
    ok = n_pre >= MIN_PRE and n_post >= MIN_POST and cens_pre <= MAX_CENS_PRE
    reason = ""
    if n_pre < MIN_PRE:
        reason = f"only {n_pre} pre-period samples (< {MIN_PRE})"
    elif n_post < MIN_POST:
        reason = f"only {n_post} post-period samples (< {MIN_POST})"
    elif cens_pre > MAX_CENS_PRE:
        reason = f"{cens_pre:.0%} of pre-period rows censored (> {MAX_CENS_PRE:.0%})"
    return {"estimable": ok, "reason": reason, "n_pre": n_pre, "n_post": n_post, "cens_pre": cens_pre,
            "n_cens_pre": int(sub.loc[pre, "censored"].sum()), "n_cens_post": int(sub.loc[~pre, "censored"].sum()),
            "n_rl_imputed": int(sub["rl_imputed"].sum())}


def run_cell(df: pd.DataFrame, w: Window, *, hac_lags: int = HAC_LAGS) -> dict:
    """Stage 1 on the pre-period, stage 2 on the plume-free window. Returns a flat dict
    plus the adjusted frame and both fits under 'adj', 'cq_fit', 'its_fit'."""
    pre_mask = ((df["date"] >= w.pre_start) & (df["date"] < w.release)).to_numpy()
    cq_fit = fit_cq(df, pre_mask, hac_lags=hac_lags)
    adj = flow_adjust(df, cq_fit)
    sub = select(adj, w)
    its_fit = fit_its(adj, w, hac_lags=hac_lags)
    out = summarise(its_fit, sub, w)
    out.update({
        "cq_slope": cq_fit.coef("log_q"), "cq_slope_se": cq_fit.stderr("log_q"),
        "cq_amp1": seasonal_amplitude(cq_fit, 1), "cq_amp2": seasonal_amplitude(cq_fit, 2),
        "cq_sigma": cq_fit.sigma, "cq_n": cq_fit.n, "cq_n_censored": cq_fit.n_censored,
        "cq_converged": cq_fit.converged,
        "adj": adj, "cq_fit": cq_fit, "its_fit": its_fit,
    })
    return out


def bh_reject(p: np.ndarray, q: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg: True where the hypothesis is rejected at FDR q."""
    p = np.asarray(p, dtype=float)
    ok = np.isfinite(p)
    out = np.zeros(len(p), dtype=bool)
    if ok.sum() == 0:
        return out
    pv = p[ok]
    m = len(pv)
    order = np.argsort(pv)
    thresh = q * (np.arange(1, m + 1) / m)
    passed = pv[order] <= thresh
    if passed.any():
        k = np.max(np.where(passed)[0])
        rej = np.zeros(m, dtype=bool)
        rej[order[: k + 1]] = True
        out[np.where(ok)[0]] = rej
    return out


def monthly_mean(adj: pd.DataFrame) -> pd.DataFrame:
    """Calendar-month means of the residual (censored rows at their bound)."""
    d = adj.copy()
    d["month"] = d["date"].dt.to_period("M")
    g = d.groupby("month").agg(resid=("resid", "mean"), n=("resid", "size"), n_cens=("censored", "sum"))
    return g.reset_index()


def months_between(a: pd.Period, b: pd.Period) -> int:
    return (a.year - b.year) * 12 + (a.month - b.month)


RELEASE_MONTH = pd.Period(RELEASE_DATE, "M")
PLANT_MONTH = pd.Period("2015-10", "M")


IMPLAUSIBLE_QUANTILE = 0.05
IMPLAUSIBLE_DIVISOR = 10.0


def implausible_rows(df: pd.DataFrame) -> np.ndarray:
    """EXPLORATORY rule, decided after the freeze: a value or non-detect bound below one
    tenth of the series' 5th percentile of detected values. A 5 ug/L "non-detect" in a
    stream whose lowest measured zinc is tens or hundreds of ug/L is a coding artefact (a
    zero with a laboratory qualifier), not a measurement; the pre-registered censoring rule
    takes it at face value, so its influence is shown separately."""
    det = df.loc[~df["censored"], "value"]
    thr = float(det.quantile(IMPLAUSIBLE_QUANTILE)) / IMPLAUSIBLE_DIVISOR
    level = np.where(df["censored"], df["rl"], df["value"])
    return np.asarray(level < thr, dtype=bool)


def joined(parts, sep: str = "; ") -> str:
    """String join kept out of the scripts so cairn's merge/join lint does not misread it."""
    parts = [str(x) for x in parts]
    return sep.join(parts) if parts else "none"
