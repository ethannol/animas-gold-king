"""Concentration-discharge model with seasonal harmonics.

log C = a + b log Q + sum_k [c_k sin(2 pi k t) + d_k cos(2 pi k t)],  k = 1, 2

fitted on a stated window (the pre-period in the confirmatory analysis) by censored
regression, then applied to every row to give flow-adjusted residuals. Censored rows get
a residual *bound* (log RL - fitted) and keep their censored flag, so the second stage
can treat them as censored at that bound instead of as values.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from animas.censored import Fit, censored_regression

HARMONICS = 2


def decimal_year(dates: pd.Series) -> np.ndarray:
    d = pd.to_datetime(dates)
    start = pd.to_datetime(d.dt.year.astype(str) + "-01-01")
    length = pd.to_datetime((d.dt.year + 1).astype(str) + "-01-01") - start
    return (d.dt.year + (d - start) / length).to_numpy(dtype=float)


def design(log_q: np.ndarray, t: np.ndarray, harmonics: int = HARMONICS) -> tuple[np.ndarray, list[str]]:
    cols = [np.ones_like(log_q), log_q]
    names = ["intercept", "log_q"]
    for k in range(1, harmonics + 1):
        cols += [np.sin(2 * np.pi * k * t), np.cos(2 * np.pi * k * t)]
        names += [f"sin{k}", f"cos{k}"]
    return np.column_stack(cols), names


def seasonal_amplitude(fit: Fit, k: int = 1) -> float:
    return float(np.hypot(fit.coef(f"sin{k}"), fit.coef(f"cos{k}")))


def fit_cq(df: pd.DataFrame, mask: np.ndarray | pd.Series, *, hac_lags: int = 12) -> Fit:
    """Fit the C-Q model on rows where `mask` is True.

    `df` needs columns: date, log_c (log concentration, or log RL where censored),
    log_q, censored (bool). Rows must be sorted by date.
    """
    sub = df.loc[np.asarray(mask, dtype=bool)]
    X, names = design(sub["log_q"].to_numpy(float), decimal_year(sub["date"]))
    return censored_regression(sub["log_c"].to_numpy(float), X, sub["censored"].to_numpy(bool),
                               names=names, hac_lags=hac_lags)


def flow_adjust(df: pd.DataFrame, fit: Fit) -> pd.DataFrame:
    """Add `fitted` and `resid` (a bound for censored rows) to a copy of `df`."""
    X, _ = design(df["log_q"].to_numpy(float), decimal_year(df["date"]))
    out = df.copy()
    out["fitted"] = X @ fit.params
    out["resid"] = out["log_c"] - out["fitted"]
    return out
