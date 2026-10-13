On 5 August 2015 the Gold King Mine release sent a pulse of acidic, metal-laden mine water down Cement Creek and into the Animas River at Silverton, Colorado. The plume passed Silverton within a day and Durango within days. I wanted to know whether anything lasting changed in the river's metal chemistry once the plume was gone, because the obvious before-and-after comparison is the one that gets quoted, and it is wrong in ways that do not announce themselves.

The question sounds simple. Take the concentrations before, take them after, compare. But river concentrations move with flow and season, so two years with different snowmelt are not comparable on raw numbers. Sampling surged after the release, so the "after" record comes from different organisations, methods and reporting limits than the "before" record. And a treatment plant began treating the same mine discharge two months after the release, so any change at the release date has two candidate causes inside the resolution of a monthly series.

## What I expected before I looked

I expected the treatment plant; the brief anticipated it, and I checked the dates against published sources. EPA's releases say the Gladstone interim treatment plant has treated the Gold King discharge since October 2015. EPA documents say that flows from Gold King and its neighbours rose after concrete bulkheads were installed in the adjacent Sunnyside workings before my study period began, so I expected a rising pre-period trend rather than a flat baseline. The Bonita Peak Mining District went onto the Superfund list in 2016, so I expected source-control changes inside the post-period too.

Those expectations shaped the design before any data arrived. The interrupted time series would need a pre-period slope term, because a rising baseline extrapolated forward is the counterfactual against which any change is judged. I would need a sensitivity grid over the pre-period start, a change-point search not told the release date, and an upstream control above the Gold King source.

## Getting the records, and the profile that dropped every USGS row

The chemistry comes from the Water Quality Portal, the public service that serves water-chemistry results from federal, state and other organisations in a common format. I pulled the snapshot on {{snapshot.download_date}} through the portal's legacy result endpoint, which returned {{snapshot.wqp_result_rows:,}} rows since 2005 with count headers that let me confirm the total. The same query on the newer WQX3 profile returned {{snapshot.wqx3_rows:,}} rows and no count headers. The difference is exactly {{snapshot.wqx3_missing_rows:,}} rows, which is every USGS row in the period. The newer profile had silently dropped one agency's entire contribution.

I recorded both outcomes in a manifest and used the legacy profile. Discharge came from the USGS Water Data API as daily mean values at the five gauges, {{snapshot.daily_rows_total:,}} values in all, and the snapshot was hashed and committed.

The gauges themselves were too thin; the USGS sampled chemistry at Cement Creek on only a handful of dates, all after the release. So I grouped partner stations within about a kilometre of each gauge into reaches, with Cement Creek at Silverton and the Animas below Silverton as impacted reaches, the Animas above Cement Creek as the upstream control, and Durango downstream.

## Using one organisation across the release

With {{coverage.n_orgs}} organisations in the snapshot, the next question was whether to pool them, so I counted sampling events by reach, year and organisation first.

![Metal sampling events per year by organisation at the four reaches, with the release and plant start marked.](reports/figures/coverage.png)

At the four reaches from Silverton to Durango the rate was {{coverage.r4.events_per_year_pre:.0f}} events a year before the release and {{coverage.r4.events_per_year_post2y:.0f}} a year in the two years after the plant started. Of the {{coverage.r4.orgs_pre}} organisations with pre-period samples, {{coverage.r4.orgs_pre_steady}} sampled steadily. Colorado River Watch supplied {{coverage.r4.rw_share_pre:.0%}} of pre-period events and {{coverage.r4.rw_share_post2y:.0%}} of events in those two post years, while its own count barely moved, {{coverage.rw_events_pre}} events before and {{coverage.rw_events_post}} after, with one laboratory method ({{coverage.rw_method}}) throughout.

That settled it. Pooling would make the "after" record a different population from the "before" record. I considered an organisation fixed effect and rejected it, because programmes that began after the release have no pre-period, so their effect cannot be separated from the change itself. The confirmatory series use River Watch alone at the four reaches it sampled monthly from 2005 to 2025; everyone else is kept for description and for an exploratory pooled fit I report later.

