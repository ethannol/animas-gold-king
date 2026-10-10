"""Step 6: difference-in-differences style check against the upstream control."""

import pandas as pd
from cairn import checked_merge, record

from animas.analysis import HAC_LAGS, PRIMARY, TABLES, cell_series, inclusion, load_samples
from animas.cq import fit_cq, flow_adjust
from animas.its import fit_its, select, summarise

s = load_samples()
CONTROL = "animas_above_cement"


def residuals(reach, constituent, fraction):
    d = cell_series(s, reach, constituent, fraction)
    pre = ((d["date"] >= PRIMARY.pre_start) & (d["date"] < PRIMARY.release)).to_numpy()
    fit = fit_cq(d, pre, hac_lags=HAC_LAGS)
    a = flow_adjust(d, fit)
    a["month"] = a["date"].dt.to_period("M").astype(str)
    a = a[~a["censored"]].drop_duplicates("month")  # uncensored, one per month
    return a[["month", "date", "resid"]]


rows = []
pairs = [("cement_creek", "zinc", "dissolved"), ("animas_below_silverton", "zinc", "dissolved")]
mult = pd.read_csv(TABLES / "multiplicity_grid.csv")
for _, c in mult[mult["estimable"] & (mult["reach"] != CONTROL)].iterrows():
    t = (c["reach"], c["constituent"], c["fraction"])
    if t not in pairs:
        pairs.append(t)
for reach, constituent, fraction in pairs:
    ctrl_ok = inclusion(cell_series(s, CONTROL, constituent, fraction), PRIMARY)["estimable"]
    if not ctrl_ok:
        rows.append({"reach": reach, "constituent": constituent, "fraction": fraction, "estimable": False,
                     "reason": "control cell not estimable"})
        continue
    imp = residuals(reach, constituent, fraction)
    ctl = residuals(CONTROL, constituent, fraction).rename(columns={"resid": "resid_control", "date": "date_control"})
    both = checked_merge(imp, ctl, on="month", expect="1:1", how="inner")
    both["resid"] = both["resid"] - both["resid_control"]
    both["censored"] = False
    both = both.sort_values("date").reset_index(drop=True)
    w = PRIMARY
    fit = fit_its(both, w, hac_lags=HAC_LAGS)
    sm = summarise(fit, select(both, w), w)
    rows.append({"reach": reach, "constituent": constituent, "fraction": fraction, "estimable": True, "reason": "",
                 "n_pairs": len(both), "n_impacted_months": len(imp), "n_control_months": len(ctl), **sm})
did = pd.DataFrame(rows)
did.to_csv(TABLES / "did_results.csv", index=False)
h = did.iloc[0]
record("did.headline.n_pairs", int(h["n_pairs"]), note="months with an uncensored residual at both Cement Creek and the control")
record("did.headline.share_months_paired", round(float(h["n_pairs"] / h["n_impacted_months"]), 3))
record("did.headline.level_change_pct", round(float(h["level_change_pct"]), 1))
record("did.headline.level_change_pct_lo", round(float(h["level_change_pct_lo"]), 1))
record("did.headline.level_change_pct_hi", round(float(h["level_change_pct_hi"]), 1))
record("did.headline.level_change_p", round(float(h["level_change_p"]), 4))
record("did.headline.slope_change_per_yr", round(float(h["slope_change_per_yr"]), 4))
record("did.headline.slope_change_p", round(float(h["slope_change_p"]), 4))
b = did.iloc[1]
record("did.below_silverton.n_pairs", int(b["n_pairs"]))
record("did.below_silverton.level_change_pct", round(float(b["level_change_pct"]), 1))
record("did.below_silverton.level_change_pct_lo", round(float(b["level_change_pct_lo"]), 1))
record("did.below_silverton.level_change_pct_hi", round(float(b["level_change_pct_hi"]), 1))
record("did.below_silverton.level_change_p", round(float(b["level_change_p"]), 4))
ctl_zn = mult[(mult["reach"] == CONTROL) & (mult["constituent"] == "zinc") & (mult["fraction"] == "dissolved")].iloc[0]
record("did.control_zinc.level_change_pct", round(float(ctl_zn["level_change_pct"]), 1),
       note="the upstream control's own ITS level change, dissolved zinc")
record("did.control_zinc.level_change_pct_lo", round(float(ctl_zn["level_change_pct_lo"]), 1))
record("did.control_zinc.level_change_pct_hi", round(float(ctl_zn["level_change_pct_hi"]), 1))
record("did.control_zinc.level_change_p", round(float(ctl_zn["level_change_p"]), 4))
e = did[did["estimable"] == True]  # noqa: E712
record("did.cells.n", int(len(e)))
record("did.cells.n_ci_excludes_zero", int(((e["level_change_lo"] > 0) | (e["level_change_hi"] < 0)).sum()))
record("did.cells.n_negative", int((e["level_change_pct"] < 0).sum()))
record("did.cells.n_not_estimable", int((did["estimable"] == False).sum()))  # noqa: E712
print("did done", h["level_change_pct"])
