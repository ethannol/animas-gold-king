"""Step 4: interrupted time series. Headline cell, 27-fit sensitivity grid, 64-cell
multiplicity grid at the primary specification."""

import numpy as np
import pandas as pd
from cairn import record

from animas import figures
from animas.analysis import (
    FIGURES,
    FRACTIONS,
    HEADLINE,
    PRIMARY,
    REACHES,
    TABLES,
    bh_reject,
    cell_series,
    grid_windows,
    inclusion,
    load_samples,
    run_cell,
)
from animas.its import counterfactual, select
from animas.units import METALS

s = load_samples()
reach, constituent, fraction = HEADLINE
df = cell_series(s, reach, constituent, fraction)
record("const.ci_pct", 95, note="nominal coverage of every interval in the report")
record("const.hac_lags", 12, note="Newey-West Bartlett bandwidth, observations")
record("const.n_harmonics", 2)
record("const.min_pre", 60)
record("const.min_post", 36)
record("const.max_cens_pre_pct", 50)
record("const.fdr_pct", 5)
record("const.alpha", 0.05, note="raw significance threshold used only for counting")
record("const.implausible_quantile_pct", 5)
record("const.implausible_divisor", 10)

# --- headline, primary specification -------------------------------------------------
res = run_cell(df, PRIMARY)
sub = select(res["adj"], PRIMARY)
for k in ("n", "n_pre", "n_post", "n_censored", "level_change_log", "level_change_se", "level_change_lo",
          "level_change_hi", "level_change_pct", "level_change_pct_lo", "level_change_pct_hi", "level_change_p",
          "slope_change_per_yr", "slope_change_lo", "slope_change_hi", "slope_change_p", "pre_slope_per_yr",
          "pre_slope_se", "sigma", "hac_lags", "converged"):
    v = res[k]
    record(f"its.headline.{k}", round(float(v), 4) if isinstance(v, float | np.floating) else v)
record("its.headline.slope_change_pct_per_yr", round(100 * (np.exp(res["slope_change_per_yr"]) - 1), 2))
record("its.headline.pre_slope_pct_per_yr", round(100 * (np.exp(res["pre_slope_per_yr"]) - 1), 2))
pre_lo, pre_hi = res["its_fit"].ci("pre_slope")
record("its.headline.pre_slope_pct_per_yr_lo", round(100 * (np.exp(pre_lo) - 1), 2))
record("its.headline.pre_slope_pct_per_yr_hi", round(100 * (np.exp(pre_hi) - 1), 2))
cf = counterfactual(res["its_fit"], sub["date"], PRIMARY.release)
figures.its_plot(sub, res["its_fit"], PRIMARY, FIGURES / "its_headline.png",
                 "Interrupted time series on flow-adjusted dissolved zinc, Cement Creek", cf)
# implied change at the end of the post-period (level + slope change x years)
yrs_end = (PRIMARY.post_end - PRIMARY.release).days / 365.25
end_log = res["level_change_log"] + res["slope_change_per_yr"] * yrs_end
record("its.headline.years_post", round(yrs_end, 1))
record("its.headline.change_at_end_pct", round(100 * (np.exp(end_log) - 1), 1),
       note="level change plus slope change accumulated to the end of the post-period, point estimate only")

# --- sensitivity grid ------------------------------------------------------------------
rows = []
for w in grid_windows():
    r = run_cell(df, w)
    rows.append({k: v for k, v in r.items() if k not in ("adj", "cq_fit", "its_fit")})
grid = pd.DataFrame(rows)
grid.to_csv(TABLES / "sensitivity_grid_headline.csv", index=False)
for _, r in grid.iterrows():
    for k in ("level_change_pct", "level_change_pct_lo", "level_change_pct_hi", "level_change_p", "n"):
        record(f"grid.{r['window']}.{k}", round(float(r[k]), 3) if k != "n" else int(r[k]))
excl = (grid["level_change_lo"] > 0) | (grid["level_change_hi"] < 0)
record("grid.n_fits", int(len(grid)))
record("grid.n_ci_excludes_zero", int(excl.sum()))
record("grid.n_negative", int((grid["level_change_pct"] < 0).sum()))
record("grid.pct_min", round(float(grid["level_change_pct"].min()), 1))
record("grid.pct_max", round(float(grid["level_change_pct"].max()), 1))
prim_plume, prim_post = PRIMARY.plume_end.strftime("%Y-%m-%d"), PRIMARY.post_end.strftime("%Y-%m-%d")
by_pre = grid[(grid["plume_end"] == prim_plume) & (grid["post_end"] == prim_post)].set_index("pre_start")
for ps, r in by_pre.iterrows():
    record(f"grid.pre{ps[:4]}.level_change_pct", round(float(r["level_change_pct"]), 1))
    record(f"grid.pre{ps[:4]}.level_change_pct_lo", round(float(r["level_change_pct_lo"]), 1))
    record(f"grid.pre{ps[:4]}.level_change_pct_hi", round(float(r["level_change_pct_hi"]), 1))
    record(f"grid.pre{ps[:4]}.level_change_p", round(float(r["level_change_p"]), 4))
    record(f"grid.pre{ps[:4]}.pre_slope_pct_per_yr", round(100 * (np.exp(r["pre_slope_per_yr"]) - 1), 2))
    record(f"grid.pre{ps[:4]}.slope_change_per_yr", round(float(r["slope_change_per_yr"]), 4))
    record(f"grid.pre{ps[:4]}.slope_change_p", round(float(r["slope_change_p"]), 4))
    record(f"grid.pre{ps[:4]}.n_pre", int(r["n_pre"]))