## Why raw concentrations cannot be compared across years

Before fitting anything I looked at the raw headline series beside the discharge at its gauge.

![Raw dissolved zinc at Cement Creek, with daily discharge below.](reports/figures/timeseries_headline.png)

Median dissolved zinc was {{cq.headline.median_conc_pre:,.0f}} micrograms per litre before the release and {{cq.headline.median_conc_post:,.0f}} after, which looks like a clear drop. But median discharge on the sampling dates was {{cq.headline.median_q_pre}} cubic feet per second before and {{cq.headline.median_q_post}} after. Concentration depends on flow and on season, so a raw comparison across years with different water is partly a comparison of the water.

Flow adjustment is the first stage of the model. For each series I fitted a concentration-discharge regression, log concentration against log discharge with {{const.n_harmonics}} seasonal harmonics, sine and cosine terms that absorb the annual cycle without assuming its shape. It is fitted on pre-period rows only, so the post-period cannot shape its own baseline, and the residual is the flow-adjusted series.

![Dissolved zinc against discharge at Cement Creek, before and after the release.](reports/figures/cq_headline.png)

The fitted slope for the headline is {{cq.headline.slope:.2f}}, interval {{cq.headline.slope_lo:.2f}} to {{cq.headline.slope_hi:.2f}}, so zinc in Cement Creek is only weakly diluted by flow. Non-detects needed their own rule, because "below the limit" is an interval, not a value. Both stages are fitted by censored maximum likelihood, a Tobit regression that treats those rows as bounds rather than substituting a number. River Watch did not record reporting limits before {{coverage.rw_first_year_with_limits}}, so {{coverage.rw_rows_bound_assigned:,}} earlier non-detects received a bound by a pre-registered rule and are flagged.

## Writing the decision rule before fitting

Before I computed any result I wrote the pre-registration and froze it by hash. The headline is one series, dissolved zinc at Cement Creek, because zinc is the dominant dissolved metal there and one the plant targets. The pre-period runs from the start of 2005 to the day before the release; a plume window of about eight weeks, to the end of September 2015, is excluded from every fit because the plume is not the lasting condition under test; the post-period runs to the end of 2025.

The second stage is an interrupted time series on the flow-adjusted residuals, a regression with a pre-period slope, a level change at the release and a slope change after it. Monthly samples from one stream are autocorrelated, so every interval is Newey-West, an autocorrelation-robust sandwich with a bandwidth of {{const.hac_lags}} observations. A cell is estimable with at least {{const.min_pre}} pre-period and {{const.min_post}} post-period samples and no more than {{const.max_cens_pre_pct}} percent pre-period censoring; otherwise it is reported as not estimable, not filled.

The rule says "lasting change detected" if the {{const.ci_pct}} percent interval for the level change excludes zero under the primary specification and under all three pre-period starts with the same sign; "change depends on the pre-period" if the primary excludes zero but a start does not; and "no detectable lasting change" otherwise, never reported as an upper bound. Attribution is a separate clause, because the interrupted time series alone cannot separate the release from a plant two months away. If the strongest blind change-point lies within three months of the release the change is "coincident with the release and the plant start, inseparable from this series"; otherwise it is "not attributable to the release".

## The primary result and its verdict

![The interrupted time series on flow-adjusted zinc, with the release, the plant start and the extrapolated pre-period trend.](reports/figures/its_headline.png)

The primary fit uses {{its.headline.n}} monthly samples. The level change at the release is {{its.headline.level_change_pct:pct_signed}}, with a {{const.ci_pct}} percent interval from {{its.headline.level_change_pct_lo:.0f}} to {{its.headline.level_change_pct_hi:+.0f}} percent and p = {{its.headline.level_change_p:.2f}}. The pre-period trend is {{its.headline.pre_slope_pct_per_yr:.1f}} percent a year, interval {{its.headline.pre_slope_pct_per_yr_lo:.1f}} to {{its.headline.pre_slope_pct_per_yr_hi:.1f}}, so flow-adjusted zinc was rising through the pre-period as I expected, and the counterfactual extrapolates that rise. The slope change after the release is {{its.headline.slope_change_pct_per_yr:.1f}} percent a year, p = {{its.headline.slope_change_p:.2f}}; level and slope together put the series {{its.headline.change_at_end_pct:.0f}} percent below the counterfactual after {{its.headline.years_post:.1f}} years.

