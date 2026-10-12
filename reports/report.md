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
dissolved zinc in Cement Creek after the release is -20
percent relative to the continued pre-period trend (interval
-38 to 3
percent, p = 0.08, n = 245 samples).
The pre-registered rule returns "no detectable lasting change". That verdict is fragile in a
specific, documented way: with the pre-period starting in 2010 or 2013 instead of 2005 the
same model gives -19 percent
(-29 to -7) and
-23 percent (-34 to
-11), both excluding zero, and with the post-period cut
at the end of 2016 the sign flips to 41
percent (-12 to
126). The blind change-point
search puts its strongest split at 2010-03,
-65 months from the release; on the series with
three coding artefacts removed (exploratory) the strongest split is 2016-02,
6 months after the release and
4 months after the treatment plant start. Across all
64 reach-constituent-fraction cells, 7 have a raw p below
0.05 and 0 survive false-discovery control. The honest summary is: a
decline in flow-adjusted zinc of roughly a fifth is plausible over the decade after 2015, it
is not detectable against the longest pre-period, it did not begin at the release, and
nothing in these series separates the release from the treatment plant that started two
months later.

All intervals in this report are two-sided with nominal coverage of 95
percent, from a Newey-West sandwich with a Bartlett bandwidth of 12
observations. Percent changes are `exp(level change) - 1` on the natural-log scale.

## Data and comparability

- Snapshot downloaded 2026-10-09: 38236 Water
  Quality Portal result rows (2568 USGS NWIS, 35668
  WQX/STORET) for 32 stations grouped into five reaches, and
  39751 daily mean discharge values for 5 gauges
  from the USGS Water Data API (version 0.80.8). The same query on the
  portal's WQX3 profile returned 35668 rows, i.e. it dropped all
  2568 USGS rows; the legacy `resultPhysChem` profile is the
  complete one for this period.
- One raw row is one result (characteristic, fraction) from one sampling activity at one
  station. After the exclusion log (9071 rows excluded with a rule
  each; 602 quality-control rows and 4005 instantaneous-flow
  rows kept in separate tables) the sample table holds 24558 rows from
  9 organisations at 32 stations,
  2005-01-10 to 2026-07-29. Every sample date had a daily discharge
  value at its gauge.
- Sampling intensity: at the four reaches from Silverton to Durango, metal sampling ran at
  59.2 events per year before the release and
  129 per year in the two years after the treatment plant
  started (2.18 times), settling to 70.4
  per year over the whole post-period. Of the 6 organisations with
  pre-period samples only 1 sampled steadily; Colorado River
  Watch supplied 76% of pre-period events and
  36% of events in those two post years, while staying at
  475 events before and 479 after with one
  method (200.15) throughout (figure `reports/figures/coverage.png`). At
  Cement Creek alone the rate went from 14.3 to
  37 events per year. That is why the confirmatory
  series use River Watch only; pooling organisations is reported below as exploratory.
- Censoring: 4345 of 24558 rows are non-detects
  (17.7%). River Watch recorded reporting limits only from
  2013; 1739 earlier
  non-detects received a bound by the pre-registered rule and are flagged. Reporting limits
  changed over time (figure `reports/figures/detection_limits.png`): dissolved arsenic is
  98% censored and is not estimable anywhere;
  dissolved zinc is 1.4% censored.
- Dissolved and total fractions are separate series throughout.

## Method

Pre-registered in `docs/prereg.md` (frozen before any fit). Stage one: for each series,
`log C = a + b log Q + seasonal harmonics` (2 harmonics) fitted on the
pre-period by left-censored maximum likelihood; the residual, or its bound for a non-detect,
is the flow-adjusted series. Stage two: an interrupted time series on that series with a
pre-period slope, a level change and a slope change at the release, the plume window
excluded, censored rows kept as censored, Newey-West uncertainty. The headline cell has
123 pre-period and 122 post-period samples; its
concentration-discharge slope is -0.12 (-0.50 to
0.26) and its annual seasonal amplitude 0.09
log units (figure `reports/figures/cq_headline.png`). A cell is estimable with at least
60 pre and 36 post samples and at most
50 percent pre-period censoring.

## Result: the headline cell

Figure `reports/figures/its_headline.png` shows the fit; `reports/figures/timeseries_headline.png`
the raw series with discharge.

- Level change at the release: -19.9 percent
  (-37.7 to 3.1;
  p = 0.085).
- Pre-period trend: 3.0 percent per year
  (0.1 to 6.1):
  flow-adjusted zinc was rising through the pre-period, as expected after the Sunnyside
  bulkheads. The counterfactual extrapolates that rise.
- Slope change after the release: -2.6 percent per
  year (p = 0.16). Level and slope together put the series
  -39 percent below the counterfactual at the end of
  10.4 post-release years, a point estimate whose uncertainty grows
  with the extrapolation.
- Median dissolved zinc was 2061 ug/L before and
  1652 ug/L after, at median discharges of
  18.6 and 15.2 ft3/s: the raw drop is
  larger than the flow-adjusted one.
- Pre-registered conclusion: **no detectable lasting change** (primary interval excludes zero:
  False; all three pre-period starts agree:
  False).

## How the answer depends on the choices

The grid of 27 fits (figure `reports/figures/sensitivity_grid.png`, table
`reports/tables/sensitivity_grid_headline.csv`) spans -26 to
46 percent; 14 of 27 intervals
exclude zero and 15 of 27 point estimates are negative.

| Pre-period start | Level change, percent | Interval | p | Pre-slope, percent per year |
|---|---|---|---|---|
| 2005 (primary) | -20 | -38 to 3 | 0.085 | 3.0 |
| 2010 | -19 | -29 to -7 | 0.003 | -1.7 |
| 2013 | -23 | -34 to -11 | 0.001 | 2.2 |

