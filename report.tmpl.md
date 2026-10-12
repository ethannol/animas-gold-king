# Animas River after Gold King: a flow-adjusted interrupted time series

_Rendered by `cairn render`; every figure below is a ledger value. Do not edit `reports/report.md`._

## Question

After adjusting for discharge and season, did metal concentrations in Cement Creek at
Silverton and in the Animas River change in a lasting way after the Gold King Mine
release of 2015-08-05, and can any change be attributed to the release rather than to what
came after it, above all the Gladstone interim treatment plant that has treated the Gold King
discharge since October 2015? The pre-registered headline is one series: dissolved zinc in
Cement Creek, sampled monthly by Colorado River Watch, paired with daily mean discharge at
USGS gauge `09358550`.

**Answer.** Under the pre-registered primary specification the flow-adjusted level of
dissolved zinc in Cement Creek after the release is {{its.headline.level_change_pct:.0f}}
percent relative to the continued pre-period trend (interval
{{its.headline.level_change_pct_lo:.0f}} to {{its.headline.level_change_pct_hi:.0f}}
percent, p = {{its.headline.level_change_p:.2f}}, n = {{its.headline.n}} samples).
The pre-registered rule returns "{{its.headline.verdict}}". That verdict is fragile in a
specific, documented way: with the pre-period starting in 2010 or 2013 instead of 2005 the
same model gives {{grid.pre2010.level_change_pct:.0f}} percent
({{grid.pre2010.level_change_pct_lo:.0f}} to {{grid.pre2010.level_change_pct_hi:.0f}}) and
{{grid.pre2013.level_change_pct:.0f}} percent ({{grid.pre2013.level_change_pct_lo:.0f}} to
{{grid.pre2013.level_change_pct_hi:.0f}}), both excluding zero, and with the post-period cut
at the end of 2016 the sign flips to {{grid.pre2005_plume20150930_post2016.level_change_pct:.0f}}
percent ({{grid.pre2005_plume20150930_post2016.level_change_pct_lo:.0f}} to
{{grid.pre2005_plume20150930_post2016.level_change_pct_hi:.0f}}). The blind change-point
search puts its strongest split at {{cp.headline.strongest_month}},
{{cp.headline.strongest_rel_release_months}} months from the release; on the series with
three coding artefacts removed (exploratory) the strongest split is {{cp.explore.strongest_month}},
{{cp.explore.strongest_rel_release_months}} months after the release and
{{cp.explore.strongest_rel_plant_months}} months after the treatment plant start. Across all
{{mult.n_cells}} reach-constituent-fraction cells, {{mult.n_raw_sig}} have a raw p below
{{const.alpha}} and {{mult.n_bh_sig}} survive false-discovery control. The honest summary is: a
decline in flow-adjusted zinc of roughly a fifth is plausible over the decade after 2015, it
is not detectable against the longest pre-period, it did not begin at the release, and
nothing in these series separates the release from the treatment plant that started two
months later.

All intervals in this report are two-sided with nominal coverage of {{const.ci_pct}}
percent, from a Newey-West sandwich with a Bartlett bandwidth of {{const.hac_lags}}
observations. Percent changes are `exp(level change) - 1` on the natural-log scale.

## Data and comparability

- Snapshot downloaded {{snapshot.download_date}}: {{snapshot.wqp_result_rows}} Water
  Quality Portal result rows ({{snapshot.wqp_nwis_rows}} USGS NWIS, {{snapshot.wqp_storet_rows}}
  WQX/STORET) for {{snapshot.wqp_sites}} stations grouped into five reaches, and
  {{snapshot.daily_rows_total}} daily mean discharge values for {{snapshot.n_gauges}} gauges
  from the USGS Water Data API (version {{snapshot.api_version}}). The same query on the
  portal's WQX3 profile returned {{snapshot.wqx3_rows}} rows, i.e. it dropped all
  {{snapshot.wqx3_missing_rows}} USGS rows; the legacy `resultPhysChem` profile is the
  complete one for this period.
- One raw row is one result (characteristic, fraction) from one sampling activity at one
  station. After the exclusion log ({{prepare.excluded_rows}} rows excluded with a rule
  each; {{prepare.qc_rows}} quality-control rows and {{prepare.flow_rows}} instantaneous-flow
  rows kept in separate tables) the sample table holds {{prepare.sample_rows}} rows from
  {{prepare.n_orgs}} organisations at {{prepare.n_sites_with_data}} stations,
  {{prepare.first_date}} to {{prepare.last_date}}. Every sample date had a daily discharge
  value at its gauge.