By the frozen rule the verdict is "{{its.headline.verdict}}", because the primary interval includes zero.

One post-freeze code change belongs here. The first run flagged non-convergence on a flat likelihood where the score was numerically zero, so I changed convergence to be judged by the score itself and logged that no estimate moved beyond optimiser noise.

## How the answer moves with the windows

The pre-registration committed me to a sensitivity grid, the same model rerun under every pre-period start, plume window and post-period end, all reported together.

![Level change under every pre-period start, plume window and post-period end; starred cells exclude zero.](reports/figures/sensitivity_grid.png)

Across the {{grid.n_fits}} fits the level change runs from {{grid.pct_min:.0f}} to {{grid.pct_max:+.0f}} percent; {{grid.n_ci_excludes_zero}} intervals exclude zero and {{grid.n_negative}} point estimates are negative. The pre-period start barely moves the point estimate and strongly moves the interval. Starting in 2010 gives {{grid.pre2010.level_change_pct:.0f}} percent, interval {{grid.pre2010.level_change_pct_lo:.0f}} to {{grid.pre2010.level_change_pct_hi:.0f}}, and starting in 2013 gives {{grid.pre2013.level_change_pct:.0f}} percent, interval {{grid.pre2013.level_change_pct_lo:.0f}} to {{grid.pre2013.level_change_pct_hi:.0f}}, both excluding zero. The long pre-period carries the rising trend and, as I found later, a few coding artefacts, which widen the interval.

The post-period end matters more. Ending it in 2016 flips the sign to {{grid.pre2005_plume20150930_post2016.level_change_pct:+.0f}} percent, interval {{grid.pre2005_plume20150930_post2016.level_change_pct_lo:.0f}} to {{grid.pre2005_plume20150930_post2016.level_change_pct_hi:+.0f}}; ending in 2018 gives {{grid.pre2005_plume20150930_post2018.level_change_pct:.0f}} percent with p = {{grid.pre2005_plume20150930_post2018.level_change_p:.2f}}. The first year after the release sat above the counterfactual, not below it, and the decline accrues over years; widening the plume window to the end of 2015 removes those higher autumn samples and gives {{grid.pre2005_plume20151231_post2025.level_change_pct:.0f}} percent.

The rule's second clause was written for the opposite case, a significant primary with a start that disagrees, so it does not fire, and the sign flip with the post-period end was not anticipated at all. I report the dependence in full rather than reinterpret the rule after the fact. That raised the question the grid cannot answer, where in the record the change actually sits.

## A change-point search that was not told the date

A blind change-point search asks the series where its level shifts without telling it where to look. I fitted the stage-one model without any trend or step over the whole period, averaged the residuals by calendar month, and ran PELT, an exact search that balances fit against the number of breaks, with a mean-shift cost and a minimum segment of a year. The algorithm never sees the release date.

![Blind change-points on the pre-registered series, with the release and plant start marked.](reports/figures/changepoints_headline.png)

It finds {{cp.headline.n_pelt}} change-points, at {{cp.headline.pelt_months}}, which is {{cp.headline.pelt_rel_release_months}} months relative to the release. The strongest single split is {{cp.headline.strongest_month}}, {{cp.headline.strongest_rel_release_months:+d}} months from the release, so by the frozen rule the change is "not attributable to the release". But three of those splits are not chemistry. The pre-period holds a few zero-valued rows carrying a laboratory qualifier, which the pre-registered rule reads as non-detects bounded at about {{coverage.rw_zinc_rl_min:.0f}} micrograms per litre, in a stream whose median runs in the thousands. The censored model takes that bound at face value; the residual scale is {{its.headline.sigma:.2f}} with those rows and {{explore.clean.sigma:.2f}} without them.

