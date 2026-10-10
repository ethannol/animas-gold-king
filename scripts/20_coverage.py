"""Step 2: coverage and comparability description (one figure each), no model fits."""

import pandas as pd
from cairn import record

from animas import figures
from animas.analysis import FIGURES, REACHES, TABLES, load_samples
from animas.units import METALS

FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)
s = load_samples()
reaches_all = [*REACHES, "animas_cedar_hill"]
tab = figures.coverage(s, FIGURES / "coverage.png", reaches_all)
tab.to_csv(TABLES / "coverage_events_by_reach_year_org.csv", index=False)

metals = s[s["constituent"].isin(METALS)]
events = metals.drop_duplicates(["org", "site_id", "date", "time"])
pre = events["date"] < "2015-08-05"
post = events["date"] >= "2015-10-01"
record("coverage.n_orgs", int(s["org"].nunique()))
record("coverage.n_sites", int(s["site_id"].nunique()))
record("coverage.events_total", int(len(events)))
record("coverage.events_pre", int(pre.sum()), note="metal sampling events 2005-01-01 to 2015-08-04, all organisations")
record("coverage.events_post", int(post.sum()), note="metal sampling events from 2015-10-01, all organisations")
yrs_pre = (pd.Timestamp("2015-08-05") - pd.Timestamp("2005-01-01")).days / 365.25
yrs_post = (events["date"].max() - pd.Timestamp("2015-10-01")).days / 365.25
record("coverage.events_per_year_pre", round(pre.sum() / yrs_pre, 1))
record("coverage.events_per_year_post", round(post.sum() / yrs_post, 1))
record("coverage.events_per_year_ratio", round((post.sum() / yrs_post) / (pre.sum() / yrs_pre), 2))
rw = events[events["org"] == "CORIVWCH_WQX"]
record("coverage.rw_events", int(len(rw)))
record("coverage.rw_events_pre", int((rw["date"] < "2015-08-05").sum()))
record("coverage.rw_events_post", int((rw["date"] >= "2015-10-01").sum()))
record("coverage.rw_share_of_pre_events", round(float((rw["date"] < "2015-08-05").sum() / pre.sum()), 3))
record("coverage.rw_share_of_post_events", round(float((rw["date"] >= "2015-10-01").sum() / post.sum()), 3))
record("coverage.orgs_with_pre_events", int(events.loc[pre, "org"].nunique()))
record("coverage.orgs_with_post_events", int(events.loc[post, "org"].nunique()))
record("coverage.n_metal_results", int(len(metals)))
record("coverage.share_metal_results_censored", round(float(metals["censored"].mean()), 3))
record("coverage.n_methods", int(metals["method_id"].replace("", pd.NA).dropna().nunique()))
record("coverage.rw_method", str(metals.loc[metals["org"] == "CORIVWCH_WQX", "method_id"].mode().iloc[0]))

r4 = events[events["reach"].isin(REACHES)]
pre4 = r4["date"] < "2015-08-05"
post2 = (r4["date"] >= "2015-10-01") & (r4["date"] <= "2017-09-30")
post4 = r4["date"] >= "2015-10-01"
yrs_post4 = (r4["date"].max() - pd.Timestamp("2015-10-01")).days / 365.25
record("coverage.r4.events_per_year_pre", round(pre4.sum() / yrs_pre, 1),
       note="metal sampling events per year at the four River Watch reaches, 2005-01-01 to 2015-08-04")
record("coverage.r4.events_per_year_post2y", round(post2.sum() / 2.0, 1),
       note="same, 2015-10-01 to 2017-09-30 (the two years after the plant start)")
record("coverage.r4.events_per_year_post", round(post4.sum() / yrs_post4, 1))
record("coverage.r4.ratio_post2y", round((post2.sum() / 2.0) / (pre4.sum() / yrs_pre), 2))
record("coverage.r4.orgs_pre", int(r4.loc[pre4, "org"].nunique()))
record("coverage.r4.orgs_post2y", int(r4.loc[post2, "org"].nunique()))
record("coverage.r4.orgs_pre_steady", int((r4.loc[pre4].groupby("org").size() >= 100).sum()),
       note="organisations with at least 100 pre-period events at the four reaches")
record("coverage.r4.rw_share_pre", round(float((r4.loc[pre4, "org"] == "CORIVWCH_WQX").mean()), 3))
record("coverage.r4.rw_share_post2y", round(float((r4.loc[post2, "org"] == "CORIVWCH_WQX").mean()), 3))
cc = events[events["reach"] == "cement_creek"]
record("coverage.cc.events_per_year_pre", round((cc["date"] < "2015-08-05").sum() / yrs_pre, 1))
record("coverage.cc.events_per_year_post2y", round(((cc["date"] >= "2015-10-01") & (cc["date"] <= "2017-09-30")).sum() / 2.0, 1))

dl = figures.detection_limits(s, FIGURES / "detection_limits.png", METALS)
dl.to_csv(TABLES / "riverwatch_detection_limits_by_year.csv", index=False)
rwm = metals[(metals["org"] == "CORIVWCH_WQX")]
record("coverage.rw_rows_with_reported_limit", int((rwm["rl_source"] == "reported").sum()))
record("coverage.rw_rows_bound_assigned", int(rwm["rl_source"].isin(["min_detect_same_year", "earliest_recorded_rl"]).sum()))
record("coverage.rw_first_year_with_limits", int(rwm.loc[rwm["rl_source"] == "reported", "year"].min()))
zn = rwm[(rwm["constituent"] == "zinc") & (rwm["fraction"] == "dissolved") & (rwm["rl_source"] == "reported")]
record("coverage.rw_zinc_rl_min", float(zn["rl"].min()), unit="ug/L")
record("coverage.rw_zinc_rl_max", float(zn["rl"].max()), unit="ug/L")
cs = rwm.groupby(["constituent", "fraction"])["censored"].mean()
record("coverage.rw_arsenic_dissolved_censored", round(float(cs[("arsenic", "dissolved")]), 3))
record("coverage.rw_zinc_dissolved_censored", round(float(cs[("zinc", "dissolved")]), 3))
qc = pd.read_csv("data/derived/qc_samples.csv", low_memory=False)
record("coverage.n_qc_rows", int(len(qc)))
record("coverage.n_qc_replicates", int(qc["activity_type"].str.contains("Replicate").sum()))
record("coverage.n_qc_blanks", int(qc["activity_type"].str.contains("Blank").sum()))
# gaps: longest run of months without a River Watch sample at the headline station
rwcc = s[(s["org"] == "CORIVWCH_WQX") & (s["reach"] == "cement_creek")].drop_duplicates("date").sort_values("date")
gap = rwcc["date"].diff().dt.days.max()
record("coverage.rw_cement_longest_gap_days", int(gap))
record("coverage.rw_cement_events", int(len(rwcc)))
print("coverage done")
