"""Step 7: EXPLORATORY checks, not pre-registered as confirmatory. Each is labelled so in
the report: substitution at half the limit; pooling every organisation; instantaneous
flow vs daily mean; the USGS quarterly series below Silverton."""

import numpy as np
import pandas as pd
from cairn import checked_merge, record

from animas.analysis import (
    HAC_LAGS,
    HEADLINE,
    PRIMARY,
    TABLES,
    bh_reject,
    cell_series,
    implausible_rows,
    inclusion,
    load_samples,
    run_cell,
)
from animas.cq import fit_cq, flow_adjust
from animas.its import fit_its, select, summarise

s = load_samples()
reach, constituent, fraction = HEADLINE

# 1. substitution at half the reporting limit, every estimable cell
mult = pd.read_csv(TABLES / "multiplicity_grid.csv")
rows = []
for _, c in mult[mult["estimable"]].iterrows():
    d = cell_series(s, c["reach"], c["constituent"], c["fraction"])
    d["log_c"] = np.where(d["censored"], np.log(d["rl"] / 2.0), d["log_c"])
    d["censored"] = False
    r = run_cell(d, PRIMARY)
    rows.append({"reach": c["reach"], "constituent": c["constituent"], "fraction": c["fraction"],
                 "n_censored": int(c["n_cens_pre"] + c["n_cens_post"]),
                 "censored_method_pct": c["level_change_pct"], "half_rl_pct": r["level_change_pct"],
                 "diff_pct_points": r["level_change_pct"] - c["level_change_pct"]})
sub = pd.DataFrame(rows)
sub.to_csv(TABLES / "exploratory_half_rl_substitution.csv", index=False)
record("explore.halfrl.n_cells", int(len(sub)))
record("explore.halfrl.max_abs_diff_pct_points", round(float(sub["diff_pct_points"].abs().max()), 1))
record("explore.halfrl.headline_diff_pct_points",
       round(float(sub[(sub["reach"] == reach) & (sub["constituent"] == constituent) & (sub["fraction"] == fraction)]["diff_pct_points"].iloc[0]), 2))

# 2. pooling all organisations at the headline reach
pooled = cell_series(s, reach, constituent, fraction, org=None)
inc = inclusion(pooled, PRIMARY)
r = run_cell(pooled, PRIMARY)
record("explore.pooled.n_orgs", int(pooled["org"].nunique()))
record("explore.pooled.n", int(r["n"]))
record("explore.pooled.n_pre", int(inc["n_pre"]))
record("explore.pooled.n_post", int(inc["n_post"]))
record("explore.pooled.level_change_pct", round(float(r["level_change_pct"]), 1))
record("explore.pooled.level_change_pct_lo", round(float(r["level_change_pct_lo"]), 1))
record("explore.pooled.level_change_pct_hi", round(float(r["level_change_pct_hi"]), 1))
record("explore.pooled.level_change_p", round(float(r["level_change_p"]), 4))
post_orgs = pooled.loc[pooled["date"] > PRIMARY.plume_end, "org"].value_counts()
record("explore.pooled.share_post_rows_non_riverwatch", round(float(1 - post_orgs.get("CORIVWCH_WQX", 0) / post_orgs.sum()), 3))

# 3. instantaneous flow recorded with the sample vs the daily mean at the gauge
flow = pd.read_csv("data/derived/sample_flow.csv", parse_dates=["date"], low_memory=False)
flow = flow[flow["value"] > 0].drop_duplicates(["org", "site_id", "date", "time"])
daily = pd.read_csv("data/derived/discharge_daily.csv", parse_dates=["date"])
f = checked_merge(flow, daily[["gauge", "date", "q_cfs"]], on=["gauge", "date"], expect="m:1", how="inner")
f = f[f["q_cfs"] > 0]
lr = np.log(f["value"]) - np.log(f["q_cfs"])
record("explore.flow.n_pairs", int(len(f)), note="samples with an instantaneous discharge and a daily mean on the same day")
record("explore.flow.corr_log", round(float(np.corrcoef(np.log(f["value"]), np.log(f["q_cfs"]))[0, 1]), 3))
record("explore.flow.median_abs_log_ratio", round(float(lr.abs().median()), 3))
record("explore.flow.p90_abs_log_ratio", round(float(lr.abs().quantile(0.9)), 3))
record("explore.flow.n_orgs", int(f["org"].nunique()))

# 4. USGS quarterly series, Animas below Silverton, dissolved zinc (below the inclusion rule)
u = cell_series(s, "animas_below_silverton", "zinc", "dissolved", org="USGS-CO")
inc = inclusion(u, PRIMARY)
record("explore.usgs.n_pre", inc["n_pre"])
record("explore.usgs.n_post", inc["n_post"])
record("explore.usgs.estimable_by_rule", bool(inc["estimable"]), note=inc["reason"])
try:
    r = run_cell(u, PRIMARY)
    record("explore.usgs.level_change_pct", round(float(r["level_change_pct"]), 1))
    record("explore.usgs.level_change_pct_lo", round(float(r["level_change_pct_lo"]), 1))
    record("explore.usgs.level_change_pct_hi", round(float(r["level_change_pct_hi"]), 1))
    record("explore.usgs.level_change_p", round(float(r["level_change_p"]), 4))
except ValueError as e:
    record("explore.usgs.level_change_pct", float("nan"), note=str(e))