I could not edit the frozen plan, and I did not drop the rows silently. I wrote a post-freeze rule, a value or bound below a {{const.implausible_divisor}}th of the series' {{const.implausible_quantile_pct}}th percentile of detected values, and reported the count it removes per cell. My first version, a fraction of the median, missed the control's artefacts; I replaced it before writing the report and logged the change. This part is exploratory.

![Blind change-points on the cleaned series; the strongest lands after the plant started.](reports/figures/changepoints_headline_cleaned.png)

With {{cp.explore.n_rows_removed}} rows removed PELT finds {{cp.explore.n_pelt}} change-points, at {{cp.explore.pelt_months}}. The strongest is {{cp.explore.strongest_month}}, {{cp.explore.strongest_rel_release_months:+d}} months after the release and {{cp.explore.strongest_rel_plant_months:+d}} months after the plant started, with a level shift of {{cp.explore.post_release_shift_pct:.0f}} percent across it. The cleaned interrupted time series gives {{explore.clean.level_change_pct:.0f}} percent, interval {{explore.clean.level_change_pct_lo:.0f}} to {{explore.clean.level_change_pct_hi:.0f}}, p = {{explore.clean.level_change_p:.3f}}.

A split a few months after both events is what a plant that started in October 2015 would produce, and also what a slowly developing post-release change would produce. The series cannot tell them apart, and the segment before the split, the most elevated in the record, begins before the release, so the baseline was not stable either. Across the {{cp.cells.n}} estimable cells, {{cp.cells.n_strongest_within_3mo_release}} have their strongest split within three months of the release.

## The upstream control and the difference-in-differences

If zinc fell everywhere in the basin, a fall at Cement Creek says nothing about its source. The Animas above Cement Creek is upstream of Gold King, and its pre-registered dissolved-zinc level change is {{did.control_zinc.level_change_pct:.0f}} percent, interval {{did.control_zinc.level_change_pct_lo:.0f}} to {{did.control_zinc.level_change_pct_hi:.0f}}, p = {{did.control_zinc.level_change_p:.2f}}. That looked like a basin-wide decline, and it is not. The control carries {{explore.clean.control.n_rows_removed}} zero-coded "non-detects" with bounds far below anything the stream has measured, two of them in the post-period. Without them the control's change is {{explore.clean.control.level_change_pct:.0f}} percent, interval {{explore.clean.control.level_change_pct_lo:.0f}} to {{explore.clean.control.level_change_pct_hi:.0f}}, p = {{explore.clean.control.level_change_p:.2f}}.

The pre-registered difference-in-differences subtracts the control's same-month residual from Cement Creek's, so that anything common to both reaches cancels, and fits the interrupted time series on the difference. On {{did.headline.n_pairs}} paired months the level change is {{did.headline.level_change_pct:.0f}} percent, interval {{did.headline.level_change_pct_lo:.0f}} to {{did.headline.level_change_pct_hi:.0f}}, p = {{did.headline.level_change_p:.3f}}, with a slope change of {{did.headline.slope_change_per_yr:.3f}} log units a year, p = {{did.headline.slope_change_p:.4f}}. Cleaned the same way it is {{explore.clean.did.level_change_pct:.0f}} percent and still excludes zero.

Relative to the upstream control, Cement Creek stepped down and then kept drifting down through the post-period. That rules out a basin-wide driver as the whole explanation. It is consistent with treatment at Gladstone and with Superfund-era source control in the Cement Creek basin, and it is not the signature of a one-day release.

## Every site and metal, with false-discovery control

The headline is one of {{mult.n_cells}} cells, four reaches by eight constituents by two fractions. A grid that size produces significant cells by chance, so the pre-registration committed to the corrected count and to describing the grid as a whole.

