# Decision log

Append-only. One entry per scoping, data, or analytical decision, with the date,
the evidence (which script or profile), and the alternatives rejected.

## 2026-10-09 Endpoint history (what was tried, what worked)

Verified by direct requests on 2026-10-09; recorded in `data/raw/manifest.json` where the
downloader re-probes them.

| Endpoint | Request | Outcome |
|---|---|---|
| WQP legacy Station `https://www.waterqualitydata.us/data/Station/search` | five USGS gauge ids, `mimeType=csv` | HTTP 200, 5 sites; headers `Total-Site-Count`, `NWIS-Site-Count`. Used. |
| WQP legacy Station, `dataProfile=periodOfRecord` | same sites | HTTP 200 but only station columns, duplicated rows; no per-year counts. Not used. |
| WQP summary `/data/summary/monitoringlocation/search?summaryYears=all&mimeType=geojson` | two sites | HTTP 200, per-site result counts by characteristic group. Used for scoping only. |
| WQP legacy Result `/data/Result/search?dataProfile=resultPhysChem` | full site and characteristic list, `startDateLo=01-01-2005` | HTTP 200, 38,236 rows (NWIS 2,568 + STORET 35,668), count headers present. **Used for the snapshot.** |
| WQP WQX3 Result `/wqx3/Result/search?dataProfile=fullPhysChem` | identical query | HTTP 200, 35,668 rows = the STORET count only; every USGS NWIS row missing; no count headers. Rejected: incomplete for this period. |
| USGS Water Data API `https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items` | `parameter_code=00060`, `statistic_id=00003`, `datetime=2005-01-01/2026-10-09`, `limit=10000`, `f=csv` | HTTP 200, 7,951 rows per gauge in one page (the downloader refuses a page that hits the limit). The `api-version` header read `1.9.8` on the JSON probe and `0.80.8` on the CSV downloads recorded in the manifest (the service appears to be served by more than one backend). Note: the collection metadata links to `/ogcapi/v1/`; `v0` still answers. **Used.** |
| Legacy `https://waterservices.usgs.gov/nwis/dv/?format=json` | one gauge, ten days | HTTP 200, WaterML JSON, 10 values. Still alive; not used because the new API is the supported path. |
| USGS parameter-code lookup `help.waterdata.usgs.gov/code/parameter_cd_query` | pcode 52303 | redirected and returned no table; the definition of the blank-fraction USGS zinc code was not resolved, so those rows are excluded as fraction-unknown rather than guessed. |

- Evidence: `data/raw/manifest.json` (`files`, `probes`), scratch probes during scoping.
- Rejected: WQX3 profile (incomplete); legacy DV service (retiring).

## 2026-10-09 Site selection: partner stations co-located with the USGS gauges

A WQP Station search for zinc stations since 2005 in the Animas corridor
(bBox -108.10,36.90,-107.40,37.95) returned 2,124 stations from 21 organisations. The
five USGS gauges alone hold 447 sampling activities since 2005 (Cement Creek: seven
sampling dates, all 2015 or later; Animas at Silverton: one), far too thin for a monthly
interrupted time series. Partner stations within about one kilometre of each gauge on
the same stream were added and grouped into reaches (`data/raw/query.json`,
`reaches`). Colorado River Watch (CORIVWCH_WQX) sampled four of the reaches monthly from
2005 through 2025 with one laboratory method (EPA 200.15 ICP-AES) throughout; EPA, the
Bonita Peak programme, CDPHE and ARSG sampled in bursts (ARSG 2005 to 2007; EPA and
CDPHE 2015 onwards).

- Reach roles: `cement_creek` impacted (gauge 09358550); `animas_above_cement` control,
  upstream of the Cement Creek confluence (09358000); `animas_below_silverton` impacted,
  downstream of the confluence (09359020); `animas_durango` downstream (09361500);
  `animas_cedar_hill` downstream, New Mexico (09363500).
- Rejected: "Storm Opp" opportunistic storm stations; stations on tributaries (Mineral
  Creek, Lightner Creek, Florida River); the Cement Creek-at-mouth USGS site is listed but
  has no rows in the period.

## 2026-10-09 Confounder timeline, verified against published sources

