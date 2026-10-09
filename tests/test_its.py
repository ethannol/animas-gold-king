import numpy as np
import pandas as pd

from animas.its import RELEASE_DATE, Window, fit_its, plume_mask, select, summarise

W = Window(pd.Timestamp("2005-01-01"), pd.Timestamp("2015-09-30"), pd.Timestamp("2025-12-31"))


def _series(seed, level=0.0, slope=0.0, ar=0.4):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2005-01-10", "2025-12-10", freq="MS")
    n = len(dates)
    e = np.zeros(n)
    for i in range(1, n):
        e[i] = ar * e[i - 1] + rng.normal(scale=0.3)
    post = (dates > RELEASE_DATE).astype(float)
    tau = (dates - RELEASE_DATE).days / 365.25
    y = level * post + slope * post * tau + e
    return pd.DataFrame({"date": dates, "resid": y, "censored": False})


def test_recovers_planted_level_change():
    df = _series(5, level=-0.5)
    fit = fit_its(df, W)
    s = summarise(fit, select(df, W), W)
    assert abs(s["level_change_log"] + 0.5) < 0.2
    assert s["level_change_lo"] < -0.5 < s["level_change_hi"]
    assert s["level_change_p"] < 0.01


def test_null_series_reports_no_change():
    hits = 0
    for seed in range(10):
        df = _series(100 + seed)
        fit = fit_its(df, W)
        if fit.pvalue("level_change") < 0.05:
            hits += 1
    assert hits <= 2  # nominal 5% with HAC on AR(1) noise; allow slack


def test_plume_window_excludes_exactly_the_intended_rows():
    dates = pd.to_datetime(["2015-08-04", "2015-08-05", "2015-08-20", "2015-09-30", "2015-10-01"])
    m = plume_mask(pd.Series(dates), RELEASE_DATE, pd.Timestamp("2015-09-30"))
    assert m.tolist() == [False, True, True, True, False]
    df = pd.DataFrame({"date": dates, "resid": 0.0, "censored": False})
    kept = select(df, W)
    assert kept["date"].tolist() == [pd.Timestamp("2015-08-04"), pd.Timestamp("2015-10-01")]
