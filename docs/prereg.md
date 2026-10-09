# Pre-registration

Written before computing any result. Frozen by `cairn freeze`; a changed hash
fails verification. Anything not described here is exploratory and must be
labelled as such in the report.

## Question

After adjusting for discharge and season, did dissolved and total metal concentrations
in Cement Creek at Silverton and in the Animas River (above Cement Creek, below
Silverton, at Durango) change in a lasting way, on a scale of months to years, after the
5 August 2015 Gold King Mine release, and can any change be distinguished from what
followed it, above all the Gladstone interim water treatment plant that has treated the
Gold King discharge since October 2015? Period: samples from 2005-01-01 to the last
available Colorado River Watch sample (2025); concentrations in micrograms per litre.

## Primary quantity

The headline cell is one series: dissolved zinc at Cement Creek, Colorado River Watch
station CORIVWCH_WQX-323, paired with USGS gauge 09358550. The primary quantity is the
level change at the release date in the flow-adjusted series from the interrupted time
series model below (`level_change`, natural-log units), reported as a percent change
`100 * (exp(level_change) - 1)` with its Newey-West 95% interval, and the slope change
(log units per year) beside it. Zinc is the dominant dissolved metal in Cement Creek and
one of the three metals the treatment plant targets, which is why it is the headline;
the other seven metals and the total fraction are reported in the multiplicity grid.

## Unit of analysis

The unit is one routine sampling event (site and date) inside one series, a series
being one reach, one constituent, one fraction, one organisation. Samples within a
series are repeated measures on the same stream and are autocorrelated, so every
interval uses a Newey-West (Bartlett kernel) heteroskedasticity- and
autocorrelation-consistent sandwich with a bandwidth of 12 observations, applied along
the time-ordered observation index (about one year at monthly sampling). Series are
never pooled; each cell is fitted on its own.

## Population and comparability

- Water-quality rows: Water Quality Portal snapshot `data/raw/wqp_result.csv` (legacy
  `resultPhysChem` profile; the WQX3 profile omitted every USGS row and is not used).
- Confirmatory population: Colorado River Watch (`CORIVWCH_WQX`) routine samples
  (`ActivityTypeCode = Sample-Routine`, `ActivityMediaName = Water`) at the four reaches
  it sampled monthly from 2005 through 2025: `cement_creek` (station 323, impacted),
  `animas_above_cement` (103, upstream control), `animas_below_silverton` (3611,
  impacted), `animas_durango` (91, downstream). One laboratory method (EPA 200.15
  ICP-AES) applies throughout, so the confirmatory series do not mix organisations,
  methods or sampling programmes across the release date. The Cedar Hill reach has no
  monthly series before 2015 and is descriptive only.
- Records from USGS, EPA Region 8, the Bonita Peak programme, CDPHE, ARSG and the
  Southern Ute Tribe are kept for coverage, detection-limit and comparability
  description, and for an exploratory all-organisation sensitivity. They are never in a
  confirmatory estimate because their sampling starts, stops or intensifies at the
  release date.
- Exclusions (each logged with counts in `data/derived/exclusion_log.csv`): non-water
  media; quality-control samples (kept separately); data-logger daily statistics; flow
  rows (kept separately); metal rows without a dissolved or total/recoverable fraction
  label; `Not Reported` results; unconvertible units; rows without a value (or, for a
  non-detect, without a limit); non-positive values; duplicate results on the same
  organisation, site, date, time, constituent and fraction (first `ResultIdentifier`
  kept). Dissolved and total fractions are separate series. Units are converted with
  explicit factors (`src/animas/units.py`); `Total`, `Total Recoverable` and
  `Recoverable` are grouped as total with the raw label retained.
- Discharge: the USGS daily mean discharge (parameter 00060, statistic 00003) at the
  reach's gauge on the sample date, joined many-to-one with `cairn.checked_merge`;
  samples whose date has no daily value are excluded from the models and counted.
  Provisional and ice-estimated values are used as served and flagged.
- Periods. Pre-period: 2005-01-01 to 2015-08-04. Plume-passage window: 2015-08-05 to
  2015-09-30 inclusive, excluded from every fit (the plume passed Silverton within a
  day and Durango within days; eight weeks also covers the immediate post-release
  resampling of settled material). Post-period: 2015-10-01 to 2025-12-31. "Lasting"
  therefore means a level or slope change that persists across the post-period, not
  the plume itself.
- Inclusion rule for a cell: at least 60 pre-period and 36 post-period samples with
  discharge, and no more than 50% censored rows in the pre-period. Cells failing this
  are reported as not estimable, not fitted.