- Sampling intensity: at the four reaches from Silverton to Durango, metal sampling ran at
  {{coverage.r4.events_per_year_pre}} events per year before the release and
  {{coverage.r4.events_per_year_post2y}} per year in the two years after the treatment plant
  started ({{coverage.r4.ratio_post2y}} times), settling to {{coverage.r4.events_per_year_post}}
  per year over the whole post-period. Of the {{coverage.r4.orgs_pre}} organisations with
  pre-period samples only {{coverage.r4.orgs_pre_steady}} sampled steadily; Colorado River
  Watch supplied {{coverage.r4.rw_share_pre:.0%}} of pre-period events and
  {{coverage.r4.rw_share_post2y:.0%}} of events in those two post years, while staying at
  {{coverage.rw_events_pre}} events before and {{coverage.rw_events_post}} after with one
  method ({{coverage.rw_method}}) throughout (figure `reports/figures/coverage.png`). At
  Cement Creek alone the rate went from {{coverage.cc.events_per_year_pre}} to
  {{coverage.cc.events_per_year_post2y}} events per year. That is why the confirmatory
  series use River Watch only; pooling organisations is reported below as exploratory.
- Censoring: {{prepare.n_censored}} of {{prepare.sample_rows}} rows are non-detects
  ({{prepare.share_censored:.1%}}). River Watch recorded reporting limits only from
  {{coverage.rw_first_year_with_limits}}; {{coverage.rw_rows_bound_assigned}} earlier
  non-detects received a bound by the pre-registered rule and are flagged. Reporting limits
  changed over time (figure `reports/figures/detection_limits.png`): dissolved arsenic is
  {{coverage.rw_arsenic_dissolved_censored:.0%}} censored and is not estimable anywhere;
  dissolved zinc is {{coverage.rw_zinc_dissolved_censored:.1%}} censored.
- Dissolved and total fractions are separate series throughout.

## Method

Pre-registered in `docs/prereg.md` (frozen before any fit). Stage one: for each series,
`log C = a + b log Q + seasonal harmonics` ({{const.n_harmonics}} harmonics) fitted on the
pre-period by left-censored maximum likelihood; the residual, or its bound for a non-detect,
is the flow-adjusted series. Stage two: an interrupted time series on that series with a
pre-period slope, a level change and a slope change at the release, the plume window
excluded, censored rows kept as censored, Newey-West uncertainty. The headline cell has
{{cq.headline.n_pre}} pre-period and {{cq.headline.n_post}} post-period samples; its
concentration-discharge slope is {{cq.headline.slope:.2f}} ({{cq.headline.slope_lo:.2f}} to
{{cq.headline.slope_hi:.2f}}) and its annual seasonal amplitude {{cq.headline.amp1:.2f}}
log units (figure `reports/figures/cq_headline.png`). A cell is estimable with at least
{{const.min_pre}} pre and {{const.min_post}} post samples and at most
{{const.max_cens_pre_pct}} percent pre-period censoring.

## Result: the headline cell

Figure `reports/figures/its_headline.png` shows the fit; `reports/figures/timeseries_headline.png`
the raw series with discharge.

- Level change at the release: {{its.headline.level_change_pct:.1f}} percent
  ({{its.headline.level_change_pct_lo:.1f}} to {{its.headline.level_change_pct_hi:.1f}};
  p = {{its.headline.level_change_p:.3f}}).
- Pre-period trend: {{its.headline.pre_slope_pct_per_yr:.1f}} percent per year
  ({{its.headline.pre_slope_pct_per_yr_lo:.1f}} to {{its.headline.pre_slope_pct_per_yr_hi:.1f}}):
  flow-adjusted zinc was rising through the pre-period, as expected after the Sunnyside
  bulkheads. The counterfactual extrapolates that rise.
- Slope change after the release: {{its.headline.slope_change_pct_per_yr:.1f}} percent per
  year (p = {{its.headline.slope_change_p:.2f}}). Level and slope together put the series
  {{its.headline.change_at_end_pct:.0f}} percent below the counterfactual at the end of
  {{its.headline.years_post}} post-release years, a point estimate whose uncertainty grows
  with the extrapolation.