# 5. headline refit with implausible rows removed (see analysis.implausible_rows)
d = cell_series(s, reach, constituent, fraction)
bad = implausible_rows(d)
r = run_cell(d.loc[~bad].reset_index(drop=True), PRIMARY)
record("explore.clean.n_rows_removed", int(bad.sum()))
record("explore.clean.level_change_pct", round(float(r["level_change_pct"]), 1))
record("explore.clean.level_change_pct_lo", round(float(r["level_change_pct_lo"]), 1))
record("explore.clean.level_change_pct_hi", round(float(r["level_change_pct_hi"]), 1))
record("explore.clean.level_change_p", round(float(r["level_change_p"]), 4))
record("explore.clean.sigma", round(float(r["sigma"]), 3))
record("explore.clean.pre_slope_pct_per_yr", round(100 * (np.exp(r["pre_slope_per_yr"]) - 1), 2))
record("explore.clean.slope_change_per_yr", round(float(r["slope_change_per_yr"]), 4))
record("explore.clean.slope_change_p", round(float(r["slope_change_p"]), 4))

# 5b. the control cell and the difference-in-differences, cleaned the same way
ctl = cell_series(s, "animas_above_cement", constituent, fraction)
bad_c = implausible_rows(ctl)
rc = run_cell(ctl.loc[~bad_c].reset_index(drop=True), PRIMARY)
record("explore.clean.control.n_rows_removed", int(bad_c.sum()))
record("explore.clean.control.level_change_pct", round(float(rc["level_change_pct"]), 1))
record("explore.clean.control.level_change_pct_lo", round(float(rc["level_change_pct_lo"]), 1))
record("explore.clean.control.level_change_pct_hi", round(float(rc["level_change_pct_hi"]), 1))
record("explore.clean.control.level_change_p", round(float(rc["level_change_p"]), 4))
record("explore.clean.control.sigma", round(float(rc["sigma"]), 3))


def clean_resid(df):
    d = df.loc[~implausible_rows(df)].reset_index(drop=True)
    pre = ((d["date"] >= PRIMARY.pre_start) & (d["date"] < PRIMARY.release)).to_numpy()
    a = flow_adjust(d, fit_cq(d, pre, hac_lags=HAC_LAGS))
    a["month"] = a["date"].dt.to_period("M").astype(str)
    return a[~a["censored"]].drop_duplicates("month")[["month", "date", "resid"]]


imp = clean_resid(d)
ctl_r = clean_resid(ctl).rename(columns={"resid": "resid_control", "date": "date_control"})
both = checked_merge(imp, ctl_r, on="month", expect="1:1", how="inner")
both["resid"] = both["resid"] - both["resid_control"]
both["censored"] = False
both = both.sort_values("date").reset_index(drop=True)
fit = fit_its(both, PRIMARY, hac_lags=HAC_LAGS)
sm = summarise(fit, select(both, PRIMARY), PRIMARY)
record("explore.clean.did.n_pairs", int(len(both)))
record("explore.clean.did.level_change_pct", round(float(sm["level_change_pct"]), 1))
record("explore.clean.did.level_change_pct_lo", round(float(sm["level_change_pct_lo"]), 1))
record("explore.clean.did.level_change_pct_hi", round(float(sm["level_change_pct_hi"]), 1))
record("explore.clean.did.level_change_p", round(float(sm["level_change_p"]), 4))
record("explore.clean.did.slope_change_per_yr", round(float(sm["slope_change_per_yr"]), 4))
record("explore.clean.did.slope_change_p", round(float(sm["slope_change_p"]), 4))

# 5c. the whole multiplicity grid, cleaned
rows = []
for _, c in mult[mult["estimable"]].iterrows():
    dd = cell_series(s, c["reach"], c["constituent"], c["fraction"])
    bad = implausible_rows(dd)
    r = run_cell(dd.loc[~bad].reset_index(drop=True), PRIMARY)
    rows.append({"reach": c["reach"], "constituent": c["constituent"], "fraction": c["fraction"],
                 "n_removed": int(bad.sum()), "prereg_pct": c["level_change_pct"], "clean_pct": r["level_change_pct"],
                 "clean_pct_lo": r["level_change_pct_lo"], "clean_pct_hi": r["level_change_pct_hi"],
                 "clean_p": r["level_change_p"], "prereg_sigma": c["sigma"], "clean_sigma": r["sigma"]})
cg = pd.DataFrame(rows)
cg["bh_reject"] = bh_reject(cg["clean_p"].to_numpy())
cg.to_csv(TABLES / "exploratory_cleaned_grid.csv", index=False)
record("explore.clean.grid.n_cells", int(len(cg)))
record("explore.clean.grid.n_cells_with_removed", int((cg["n_removed"] > 0).sum()))
record("explore.clean.grid.n_rows_removed_total", int(cg["n_removed"].sum()))
record("explore.clean.grid.n_raw_sig", int((cg["clean_p"] < 0.05).sum()))
record("explore.clean.grid.n_bh_sig", int(cg["bh_reject"].sum()))
record("explore.clean.grid.n_bh_sig_negative", int((cg["bh_reject"] & (cg["clean_pct"] < 0)).sum()))
record("explore.clean.grid.median_pct", round(float(cg["clean_pct"].median()), 1))
record("explore.clean.grid.n_negative", int((cg["clean_pct"] < 0).sum()))
record("explore.clean.grid.max_abs_shift_pct_points", round(float((cg["clean_pct"] - cg["prereg_pct"]).abs().max()), 1))
record("explore.clean.grid.median_sigma_ratio", round(float((cg["clean_sigma"] / cg["prereg_sigma"]).median()), 2),
       note="median ratio of the residual scale after to before removing implausible rows")
sig_cells = cg[cg["bh_reject"]]
record("explore.clean.grid.bh_sig_cells", "; ".join(f"{r.reach}/{r.constituent}/{r.fraction} {r.clean_pct:+.0f}%" for r in sig_cells.itertuples()) or "none")
print("exploratory done")