| Event | Date used | Source |
|---|---|---|
| Gold King Mine release | 2015-08-05 | EPA, "Interim Water Treatment Plant in Gladstone, Colorado Fully Operational" and the 2017 release below both describe the August 5, 2015 release. |
| Gladstone interim water treatment plant (IWTP) treating Gold King discharge | from October 2015 (`PLANT_START` = 2015-10-01) | EPA Region 8 news release, 2017-01-17, "U.S. Environmental Protection Agency announces continued operation of interim water treatment plant": "The IWTP has treated discharge from the Gold King Mine since October 2015." https://www.epa.gov/archive/epa/newsreleases/us-environmental-protection-agency-announces-continued-operation-interim-water.html . The 2019-03-16 EPA release on restoring power after an outage says the plant "was constructed in 2015" and typically removes 500 to 600 pounds of metals per day in March: https://www.epa.gov/newsreleases/interim-water-treatment-plant-gladstone-colorado-fully-operational |
| Sunnyside Mine / American Tunnel bulkheads | 1996 to 2002 (the brief said 2003; the EPA documents say 2002) | EPA Region 8 Action Memorandum, Red and Bonita Mine removal action, 2014-09-24 (SEMS DocID 1289901): "Flows from Red and Bonita Mine, Gold King (Level 7) Mine, and Mogul Mine all experienced significant increases following the construction of concrete bulkheads in Sunnyside Mine - American Tunnel between 1996 and 2002. ... Flow from the American Tunnel was reportedly approximately 1,700 gpm when it was treated prior to the final bulkhead installation." https://www.epa.gov/sites/default/files/2015-08/documents/1289901.pdf . Same wording in the EPA Community Involvement Plan for the Red and Bonita removal, January 2015: https://www.epa.gov/sites/default/files/2015-06/documents/upper-animas-red-and-bonita-removal-community-involvement-plan-1-16-2015.pdf , which adds that "water treatment of the discharge from the American Tunnel and Cement Creek was discontinued" after the bulkheads. Background on the watershed: USGS Professional Paper 1651 (2007), https://doi.org/10.3133/pp1651 . |
| Bonita Peak Mining District proposed to the NPL | 2016-04-07 | EPA news release 2016-09-07, "EPA adds Bonita Peak Mining District site in San Juan County, Colo. to Superfund list": "EPA proposed the BPMD site for addition to the NPL on April 7, 2016". https://www.epa.gov/archive/epa/newsreleases/epa-adds-bonita-peak-mining-district-site-san-juan-county-colo-superfund-list.html |
| Bonita Peak Mining District listed on the NPL | 2016-09-09 | same release: added "to the National Priorities List (NPL) of Superfund sites on September 9, 2016"; 48 mining-related areas in the Mineral Creek, Cement Creek and upper Animas drainages. |
| Red and Bonita Mine bulkhead (removal action) | approved 2014-09-24; installed later | the Action Memorandum above approves a bulkhead in the Red and Bonita adit, a Cement Creek source of about 300 gpm; its later closure is a further post-2015 source-control change inside the post-period. |

Consequences for the design: the post-period begins within two months of the treatment
plant starting, so an interrupted time series at the release date cannot by itself
separate the release from the plant; the pre-period (2005 onwards) sits entirely after
the bulkheads and may carry a rising trend; the Superfund listing and later source
control fall inside the post-period. The pre-registration handles these with a
pre-period slope term, a sensitivity grid over the pre-period start, a blind change-point
search compared against both the release and the plant start, and an upstream control.

## 2026-10-09 cairn configuration

- `cairn init .` was run from this project's own environment, where cairn is installed as
  an editable path dependency on `../cairn` (commit recorded in the README); with an
  editable install the template directory resolves and 16 template files were copied.
- `cairn.toml` was edited once, at project setup and before any analysis, to render the
  report into `reports/report.md` (the brief asks for a `reports/` directory). Figures and
  tables are written to `reports/figures/` and `reports/tables/`; the ledger and checks
  stay in `artifacts/`.
- The network download is `scripts/download.py`, deliberately not a numbered step, so
  `cairn run` and the clean rerun in `cairn verify` work offline from the committed
  snapshot; `scripts/00_snapshot.py` checks the checksums instead.

## 2026-10-09 Confirmatory population: one organisation across the release

- Decision: confirmatory series are Colorado River Watch routine samples only, at the four
  reaches it sampled monthly 2005 to 2025; all other organisations are descriptive or
  exploratory. Evidence: `scripts/20_coverage.py` (ledger `coverage.*`): metal sampling
  events rose from about nine to about twenty-three per year across all organisations after
  the release while River Watch stayed at roughly twelve; the pooled all-organisation fit
  (`explore.pooled.*`) roughly doubles the apparent decline.
- Rejected: pooling organisations with an organisation fixed effect (the post-only
  programmes have no pre-period, so the effect is not identified separately from the
  change); using the USGS quarterly series as the headline (too few samples).

## 2026-10-09 Censoring and bounds for non-detects without a limit

- Decision (pre-freeze, in `docs/prereg.md`): non-detects are identified by the
  detection-condition text, a `<` prefix, or a reported zero with qualifier `U` or `DL`; a
  non-detect without a limit gets the smallest detected value of the same organisation,
  constituent, fraction and year, else the earliest recorded limit; flagged in `rl_source`.
  Evidence: `data/derived/exclusion_log.csv`; River Watch populated limits only from 2013.