- Median dissolved zinc was {{cq.headline.median_conc_pre:.0f}} ug/L before and
  {{cq.headline.median_conc_post:.0f}} ug/L after, at median discharges of
  {{cq.headline.median_q_pre}} and {{cq.headline.median_q_post}} ft3/s: the raw drop is
  larger than the flow-adjusted one.
- Pre-registered conclusion: **{{its.headline.verdict}}** (primary interval excludes zero:
  {{its.headline.primary_ci_excludes_zero}}; all three pre-period starts agree:
  {{its.headline.all_pre_starts_agree}}).

## How the answer depends on the choices

The grid of {{grid.n_fits}} fits (figure `reports/figures/sensitivity_grid.png`, table
`reports/tables/sensitivity_grid_headline.csv`) spans {{grid.pct_min:.0f}} to
{{grid.pct_max:.0f}} percent; {{grid.n_ci_excludes_zero}} of {{grid.n_fits}} intervals
exclude zero and {{grid.n_negative}} of {{grid.n_fits}} point estimates are negative.

| Pre-period start | Level change, percent | Interval | p | Pre-slope, percent per year |
|---|---|---|---|---|
| 2005 (primary) | {{grid.pre2005.level_change_pct:.0f}} | {{grid.pre2005.level_change_pct_lo:.0f}} to {{grid.pre2005.level_change_pct_hi:.0f}} | {{grid.pre2005.level_change_p:.3f}} | {{grid.pre2005.pre_slope_pct_per_yr:.1f}} |
| 2010 | {{grid.pre2010.level_change_pct:.0f}} | {{grid.pre2010.level_change_pct_lo:.0f}} to {{grid.pre2010.level_change_pct_hi:.0f}} | {{grid.pre2010.level_change_p:.3f}} | {{grid.pre2010.pre_slope_pct_per_yr:.1f}} |
| 2013 | {{grid.pre2013.level_change_pct:.0f}} | {{grid.pre2013.level_change_pct_lo:.0f}} to {{grid.pre2013.level_change_pct_hi:.0f}} | {{grid.pre2013.level_change_p:.3f}} | {{grid.pre2013.pre_slope_pct_per_yr:.1f}} |

The point estimate barely moves; the interval does. The 2005 start carries the rising
pre-period trend and the 2007 and 2009 artefacts described under exploratory findings, which
widen the interval; the shorter pre-periods have flatter trends and tighter intervals.
The post-period end matters more than the pre-period start: ending in 2016 the level
change is {{grid.pre2005_plume20150930_post2016.level_change_pct:.0f}} percent
(p = {{grid.pre2005_plume20150930_post2016.level_change_p:.2f}}), ending in 2018
{{grid.pre2005_plume20150930_post2018.level_change_pct:.0f}} percent
(p = {{grid.pre2005_plume20150930_post2018.level_change_p:.2f}}), ending in 2025
{{grid.pre2005_plume20150930_post2025.level_change_pct:.0f}} percent. The first year after
the release was higher than the counterfactual, not lower; the decline accrues over years.
Widening the plume window to the end of 2015 removes those higher autumn samples and gives
{{grid.pre2005_plume20151231_post2025.level_change_pct:.0f}} percent
({{grid.pre2005_plume20151231_post2025.level_change_pct_lo:.0f}} to
{{grid.pre2005_plume20151231_post2025.level_change_pct_hi:.0f}}).

## Blind change-points

