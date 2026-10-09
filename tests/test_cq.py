import numpy as np
import pandas as pd

from animas.cq import decimal_year, fit_cq, flow_adjust, seasonal_amplitude


def test_recovers_slope_and_seasonal_amplitude():
    rng = np.random.default_rng(3)
    dates = pd.date_range("2005-01-15", periods=240, freq="MS") + pd.to_timedelta(rng.integers(0, 20, 240), "D")
    t = decimal_year(pd.Series(dates))
    log_q = 3.0 + 1.2 * np.sin(2 * np.pi * (t - 0.4)) + rng.normal(scale=0.3, size=240)
    amp, phase = 0.6, 1.1
    log_c = 8.0 - 0.7 * log_q + amp * np.sin(2 * np.pi * t + phase) + rng.normal(scale=0.2, size=240)
    df = pd.DataFrame({"date": dates, "log_q": log_q, "log_c": log_c, "censored": False})
    fit = fit_cq(df, np.ones(240, dtype=bool))
    assert abs(fit.coef("log_q") + 0.7) < 0.06
    assert abs(seasonal_amplitude(fit, 1) - amp) < 0.08
    adj = flow_adjust(df, fit)
    assert adj["resid"].std() < 0.3
    assert abs(adj["resid"].mean()) < 0.02


def test_censored_rows_get_bounds():
    rng = np.random.default_rng(4)
    dates = pd.date_range("2005-01-01", periods=120, freq="MS")
    log_q = rng.normal(3, 0.5, 120)
    log_c = 2.0 - 0.5 * log_q + rng.normal(scale=0.3, size=120)
    cens = log_c < 0.3
    df = pd.DataFrame({"date": dates, "log_q": log_q, "log_c": np.where(cens, 0.3, log_c), "censored": cens})
    fit = fit_cq(df, np.ones(120, dtype=bool))
    assert fit.n_censored == cens.sum() > 0
    assert abs(fit.coef("log_q") + 0.5) < 0.15