same_sign_all = bool(((by_pre["level_change_lo"] > 0) | (by_pre["level_change_hi"] < 0)).all()
                     and by_pre["level_change_log"].apply(np.sign).nunique() == 1)
primary_excl = bool(by_pre.loc[PRIMARY.pre_start.strftime("%Y-%m-%d"), "level_change_lo"] > 0
                    or by_pre.loc[PRIMARY.pre_start.strftime("%Y-%m-%d"), "level_change_hi"] < 0)
if primary_excl and same_sign_all:
    verdict = "lasting change detected"
elif primary_excl:
    verdict = "change depends on the pre-period"
else:
    verdict = "no detectable lasting change"
record("its.headline.verdict", verdict, note="pre-registered rule 1-3 applied to the primary fit and the three pre-period starts")
record("its.headline.primary_ci_excludes_zero", primary_excl)
record("its.headline.all_pre_starts_agree", same_sign_all)
figures.sensitivity_grid(grid, FIGURES / "sensitivity_grid.png",
                         "Level change in flow-adjusted dissolved zinc at Cement Creek, by analysis choices")

# --- multiplicity grid: every reach x constituent x fraction at the primary spec -------
mrows = []
for rc in REACHES:
    for c in METALS:
        for f in FRACTIONS:
            d = cell_series(s, rc, c, f)
            inc = inclusion(d, PRIMARY)
            row = {"reach": rc, "constituent": c, "fraction": f, **{k: v for k, v in inc.items()}}
            if inc["estimable"]:
                try:
                    r = run_cell(d, PRIMARY)
                    row.update({k: v for k, v in r.items() if k not in ("adj", "cq_fit", "its_fit")})
                    if not (r["converged"] and r["cq_converged"]):
                        row["estimable"] = False
                        row["reason"] = "a stage did not converge"
                except (ValueError, np.linalg.LinAlgError) as e:
                    row["estimable"] = False
                    row["reason"] = f"fit failed: {e}"
            mrows.append(row)
mult = pd.DataFrame(mrows)
p = mult["level_change_p"].where(mult["estimable"], np.nan) if "level_change_p" in mult else pd.Series(np.nan, index=mult.index)
mult["bh_reject"] = bh_reject(p.to_numpy())
mult["raw_sig"] = mult["estimable"] & (p < 0.05)
mult.to_csv(TABLES / "multiplicity_grid.csv", index=False)
record("mult.n_cells", int(len(mult)))
record("mult.n_estimable", int(mult["estimable"].sum()))
record("mult.n_not_estimable", int((~mult["estimable"]).sum()))
record("mult.n_raw_sig", int(mult["raw_sig"].sum()), note="raw p < 0.05 among estimable cells")
record("mult.n_bh_sig", int(mult["bh_reject"].sum()), note="Benjamini-Hochberg at 5% FDR among estimable cells")
record("mult.n_bh_sig_negative", int((mult["bh_reject"] & (mult["level_change_pct"] < 0)).sum()))
record("mult.n_bh_sig_positive", int((mult["bh_reject"] & (mult["level_change_pct"] > 0)).sum()))
est = mult[mult["estimable"]]
record("mult.n_negative_point", int((est["level_change_pct"] < 0).sum()), note="estimable cells with a negative point estimate")
record("mult.median_pct", round(float(est["level_change_pct"].median()), 1))
record("mult.n_censoring_excluded", int(mult["reason"].str.contains("censored").sum()))
for rc in REACHES:
    e = est[est["reach"] == rc]
    record(f"mult.{rc}.n_estimable", int(len(e)))
    record(f"mult.{rc}.n_bh_sig", int(e["bh_reject"].sum()))
    record(f"mult.{rc}.n_negative", int((e["level_change_pct"] < 0).sum()))
    record(f"mult.{rc}.median_pct", round(float(e["level_change_pct"].median()), 1) if len(e) else float("nan"))
for _, r in mult.iterrows():
    key = f"mult.{r['reach']}.{r['constituent']}.{r['fraction']}"
    record(f"{key}.estimable", bool(r["estimable"]), note=r["reason"])
    if r["estimable"]:
        record(f"{key}.level_change_pct", round(float(r["level_change_pct"]), 1))
        record(f"{key}.level_change_pct_lo", round(float(r["level_change_pct_lo"]), 1))
        record(f"{key}.level_change_pct_hi", round(float(r["level_change_pct_hi"]), 1))
        record(f"{key}.level_change_p", round(float(r["level_change_p"]), 4))
        record(f"{key}.bh_reject", bool(r["bh_reject"]))
        record(f"{key}.n_rl_imputed", int(r["n_rl_imputed"]))
figures.multiplicity_grid(mult, FIGURES / "multiplicity_grid.png",
                          "Level change at the release, all reach x constituent x fraction cells (Colorado River Watch)", REACHES)
print("its done:", verdict)
