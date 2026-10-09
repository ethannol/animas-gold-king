"""Interrupted time series on a flow-adjusted series.

resid = b0 + b1 * tau + b2 * post + b3 * post * tau + e,  tau = years since the release

with the plume-passage window excluded and censored rows kept as censored at their
residual bound. `level_change` is b2 (log units); `slope_change` is b3 (log units per
year). Percent change = exp(b2) - 1.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from animas.censored import Fit, censored_regression
from animas.cq import decimal_year

RELEASE_DATE = pd.Timestamp("2015-08-05")
PLANT_START = pd.Timestamp("2015-10-01")  # EPA: IWTP has treated discharge since October 2015


@dataclass
class Window:
    pre_start: pd.Timestamp
    plume_end: pd.Timestamp  # last day excluded (inclusive); post starts the next day
    post_end: pd.Timestamp
    release: pd.Timestamp = RELEASE_DATE

    def label(self) -> str:
        return f"pre{self.pre_start:%Y}_plume{self.plume_end:%Y%m%d}_post{self.post_end:%Y}"


def plume_mask(dates: pd.Series, release: pd.Timestamp, plume_end: pd.Timestamp) -> np.ndarray:
    """True for rows inside the plume-passage window [release, plume_end], inclusive."""
    d = pd.to_datetime(dates)
    return ((d >= release) & (d <= plume_end)).to_numpy()


def select(df: pd.DataFrame, w: Window) -> pd.DataFrame:
    d = pd.to_datetime(df["date"])
    keep = (d >= w.pre_start) & (d <= w.post_end) & ~plume_mask(df["date"], w.release, w.plume_end)
    return df.loc[keep].sort_values("date").reset_index(drop=True)


def its_design(dates: pd.Series, release: pd.Timestamp) -> tuple[np.ndarray, list[str]]:
    t = decimal_year(dates)
    t0 = decimal_year(pd.Series([release]))[0]
    tau = t - t0
    post = (pd.to_datetime(dates) > release).to_numpy(dtype=float)
    X = np.column_stack([np.ones_like(tau), tau, post, post * tau])
    return X, ["intercept", "pre_slope", "level_change", "slope_change"]


def fit_its(df: pd.DataFrame, w: Window, *, hac_lags: int = 12) -> Fit:
    """`df` has date, resid, censored (resid is a bound where censored)."""
    sub = select(df, w)
    X, names = its_design(sub["date"], w.release)
    return censored_regression(sub["resid"].to_numpy(float), X, sub["censored"].to_numpy(bool),
                               names=names, hac_lags=hac_lags)


def counterfactual(fit: Fit, dates: pd.Series, release: pd.Timestamp) -> np.ndarray:
    """What the pre-period trend predicts after the release (no level/slope change)."""
    X, _ = its_design(dates, release)
    X[:, 2:] = 0.0
    return X @ fit.params


def summarise(fit: Fit, sub: pd.DataFrame, w: Window) -> dict:
    lo, hi = fit.ci("level_change")
    slo, shi = fit.ci("slope_change")
    pre = pd.to_datetime(sub["date"]) < w.release
    return {
        "window": w.label(),
        "pre_start": str(w.pre_start.date()),
        "plume_end": str(w.plume_end.date()),
        "post_end": str(w.post_end.date()),
        "n": fit.n,
        "n_pre": int(pre.sum()),
        "n_post": int((~pre).sum()),
        "n_censored": fit.n_censored,
        "level_change_log": fit.coef("level_change"),
        "level_change_se": fit.stderr("level_change"),
        "level_change_lo": lo,
        "level_change_hi": hi,
        "level_change_pct": 100 * (np.exp(fit.coef("level_change")) - 1),
        "level_change_pct_lo": 100 * (np.exp(lo) - 1),
        "level_change_pct_hi": 100 * (np.exp(hi) - 1),
        "level_change_p": fit.pvalue("level_change"),
        "slope_change_per_yr": fit.coef("slope_change"),
        "slope_change_lo": slo,
        "slope_change_hi": shi,
        "slope_change_p": fit.pvalue("slope_change"),
        "pre_slope_per_yr": fit.coef("pre_slope"),
        "pre_slope_se": fit.stderr("pre_slope"),
        "sigma": fit.sigma,
        "hac_lags": fit.hac_lags,
        "converged": fit.converged,
    }