- Consequence discovered after the freeze: at Cement Creek and the control, a handful of
  zero-valued `U`/`DL` rows sit in series that never measure anywhere near the assigned
  bound (dissolved zinc runs in the thousands of ug/L at Cement Creek and the hundreds at the
  control). The censored model takes a bound of about five ug/L at face value, inflating the
  residual scale (headline sigma 0.69 vs 0.26 without them) and, at the control, pulling the
  post-period level down because two of the rows fall after 2015. These are coding artefacts
  (a zero with a laboratory qualifier), not measurements.
- Handling: the pre-registered estimates are reported unchanged as the confirmatory answer.
  A post-freeze, exploratory rule (`animas.analysis.implausible_rows`: a value or bound
  below one tenth of the series' fifth percentile of detected values) is applied in
  `scripts/50_changepoint.py` and `scripts/70_exploratory.py` and reported in its own
  section, with the numbers of rows it removes per cell (`reports/tables/exploratory_cleaned_grid.csv`).
  A first version of the rule (one hundredth of the median) missed the control's artefacts
  because the control's median is lower; it was replaced before the report was written and
  the replacement is the one documented here.
- Rejected: editing the pre-registration (frozen); dropping the rows silently; treating the
  qualifier-coded zeros as detected zeros (impossible on the log scale).

## 2026-10-09 Optimiser convergence flag (code, post-freeze)

- The first run reported `converged = False` for the headline and for 32 of 64 grid cells.
  Cause: `scipy.optimize.minimize(method="BFGS")` reports "precision loss" when the
  likelihood is flat near the optimum even though the score is numerically zero, and the
  pre-registration abstains on non-convergence. Fix in `animas.censored`: convergence is
  judged by the maximum absolute score (below `1e-4 * n`), with an L-BFGS-B polish when
  BFGS stops early. No estimate changed beyond optimiser noise; the number of estimable
  cells went from 20 to 52. Evidence: `tests/test_censored.py` (recovery and equality with
  OLS plus Newey-West when nothing is censored).

## 2026-10-09 Reading the pre-registered decision rule

- Primary specification: level change -19.9 percent, interval -37.7 to +3.1 (ledger
  `its.headline.*`). Rule 3 applies ("no detectable lasting change") because the primary
  interval includes zero, even though the 2010 and 2013 pre-period starts exclude it. Rule 2
  ("depends on the pre-period") was written for the opposite case (primary significant,
  others not) and does not fire; the dependence is reported in full in the grid section
  rather than by reinterpreting the rule.
- Attribution rule: the strongest blind change-point is 2010-03 (65 months before the
  release), so the pre-registered wording is "not attributable to the release". On the
  cleaned series (exploratory) the strongest split is 2016-02, six months after the release
  and four after the plant start, with an elevated segment beginning in late 2014.
- The post-period-end sensitivity (positive level change when the post-period ends in 2016,
  negative when it ends in 2025) was not anticipated by the decision rule; it is reported as
  what it is: the first post-release year sat above the counterfactual.

## 2026-10-09 Figures

- Palette and marks follow the dataviz skill's validated reference palette (categorical
  slots in fixed order, blue-red diverging ramp with a grey midpoint for signed changes, no
  dual axes: discharge gets its own stacked panel). The residual plots clip the y-axis to
  the bulk of the data and say how many points lie outside, because the artefact bounds
  would otherwise flatten the series.

## 2026-10-09 cairn: what blocked, and the workaround

- Hooks: this project was built by an agent whose working directory was the parent of the
  project, so cairn's PreToolUse, PostToolUse and Stop hooks (which fire for a `claude`
  session started inside the project) did not run. The same sensors were exercised by hand:
  `cairn verify` (with the clean rerun) and the lint stage it includes. Protected paths were
  respected by convention; `cairn.toml` was edited once, at setup, before any analysis.
- `cairn init` resolves its template directory relative to the installed package, so a
  non-editable path install of cairn copies zero template files. Workaround: cairn is an
  editable path dependency (`[tool.uv.sources]`), under which the template resolves.
- `cairn freeze` ran before the first commit, so `.cairn/frozen.json` records `git_head`
  null; the hashes are what verification uses, and the commit that follows contains the
  frozen file.
- `cairn render` renders only `report.tmpl.md`. The README, walkthrough and resume bullet
  also need ledger numbers, so `scripts/80_render_docs.py` renders their templates with
  `cairn.render` and fails on any unresolved key.
- `cairn verify` warns on bare numbers in the report template; years and the digits inside
  inline code are exempt. Gauge numbers and dates are written in inline code or as years;
  remaining warnings, if any, are reviewed in the verify output rather than suppressed.
- The test count in the README is recorded by `scripts/75_tests_count.py` from the test
  files, so even that number is not typed.
