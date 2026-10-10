# Five-minute walkthrough

_Rendered from the ledger by `scripts/80_render_docs.py`; do not edit `walkthrough.md`._

**The question (30 s).** In August 2015 the Gold King Mine release sent three million
gallons of acidic, metal-laden water down Cement Creek into the Animas. The plume passed
in days. The interesting question is whether anything changed afterwards once you adjust
for how much water was flowing, and whether you could tell a release from a treatment
plant that started two months later.

**The trap (45 s).** Sampling surged after the release: at the four reaches from Silverton
to Durango, {{coverage.r4.events_per_year_pre}} metal sampling events a year before, then
{{coverage.r4.events_per_year_post2y}} a year in the two years after the treatment plant
started, with River Watch's share falling from {{coverage.r4.rw_share_pre:.0%}} to
{{coverage.r4.rw_share_post2y:.0%}}. Pool everything and the level change in Cement Creek
dissolved zinc comes out at {{explore.pooled.level_change_pct:.0f}} percent, about double
the single-organisation estimate. Much of that is a change in who sampled,
with what limits, at what times of year. So the confirmatory series use one organisation,
Colorado River Watch, which sampled monthly with one method from 2005 to 2025:
{{coverage.rw_events_pre}} events before, {{coverage.rw_events_post}} after.

**The method (60 s).** Pre-registered and frozen before fitting. Stage one: log
concentration against log discharge with two seasonal harmonics, fitted on the pre-period
by censored maximum likelihood, giving flow-adjusted residuals. Stage two: an interrupted
time series on those residuals with a pre-period slope, a level change and a slope change
at the release, the plume window excluded, Newey-West intervals with a
{{const.hac_lags}}-observation bandwidth. Non-detects stay censored; substitution is a
labelled sensitivity. The headline is dissolved zinc in Cement Creek,
{{its.headline.n}} samples.

**The headline (60 s).** Level change {{its.headline.level_change_pct:.0f}} percent,
interval {{its.headline.level_change_pct_lo:.0f}} to {{its.headline.level_change_pct_hi:.0f}},
p = {{its.headline.level_change_p:.2f}}. By the frozen rule: "{{its.headline.verdict}}".
Now the part that matters: start the pre-period in 2010 and it is
{{grid.pre2010.level_change_pct:.0f}} percent ({{grid.pre2010.level_change_pct_lo:.0f}} to
{{grid.pre2010.level_change_pct_hi:.0f}}); in 2013, {{grid.pre2013.level_change_pct:.0f}}
percent. The long pre-period carries a rising trend, {{its.headline.pre_slope_pct_per_yr:.1f}}
percent a year, the legacy of the Sunnyside bulkheads, and the counterfactual extrapolates
it. Stop the post-period at the end of 2016 and the sign flips to
{{grid.pre2005_plume20150930_post2016.level_change_pct:.0f}} percent: the first year after
the release was higher, not lower. The {{grid.n_fits}}-fit grid runs from
{{grid.pct_min:.0f}} to {{grid.pct_max:.0f}} percent.

**Attribution (60 s).** A change-point search that was never told the release date puts
its strongest split at {{cp.headline.strongest_month}}, {{cp.headline.strongest_rel_release_months}}
months before the release. On the series with {{explore.clean.n_rows_removed}} coding
artefacts removed, the strongest split is {{cp.explore.strongest_month}}:
{{cp.explore.strongest_rel_release_months}} months after the release and
{{cp.explore.strongest_rel_plant_months}} months after the plant started. The upstream
control, above the Gold King source, looks like it fell {{did.control_zinc.level_change_pct:.0f}}
percent too, but that is three zero-valued "non-detects" doing the work; cleaned, it is
{{explore.clean.control.level_change_pct:.0f}} percent. The difference-in-differences level
change is {{did.headline.level_change_pct:.0f}} percent with a differential downward slope
after 2015: relative to the control, Cement Creek stepped down and kept drifting down. Across {{mult.n_cells}} site-metal-fraction
cells, {{mult.n_bh_sig}} survive false-discovery control.

**The sentence to leave with (15 s).** A decline of about a fifth in flow-adjusted zinc
over the decade after 2015 is plausible; it is not detectable against the longest
pre-period, it did not start at the release, it is partly a decline relative to the
upstream control, and nothing in these series separates the release from the treatment
plant that started two months later. The
value of the study is that every one of those dependencies is on the table, pre-registered,
and reproducible from the committed snapshot.