## Handling of missing and censored values

Non-detects are identified from `ResultDetectionConditionText`, a `<` prefix, or a
reported zero with laboratory qualifier `U` or `DL`; they are left-censored at the
reporting limit on the log scale, never substituted. Where a non-detect arrived without
a limit (Colorado River Watch did not populate limits before 2013), the bound is the
smallest detected value the same organisation reported for that constituent and
fraction in the same calendar year, else the median limit from the earliest year that
organisation recorded limits; such rows are flagged (`rl_source`) and counted per cell.
Both model stages are fitted by left-censored (Tobit-style) maximum likelihood with
observation-specific thresholds; with no censored rows this is ordinary least squares.
A censored row's flow-adjusted residual is a bound (log limit minus the fitted value)
and stays censored in the second stage. Substitution at half the limit is run only as a
labelled sensitivity check. Missing discharge is not imputed.

## Decision rule

Model, stage 1 (concentration-discharge): for each cell, on pre-period rows only,
`log C = a + b log Q + sum_{k=1,2} [c_k sin(2 pi k t) + d_k cos(2 pi k t)]`, t in
decimal years; residuals (or bounds) are then computed for every row in the cell.
Stage 2 (interrupted time series) on the residual series with the plume window removed:
`r = b0 + b1 tau + b2 post + b3 post * tau`, tau = years since 2015-08-05, post = 1 after
the release. `b2` is the level change and `b3` the slope change.

Sensitivity grid for the headline cell (all reported, the primary is the first of
each): pre-period start in {2005-01-01, 2010-01-01, 2013-01-01}; plume-window end in
{2015-09-30, 2015-08-19, 2015-12-31}; post-period end in {2025-12-31, 2016-12-31,
2018-12-31}; 27 fits.

Blind change-point search: a stage-1 model without trend or step is fitted to the whole
period of each cell; residuals are averaged by calendar month; PELT and binary
segmentation with an L2 (mean-shift) cost, penalty `3 * sigma^2 * log(n)` with sigma
from the median absolute first difference, minimum segment 12 months. The algorithm is
not given the release date. The reported quantities are each change-point month and its
distance in months to 2015-08 (release) and 2015-10 (plant start), and the location of
the strongest single split.

Difference-in-differences check: for `cement_creek` and `animas_below_silverton`, the
stage-1 residual minus the same-month residual of the upstream control
`animas_above_cement` (both uncensored; dropped pairs counted), then the stage-2 model
on the difference.

Conclusions for the headline cell, decided now:

1. "Lasting change detected" if the 95% interval for `b2` in the primary specification
   excludes zero and the interval excludes zero with the same sign for all three
   pre-period starts (primary plume window and post end).
2. "Change depends on the pre-period" if the primary interval excludes zero but one of
   the three pre-period starts does not, or the sign differs.
3. "No detectable lasting change" otherwise. An interval that includes zero is reported
   as no detectable change, not as an upper bound.
4. Attribution, reported alongside whichever of 1 to 3 applies: the release and the
   plant start are two months apart, inside the resolution of a monthly series, so the
   interrupted time series alone never attributes a change to the release. If the
   strongest blind change-point in the headline cell lies within three months of
   2015-08 the change is described as "coincident with the release and the treatment
   plant start, inseparable from this series"; if it lies elsewhere, as "not
   attributable to the release". If the control reach shows a change of the same sign
   and the difference-in-differences level change includes zero, the change is
   described as watershed-wide rather than specific to the Cement Creek source.
5. Multiplicity: all 4 reaches x 8 constituents x 2 fractions = 64 cells are fitted at
   the primary specification. The number of estimable cells, the number with raw
   p < 0.05, and the number surviving Benjamini-Hochberg at 5% false discovery rate are
   reported. No cell other than the headline receives confirmatory status; the grid is
   described as a whole.
6. Abstain (report no estimate) for any cell that fails the inclusion rule, for the
   headline if either stage fails to converge, and for the whole study if more than 20%
   of the headline cell's samples lack discharge.

## Confirmatory vs exploratory

Confirmatory: the headline estimate, its 27-fit sensitivity grid, the blind
change-point locations, the difference-in-differences check, and the 64-cell
multiplicity grid with its corrected counts, all exactly as specified above.
Exploratory, and labelled so wherever reported: pooling other organisations' samples
into a reach series; using instantaneous discharge recorded with the sample instead of
the daily mean; substitution at half the limit; pH and specific conductance; the USGS
quarterly series at 09359020; the Cedar Hill reach; any additional change-point
penalty; any model form, window or site not listed here. Anything decided after the
freeze is exploratory.
