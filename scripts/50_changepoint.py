"""Step 5: blind change-point search on monthly flow-adjusted residuals.

The stage-1 model here is fitted to the WHOLE period with no trend or step, so the
residual series carries no knowledge of the release date."""

import numpy as np
import pandas as pd
from cairn import record

from animas import figures
from animas.analysis import (
    FIGURES,
    HAC_LAGS,
    HEADLINE,
    PLANT_MONTH,
    PRIMARY,
    RELEASE_MONTH,
    TABLES,
    cell_series,
    implausible_rows,
    joined,
    load_samples,
    monthly_mean,
    months_between,
)
from animas.changepoint import binary_segmentation, pelt
from animas.cq import fit_cq, flow_adjust

s = load_samples()


def blind(df: pd.DataFrame) -> dict:
    d = df[(df["date"] >= PRIMARY.pre_start) & (df["date"] <= PRIMARY.post_end)].reset_index(drop=True)
    fit = fit_cq(d, np.ones(len(d), dtype=bool), hac_lags=HAC_LAGS)
    adj = flow_adjust(d, fit)
    m = monthly_mean(adj)
    x = m["resid"].to_numpy()
    cps = pelt(x)
    bs = binary_segmentation(x)
    out = {"n_months": len(m), "pelt": [str(m["month"].iloc[k]) for k in cps],
           "pelt_rel_release": [months_between(m["month"].iloc[k], RELEASE_MONTH) for k in cps],
           "pelt_rel_plant": [months_between(m["month"].iloc[k], PLANT_MONTH) for k in cps],
           "bs": [str(m["month"].iloc[k]) for k, _ in bs], "bs_gain": [g for _, g in bs],
           "strongest": str(m["month"].iloc[bs[0][0]]) if bs else "",
           "strongest_rel_release": months_between(m["month"].iloc[bs[0][0]], RELEASE_MONTH) if bs else np.nan,
           "strongest_rel_plant": months_between(m["month"].iloc[bs[0][0]], PLANT_MONTH) if bs else np.nan,
           "monthly": m, "cps_idx": cps, "bs_idx": [k for k, _ in bs], "converged": fit.converged}
    # mean shift across each PELT change-point
    bounds = [0, *cps, len(x)]
    out["segment_means"] = [float(x[a:b].mean()) for a, b in zip(bounds[:-1], bounds[1:], strict=True)]
    return out


reach, constituent, fraction = HEADLINE
df = cell_series(s, reach, constituent, fraction)
r = blind(df)
record("cp.headline.n_months", r["n_months"])
record("cp.headline.n_pelt", len(r["pelt"]))
record("cp.headline.pelt_months", joined(r["pelt"]))
record("cp.headline.pelt_rel_release_months", joined(r["pelt_rel_release"]),
       note="months after (+) or before (-) 2015-08 for each PELT change-point")
record("cp.headline.pelt_rel_plant_months", joined(r["pelt_rel_plant"]))
record("cp.headline.n_bs", len(r["bs"]))
record("cp.headline.bs_months", joined(r["bs"]))
record("cp.headline.strongest_month", r["strongest"] or "none")
record("cp.headline.strongest_rel_release_months", r["strongest_rel_release"])
record("cp.headline.strongest_rel_plant_months", r["strongest_rel_plant"])
record("cp.headline.strongest_within_3mo_of_release",
       bool(abs(r["strongest_rel_release"]) <= 3) if r["bs"] else False)
record("cp.headline.segment_means", joined(f"{v:+.2f}" for v in r["segment_means"]))
if len(r["segment_means"]) > 1:
    record("cp.headline.first_shift_pct", round(100 * (np.exp(r["segment_means"][1] - r["segment_means"][0]) - 1), 1),
           note="percent change in the flow-adjusted level across the first PELT change-point")
r["monthly"].assign(pelt_cp=False).to_csv(TABLES / "headline_monthly_residuals.csv", index=False)
figures.changepoint_plot(r["monthly"], r["cps_idx"], r["bs_idx"], FIGURES / "changepoints_headline.png",
                         "Blind change-point search, monthly flow-adjusted dissolved zinc at Cement Creek")

# every estimable cell from the multiplicity grid
mult = pd.read_csv(TABLES / "multiplicity_grid.csv")
rows = []
for _, c in mult[mult["estimable"]].iterrows():
    d = cell_series(s, c["reach"], c["constituent"], c["fraction"])
    rr = blind(d)
    rows.append({"reach": c["reach"], "constituent": c["constituent"], "fraction": c["fraction"],
                 "n_months": rr["n_months"], "n_pelt": len(rr["pelt"]), "pelt_months": joined(rr["pelt"]),
                 "pelt_rel_release": joined(rr["pelt_rel_release"]), "strongest": rr["strongest"],
                 "strongest_rel_release": rr["strongest_rel_release"], "strongest_rel_plant": rr["strongest_rel_plant"]})
cp = pd.DataFrame(rows)
cp.to_csv(TABLES / "changepoints_all_cells.csv", index=False)
has = cp[cp["strongest"] != ""]
record("cp.cells.n", int(len(cp)))
record("cp.cells.n_with_any", int(len(has)))
record("cp.cells.n_strongest_within_3mo_release", int((has["strongest_rel_release"].abs() <= 3).sum()))
record("cp.cells.n_strongest_within_12mo_release", int((has["strongest_rel_release"].abs() <= 12).sum()))
record("cp.cells.n_any_pelt_within_3mo_release",
       int(cp["pelt_rel_release"].apply(lambda t: any(abs(int(v)) <= 3 for v in t.split("; ") if v and v != "none")).sum()))
record("cp.cells.median_strongest_rel_release", float(has["strongest_rel_release"].median()) if len(has) else float("nan"),
       unit="months")
# EXPLORATORY: the same search with implausible rows removed (rule in analysis.implausible_rows)
bad = implausible_rows(df)
r2 = blind(df.loc[~bad].reset_index(drop=True))
record("cp.explore.n_rows_removed", int(bad.sum()), note="exploratory: rows below a tenth of the 5th percentile of detected values removed")
record("cp.explore.n_pelt", len(r2["pelt"]))
record("cp.explore.pelt_months", joined(r2["pelt"]))
record("cp.explore.pelt_rel_release_months", joined(r2["pelt_rel_release"]))
record("cp.explore.pelt_rel_plant_months", joined(r2["pelt_rel_plant"]))
record("cp.explore.strongest_month", r2["strongest"] or "none")
record("cp.explore.strongest_rel_release_months", r2["strongest_rel_release"])
record("cp.explore.strongest_rel_plant_months", r2["strongest_rel_plant"])
record("cp.explore.segment_means", joined(f"{v:+.2f}" for v in r2["segment_means"]))
if len(r2["segment_means"]) > 1:
    i = next((k for k, m in enumerate(r2["pelt_rel_release"]) if m >= 0), None)
    if i is not None:
        record("cp.explore.post_release_shift_pct",
               round(100 * (np.exp(r2["segment_means"][i + 1] - r2["segment_means"][i]) - 1), 1),
               note="percent shift in level across the first change-point at or after the release")
figures.changepoint_plot(r2["monthly"], r2["cps_idx"], r2["bs_idx"], FIGURES / "changepoints_headline_cleaned.png",
                         "EXPLORATORY: blind change-points with implausible rows removed, dissolved zinc at Cement Creek")
print("changepoints done", r["pelt"], r["strongest"], "| cleaned:", r2["pelt"])