![Every reach, metal and fraction, with point estimate, interval and false-discovery result.](reports/figures/multiplicity_grid.png)

{{mult.n_estimable}} cells are estimable and {{mult.n_not_estimable}} are not, every one for pre-period censoring above the threshold; dissolved arsenic is {{coverage.rw_arsenic_dissolved_censored:.0%}} censored and estimable nowhere. Of the estimable cells {{mult.n_negative_point}} have negative point estimates with a median of {{mult.median_pct:.0f}} percent, {{mult.n_raw_sig}} have a raw p below {{const.alpha:.2f}}, and {{mult.n_bh_sig}} survive the Benjamini-Hochberg procedure at a {{const.fdr_pct}} percent false discovery rate. The pattern is a broad, modest, mostly non-significant decline at all four reaches including the control. No single cell is a finding. The exploratory cleaning rule, applied to every estimable cell, touches {{explore.clean.grid.n_cells_with_removed}} of them and still leaves {{explore.clean.grid.n_bh_sig}} surviving correction.

## What pooling the newcomers would have done

I then fitted the pooled series as an exploratory check, to see the size of the trap I had designed around. At Cement Creek the sampling rate went from {{coverage.cc.events_per_year_pre:.1f}} events a year before the release to {{coverage.cc.events_per_year_post2y:.0f}} in the two years after the plant started. Pooling all {{explore.pooled.n_orgs}} organisations there, where {{explore.pooled.share_post_rows_non_riverwatch:.0%}} of post-release rows come from programmes that did not exist before the release, gives {{explore.pooled.level_change_pct:.0f}} percent, interval {{explore.pooled.level_change_pct_lo:.0f}} to {{explore.pooled.level_change_pct_hi:.0f}}, about double the single-organisation estimate. Much of that is a change in who sampled.

## What the headline interval leaves out

The headline interval is conditional on the fitted flow adjustment. The second stage treats the first-stage residuals as data, so the interval omits the estimation error of the concentration-discharge fit and is somewhat too narrow. After the primary result I decided to measure that, and this part is exploratory.

The method is a calendar-block pairs bootstrap, which resamples whole blocks of months separately before and after the release, keeps each measurement with its own discharge, date and censoring status, and refits both stages on every draw. Block lengths of 12 and 24 months were chosen after the pre-registration. With 12-month blocks, {{uncertainty.block12.n_valid}} of {{uncertainty.block12.n_draws}} draws converged and the percentile interval runs from {{uncertainty.block12.lo:.0f}} to {{uncertainty.block12.hi:+.0f}} percent; with 24-month blocks, {{uncertainty.block24.n_valid}} of {{uncertainty.block24.n_draws}} converged and it runs from {{uncertainty.block24.lo:.0f}} to {{uncertainty.block24.hi:+.0f}} percent. Both are wider than the conditional interval and both include zero, so the verdict does not move; this is a sensitivity, not a calibrated coverage claim.

## What I concluded

A decline of about a fifth in flow-adjusted dissolved zinc at Cement Creek over the decade after 2015 is plausible, and it is not detectable against the longest pre-period under the plan I froze. It did not begin at the release, it is partly a decline relative to the upstream control, and the strongest break in the cleaned record falls after the treatment plant started. Nothing in these series separates the release from the plant.

## What I would not claim

I would not attribute any change to the release; the release and the plant start are two months apart, inside the resolution of a monthly series, and the pre-registration said so. I would not report the cleaned-series estimate, whose interval excludes zero, as confirmatory; it was chosen after seeing the data and is the one a second study should pre-register. I would not treat any single cell in the grid as a finding, and I make no health, ecological, compliance or legal claim.

## What I would do next with another week

I would pre-register the cleaning rule for qualifier-coded zeros and refit the headline and the control under it, so that the tighter estimate could be confirmatory. I would look for a record of the plant's monthly treated load, which would let a model carry the plant as a covariate instead of a confounder. And I would rerun the blind change-point search under a range of penalties to see how stable the split after the plant start is.