The point estimate barely moves; the interval does. The 2005 start carries the rising
pre-period trend and the 2007 and 2009 artefacts described under exploratory findings, which
widen the interval; the shorter pre-periods have flatter trends and tighter intervals.
The post-period end matters more than the pre-period start: ending in 2016 the level
change is 41 percent
(p = 0.15), ending in 2018
-1 percent
(p = 0.95), ending in 2025
-20 percent. The first year after
the release was higher than the counterfactual, not lower; the decline accrues over years.
Widening the plume window to the end of 2015 removes those higher autumn samples and gives
-26 percent
(-39 to
-9).

## Blind change-points

On the monthly flow-adjusted series fitted without any knowledge of the release date
(figure `reports/figures/changepoints_headline.png`), PELT finds 5
change-points at 2007-05; 2009-01; 2010-03; 2016-02; 2020-11, that is -99; -79; -65; 6; 63
months relative to the release and -101; -81; -67; 4; 61 months relative to
the plant start. The strongest single split is 2010-03
(-65 months from the release), so by the
pre-registered rule the change is **not attributable to the release**. Three of the splits
are driven by implausible rows in 2007 and 2009 (see exploratory findings); with those
removed (figure `reports/figures/changepoints_headline_cleaned.png`) PELT finds
6 change-points at 2006-10; 2007-11; 2014-12; 2016-02; 2017-06; 2020-11, that is
-106; -93; -8; 6; 22; 63 months from the release and
-108; -95; -10; 4; 20; 61 months from the plant start. The strongest is
2016-02, with a level shift of -31
percent across it; the segment before it, which begins late in 2014, is the most elevated
in the series (segment means -0.05; +0.33; +0.12; +0.29; -0.08; -0.24; -0.09). A split a few months after both
events is what a treatment plant that started in October 2015 would produce; it is also
what a slowly developing post-release change would produce. The series cannot tell them
apart, and the elevated year before the release says the pre-release baseline was not
stable either. Across the 52 estimable cells, 0
have their strongest split within three months of the release and
12 have any split within three months of it.

## The upstream control

The Animas above Cement Creek, upstream of the Gold King source, shows a pre-registered
dissolved-zinc level change of -21 percent
(-40 to 4,
p = 0.09). That number is not what it seems: the control
series carries 3 zero-valued "non-detects" with
bounds far below anything the stream has measured, two of them in the post-period, and the
censored model takes them at face value. Without them (exploratory) the control's level
change is -11 percent
(-27 to 9,
p = 0.28).

The pre-registered difference-in-differences series (Cement Creek residual minus the same
month's control residual, uncensored pairs only, 234 paired months)
has a level change of -24 percent
(-42 to -1,
p = 0.040) and a slope change of
-0.075 log units per year (p = 0.0001);
cleaned the same way it is -23 percent
(-39 to -2,
slope change -0.066 per year,
p = 0.0008). For the Animas below Silverton the paired level
change is -20 percent
(-33 to -5).
Relative to the upstream control, Cement Creek stepped down and then kept drifting down
through the post-period. That pattern is consistent with treatment at Gladstone and with
the Superfund-era source control in the Cement Creek basin, and it is not the signature of
a one-day release; the control check rules out a watershed-wide driver as the whole
explanation but cannot rule in the release.

## Multiplicity

64 cells were fitted at the primary specification (figure
`reports/figures/multiplicity_grid.png`, table `reports/tables/multiplicity_grid.csv`):
52 estimable, 12 not (all for pre-period censoring
above the threshold: every arsenic series and most dissolved lead). Of the estimable
cells 43 have negative point estimates (median
-16 percent), 7 have raw p below 0.05, and
0 survive Benjamini-Hochberg control at 5 percent false
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

- Removing the 3 implausible rows from the headline series
  (rule, decided after the freeze: a value or bound below a tenth of the series'
  5th percentile of detected values) gives a level change
  of -24 percent (-37
  to -10, p = 0.002),
  with the residual scale falling from 0.69 to 0.26
  and the pre-period slope from 3.0 to
  1.0 percent per year. The same rule applied to all
  52 estimable cells touches 24
  of them (74 rows in all), leaves the median residual
  scale unchanged (median ratio 1) while cutting it
  sharply in the cells that carry artefacts, moves a point
  estimate by at most 44 points, and leaves
  9 cells with raw p below 0.05 and 0
  surviving false-discovery control. This is the
  single largest lesson of the study for the censoring rule: a qualifier-coded zero is not
  always a non-detect.
- Pooling all 6 organisations at Cement Creek, where
  35% of post-release rows come from
  programmes that did not exist before the release, gives -40
  percent (-58 to -14):
  the composition change roughly doubles the apparent decline. This is the trap the single-
  organisation design avoids.
- Substituting half the limit for non-detects moves the headline by
  0.7 percentage points; across all
  52 estimable cells the largest move is
  45 points, in a heavily censored cell.
- Instantaneous discharge recorded with a sample and the daily mean at the gauge agree on
  377 same-day pairs with a log correlation of 0.993
  and a median absolute log ratio of 0.033.
- The USGS quarterly series below Silverton (39 pre, 27
  post samples, below the inclusion rule) gives -4 percent
  (-10 to 3).

## Decision log

See `docs/decisions.md` for the endpoint history, the verified confounder timeline with
sources, every data rule, and what cairn blocked.


## Supplementary uncertainty and timeline

Headline intervals are conditional on the fitted first-stage concentration-discharge adjustment; they omit its estimation error. An [exploratory full two-stage calendar-block sensitivity](docs/two-stage-uncertainty.md) refits both stages without replacing the frozen primary results. The [release, treatment and sampling timeline](docs/timeline.md) explains why attribution remains unresolved.