On the monthly flow-adjusted series fitted without any knowledge of the release date
(figure `reports/figures/changepoints_headline.png`), PELT finds {{cp.headline.n_pelt}}
change-points at {{cp.headline.pelt_months}}, that is {{cp.headline.pelt_rel_release_months}}
months relative to the release and {{cp.headline.pelt_rel_plant_months}} months relative to
the plant start. The strongest single split is {{cp.headline.strongest_month}}
({{cp.headline.strongest_rel_release_months}} months from the release), so by the
pre-registered rule the change is **not attributable to the release**. Three of the splits
are driven by implausible rows in 2007 and 2009 (see exploratory findings); with those
removed (figure `reports/figures/changepoints_headline_cleaned.png`) PELT finds
{{cp.explore.n_pelt}} change-points at {{cp.explore.pelt_months}}, that is
{{cp.explore.pelt_rel_release_months}} months from the release and
{{cp.explore.pelt_rel_plant_months}} months from the plant start. The strongest is
{{cp.explore.strongest_month}}, with a level shift of {{cp.explore.post_release_shift_pct:.0f}}
percent across it; the segment before it, which begins late in 2014, is the most elevated
in the series (segment means {{cp.explore.segment_means}}). A split a few months after both
events is what a treatment plant that started in October 2015 would produce; it is also
what a slowly developing post-release change would produce. The series cannot tell them
apart, and the elevated year before the release says the pre-release baseline was not
stable either. Across the {{cp.cells.n}} estimable cells, {{cp.cells.n_strongest_within_3mo_release}}
have their strongest split within three months of the release and
{{cp.cells.n_any_pelt_within_3mo_release}} have any split within three months of it.

## The upstream control

The Animas above Cement Creek, upstream of the Gold King source, shows a pre-registered
dissolved-zinc level change of {{did.control_zinc.level_change_pct:.0f}} percent
({{did.control_zinc.level_change_pct_lo:.0f}} to {{did.control_zinc.level_change_pct_hi:.0f}},
p = {{did.control_zinc.level_change_p:.2f}}). That number is not what it seems: the control
series carries {{explore.clean.control.n_rows_removed}} zero-valued "non-detects" with
bounds far below anything the stream has measured, two of them in the post-period, and the
censored model takes them at face value. Without them (exploratory) the control's level
change is {{explore.clean.control.level_change_pct:.0f}} percent
({{explore.clean.control.level_change_pct_lo:.0f}} to {{explore.clean.control.level_change_pct_hi:.0f}},
p = {{explore.clean.control.level_change_p:.2f}}).

