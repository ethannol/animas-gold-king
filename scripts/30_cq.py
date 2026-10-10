"""Step 3: concentration-discharge model for the headline cell, fitted on the pre-period."""

import pandas as pd
from cairn import censored_values, record

from animas import figures
from animas.analysis import FIGURES, HAC_LAGS, HEADLINE, PRIMARY, TABLES, cell_series, inclusion, load_samples
from animas.cq import fit_cq, flow_adjust, seasonal_amplitude

s = load_samples()
reach, constituent, fraction = HEADLINE
df = cell_series(s, reach, constituent, fraction)
censored_values(pd.Series(["<" + str(r) if c else str(v) for v, c, r in zip(df["value"], df["censored"], df["rl"], strict=True)],
                          name="headline_series"))
inc = inclusion(df, PRIMARY)
record("cq.headline.n_series_rows", int(len(df)))
record("cq.headline.n_without_discharge", int(df["n_no_q"].iloc[0]) if len(df) else 0)
record("cq.headline.estimable", bool(inc["estimable"]), note=inc["reason"] or "passes the inclusion rule")
record("cq.headline.n_pre", inc["n_pre"])
record("cq.headline.n_post", inc["n_post"])
record("cq.headline.share_censored_pre", round(inc["cens_pre"], 3))

pre_mask = ((df["date"] >= PRIMARY.pre_start) & (df["date"] < PRIMARY.release)).to_numpy()
fit = fit_cq(df, pre_mask, hac_lags=HAC_LAGS)
adj = flow_adjust(df, fit)
record("cq.headline.slope", round(fit.coef("log_q"), 3), note="d ln C / d ln Q, pre-period")
record("cq.headline.slope_se", round(fit.stderr("log_q"), 3))
lo, hi = fit.ci("log_q")
record("cq.headline.slope_lo", round(lo, 3))
record("cq.headline.slope_hi", round(hi, 3))
record("cq.headline.amp1", round(seasonal_amplitude(fit, 1), 3), note="annual harmonic amplitude, ln units")
record("cq.headline.amp2", round(seasonal_amplitude(fit, 2), 3))
record("cq.headline.sigma", round(fit.sigma, 3))
record("cq.headline.n_fit", fit.n)
record("cq.headline.n_fit_censored", fit.n_censored)
record("cq.headline.resid_sd_pre", round(float(adj.loc[pre_mask, "resid"].std()), 3))
record("cq.headline.resid_sd_post", round(float(adj.loc[adj["date"] > PRIMARY.plume_end, "resid"].std()), 3))
record("cq.headline.resid_mean_post", round(float(adj.loc[adj["date"] > PRIMARY.plume_end, "resid"].mean()), 3),
       note="raw post-period mean residual, before the ITS; descriptive only")
record("cq.headline.median_conc_pre", round(float(df.loc[pre_mask, "value"].median()), 0), unit="ug/L")
record("cq.headline.median_conc_post", round(float(df.loc[df["date"] > PRIMARY.plume_end, "value"].median()), 0), unit="ug/L")
record("cq.headline.median_q_pre", round(float(df.loc[pre_mask, "q_cfs"].median()), 1), unit="ft3/s")
record("cq.headline.median_q_post", round(float(df.loc[df["date"] > PRIMARY.plume_end, "q_cfs"].median()), 1), unit="ft3/s")
adj.to_csv(TABLES / "headline_flow_adjusted.csv", index=False)
daily = pd.read_csv("data/derived/discharge_daily.csv", parse_dates=["date"])
daily = daily[(daily["gauge"] == "USGS-09358550") & (daily["date"] <= PRIMARY.post_end)]
figures.timeseries_with_discharge(adj, daily, FIGURES / "timeseries_headline.png",
                                  "Dissolved zinc, Cement Creek at Silverton (Colorado River Watch) and USGS 09358550 discharge", "ug/L")
figures.cq_plot(adj, fit, PRIMARY, FIGURES / "cq_headline.png", "Dissolved zinc vs discharge, Cement Creek: pre- and post-release")
print("cq done")