The pre-registered difference-in-differences series (Cement Creek residual minus the same
month's control residual, uncensored pairs only, {{did.headline.n_pairs}} paired months)
has a level change of {{did.headline.level_change_pct:.0f}} percent
({{did.headline.level_change_pct_lo:.0f}} to {{did.headline.level_change_pct_hi:.0f}},
p = {{did.headline.level_change_p:.3f}}) and a slope change of
{{did.headline.slope_change_per_yr:.3f}} log units per year (p = {{did.headline.slope_change_p:.4f}});
cleaned the same way it is {{explore.clean.did.level_change_pct:.0f}} percent
({{explore.clean.did.level_change_pct_lo:.0f}} to {{explore.clean.did.level_change_pct_hi:.0f}},
slope change {{explore.clean.did.slope_change_per_yr:.3f}} per year,
p = {{explore.clean.did.slope_change_p:.4f}}). For the Animas below Silverton the paired level
change is {{did.below_silverton.level_change_pct:.0f}} percent
({{did.below_silverton.level_change_pct_lo:.0f}} to {{did.below_silverton.level_change_pct_hi:.0f}}).
Relative to the upstream control, Cement Creek stepped down and then kept drifting down
through the post-period. That pattern is consistent with treatment at Gladstone and with
the Superfund-era source control in the Cement Creek basin, and it is not the signature of
a one-day release; the control check rules out a watershed-wide driver as the whole
explanation but cannot rule in the release.

## Multiplicity

{{mult.n_cells}} cells were fitted at the primary specification (figure
`reports/figures/multiplicity_grid.png`, table `reports/tables/multiplicity_grid.csv`):
{{mult.n_estimable}} estimable, {{mult.n_not_estimable}} not (all for pre-period censoring
above the threshold: every arsenic series and most dissolved lead). Of the estimable
cells {{mult.n_negative_point}} have negative point estimates (median
{{mult.median_pct:.0f}} percent), {{mult.n_raw_sig}} have raw p below {{const.alpha}}, and
{{mult.n_bh_sig}} survive Benjamini-Hochberg control at {{const.fdr_pct}} percent false
discovery rate. No single cell is reported as a finding; the pattern is a broad, modest,
mostly non-significant decline at all four reaches including the control.

## Caveats next to the claims they affect

- The level-change interval in the headline cell is wide because the pre-period residuals
  carry three rows that are almost certainly coding artefacts (two zero-valued "non-detects"
  and one value far below anything else the stream has measured). The pre-registration
  treats them as censored at a bound; the exploratory refit without them is reported below,
  keeps the sign, and tightens the interval enough to exclude zero. The pre-registered
  verdict stands as the confirmatory answer; the cleaned estimate is the one a second
  study should pre-register.
- Stage-two uncertainty does not propagate stage-one estimation error; intervals are
  somewhat too narrow for that reason, and the autocorrelation bandwidth is a fixed choice.
- "Flow-adjusted" means adjusted for the daily mean at the gauge, not the instantaneous
  discharge at sampling; the exploratory check below shows the two agree closely.
- Reporting limits for several metals rose after 2019; this matters for the censored
  constituents, not for zinc at Cement Creek.
- The analysis describes measured concentrations only. It makes no claim about health,
  ecology, compliance or liability, and it cannot attribute any change to the release.

## Exploratory findings (not pre-registered)

- Removing the {{explore.clean.n_rows_removed}} implausible rows from the headline series
  (rule, decided after the freeze: a value or bound below a tenth of the series'
  {{const.implausible_quantile_pct}}th percentile of detected values) gives a level change
  of {{explore.clean.level_change_pct:.0f}} percent ({{explore.clean.level_change_pct_lo:.0f}}
  to {{explore.clean.level_change_pct_hi:.0f}}, p = {{explore.clean.level_change_p:.3f}}),
  with the residual scale falling from {{its.headline.sigma:.2f}} to {{explore.clean.sigma:.2f}}
  and the pre-period slope from {{its.headline.pre_slope_pct_per_yr:.1f}} to
  {{explore.clean.pre_slope_pct_per_yr:.1f}} percent per year. The same rule applied to all
  {{explore.clean.grid.n_cells}} estimable cells touches {{explore.clean.grid.n_cells_with_removed}}
  of them ({{explore.clean.grid.n_rows_removed_total}} rows in all), leaves the median residual
  scale unchanged (median ratio {{explore.clean.grid.median_sigma_ratio}}) while cutting it
  sharply in the cells that carry artefacts, moves a point
  estimate by at most {{explore.clean.grid.max_abs_shift_pct_points:.0f}} points, and leaves
  {{explore.clean.grid.n_raw_sig}} cells with raw p below {{const.alpha}} and {{explore.clean.grid.n_bh_sig}}
  surviving false-discovery control. This is the
  single largest lesson of the study for the censoring rule: a qualifier-coded zero is not
  always a non-detect.
- Pooling all {{explore.pooled.n_orgs}} organisations at Cement Creek, where
  {{explore.pooled.share_post_rows_non_riverwatch:.0%}} of post-release rows come from
  programmes that did not exist before the release, gives {{explore.pooled.level_change_pct:.0f}}
  percent ({{explore.pooled.level_change_pct_lo:.0f}} to {{explore.pooled.level_change_pct_hi:.0f}}):
  the composition change roughly doubles the apparent decline. This is the trap the single-
  organisation design avoids.
- Substituting half the limit for non-detects moves the headline by
  {{explore.halfrl.headline_diff_pct_points:.1f}} percentage points; across all
  {{explore.halfrl.n_cells}} estimable cells the largest move is
  {{explore.halfrl.max_abs_diff_pct_points:.0f}} points, in a heavily censored cell.
- Instantaneous discharge recorded with a sample and the daily mean at the gauge agree on
  {{explore.flow.n_pairs}} same-day pairs with a log correlation of {{explore.flow.corr_log:.3f}}
  and a median absolute log ratio of {{explore.flow.median_abs_log_ratio:.3f}}.
- The USGS quarterly series below Silverton ({{explore.usgs.n_pre}} pre, {{explore.usgs.n_post}}
  post samples, below the inclusion rule) gives {{explore.usgs.level_change_pct:.0f}} percent
  ({{explore.usgs.level_change_pct_lo:.0f}} to {{explore.usgs.level_change_pct_hi:.0f}}).

## Decision log

See `docs/decisions.md` for the endpoint history, the verified confounder timeline with
sources, every data rule, and what cairn blocked.


## Supplementary uncertainty and timeline

Headline intervals are conditional on the fitted first-stage concentration-discharge adjustment; they omit its estimation error. An [exploratory full two-stage calendar-block sensitivity](docs/two-stage-uncertainty.md) refits both stages without replacing the frozen primary results. The [release, treatment and sampling timeline](docs/timeline.md) explains why attribution remains unresolved.
