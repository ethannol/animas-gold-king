# Animas River after Gold King

Did the 5 August 2015 Gold King Mine release leave a lasting, flow-adjusted signal in
Cement Creek and the Animas River, and can any change be told apart from the Gladstone
treatment plant that started treating the same discharge two months later? A
pre-registered interrupted time series on public USGS and Water Quality Portal data,
built and verified under the [cairn](../cairn) harness.

## Main findings (every number here is rendered from `artifacts/numbers.json`)

- Headline cell, dissolved zinc in Cement Creek (Colorado River Watch monthly samples,
  {{its.headline.n}} samples 2005 to 2025, USGS gauge `09358550` discharge): flow-adjusted
  level change at the release {{its.headline.level_change_pct:.0f}} percent (interval
  {{its.headline.level_change_pct_lo:.0f}} to {{its.headline.level_change_pct_hi:.0f}},
  p = {{its.headline.level_change_p:.2f}}). Pre-registered verdict:
  **{{its.headline.verdict}}**.
- The verdict depends on the pre-period: starting it in 2010 gives
  {{grid.pre2010.level_change_pct:.0f}} percent ({{grid.pre2010.level_change_pct_lo:.0f}} to
  {{grid.pre2010.level_change_pct_hi:.0f}}) and in 2013 {{grid.pre2013.level_change_pct:.0f}}
  percent ({{grid.pre2013.level_change_pct_lo:.0f}} to {{grid.pre2013.level_change_pct_hi:.0f}});
  the 2005 pre-period carries a rising trend of {{its.headline.pre_slope_pct_per_yr:.1f}}
  percent per year that the counterfactual extrapolates. Ending the post-period in 2016
  flips the sign to {{grid.pre2005_plume20150930_post2016.level_change_pct:.0f}} percent.
  See `reports/figures/sensitivity_grid.png`.
- Blind change-points do not sit at the release: the strongest split is
  {{cp.headline.strongest_month}} ({{cp.headline.strongest_rel_release_months}} months from
  it); on the series with three coding artefacts removed the strongest split is
  {{cp.explore.strongest_month}}, {{cp.explore.strongest_rel_release_months}} months after the
  release and {{cp.explore.strongest_rel_plant_months}} months after the treatment plant started.
- The upstream control's pre-registered change ({{did.control_zinc.level_change_pct:.0f}}
  percent) is driven by {{explore.clean.control.n_rows_removed}} zero-valued "non-detects";
  without them it is {{explore.clean.control.level_change_pct:.0f}} percent
  ({{explore.clean.control.level_change_pct_lo:.0f}} to {{explore.clean.control.level_change_pct_hi:.0f}}).
  The difference-in-differences level change is {{did.headline.level_change_pct:.0f}} percent
  ({{did.headline.level_change_pct_lo:.0f}} to {{did.headline.level_change_pct_hi:.0f}}) with a
  differential downward slope after 2015.
- Across {{mult.n_cells}} reach x constituent x fraction cells, {{mult.n_estimable}} are
  estimable, {{mult.n_raw_sig}} have raw p below {{const.alpha}} and {{mult.n_bh_sig}} survive
  false-discovery control.
- Sampling at the four Silverton-to-Durango reaches went from {{coverage.r4.events_per_year_pre}}
  to {{coverage.r4.events_per_year_post2y}} events a year in the two years after the plant
  started. Pooling the organisations that began then gives a level change of
  {{explore.pooled.level_change_pct:.0f}} percent, about double the single-organisation
  estimate; the design uses one organisation across the release for that reason.

Full report: `reports/report.md`. Five-minute script: `docs/walkthrough.md`.

![Sensitivity grid](reports/figures/sensitivity_grid.png)

## What is not claimed

No attribution of any change to the release: the release and the treatment plant start
are two months apart, inside the resolution of a monthly series. No health, ecological,
compliance or legal conclusion. No claim about any single cell in the multiplicity grid.
Stage-two intervals do not carry stage-one estimation error.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and the cairn checkout beside this directory
(`../cairn`, pinned to commit `a184e0732989373856039dea2919ccd96a88e8b1`; cairn is an
editable path dependency in `pyproject.toml`). Python 3.12 is pinned in `.python-version`
and `uv.lock`.

```bash
uv sync --extra dev          # environment, including cairn from ../cairn
uv run pytest                # focused tests of every model component
uv run cairn run             # scripts/00..80 in order, offline, from the committed snapshot
uv run cairn verify          # frozen plan, checks, lint, placeholders, clean rerun
uv run cairn render          # reports/report.md from report.tmpl.md and the ledger
uv run python scripts/download.py   # ONLY to refresh the snapshot (network); re-freeze after
```

Everything deterministic runs from a fresh checkout without network access.

## Data provenance

- `data/raw/query.json` is the query; `data/raw/manifest.json` records for every file the
  URL, date, HTTP headers, SHA-256, bytes and row count, plus probes of the alternatives.
- Water quality: Water Quality Portal legacy `/data/Result/search`, profile
  `resultPhysChem` ({{snapshot.wqp_result_rows}} rows). The WQX3 `fullPhysChem` profile
  returned {{snapshot.wqx3_rows}} rows for the same query, missing every USGS row.
- Discharge: USGS Water Data API `ogcapi/v0/collections/daily` (api-version
  {{snapshot.api_version}}), {{snapshot.daily_rows_total}} daily values; the legacy
  `waterservices.usgs.gov/nwis/dv` endpoint still answered (HTTP {{snapshot.legacy_dv_status}})
  and was not used.
- Reaches and roles: Cement Creek at Silverton (impacted), Animas above Cement Creek
  (control), Animas below Silverton (impacted), Animas at Durango and near Cedar Hill
  (downstream). Field dictionary: `data/dictionary/wqp_fields.csv` (reused from the
  groundwater-audit sibling). Data dictionary: `docs/data_dictionary.md`.
- Exclusion log: `data/derived/exclusion_log.csv` and `data/derived/excluded.csv`.

## Layout

```
src/animas/      acquire, units, prepare, censored (Tobit + Newey-West), cq, its, changepoint, analysis, figures
scripts/         00_snapshot 10_prepare 20_coverage 30_cq 40_its 50_changepoint 60_did 70_exploratory 80_render_docs; download.py
data/raw/        committed public snapshot (immutable, hashed by cairn freeze)
data/derived/    sample table, QC, flow, exclusion log, daily discharge, sites
artifacts/       numbers.json (ledger), checks.jsonl
reports/         report.md (rendered), figures/, tables/
docs/            prereg.md (frozen), decisions.md, data_dictionary.md, walkthrough.md, resume_bullet.md
tests/           {{tests.n_tests}} pytest tests
```

## How AI was used

This project was built in a Claude Code session with Claude Fable 5.1 from the project
brief: the agent verified the endpoints and the confounder timeline against published
sources, wrote the acquisition, preparation, models, tests, scripts and templates, and ran
the pipeline under cairn. The author reviewed the pre-registration, the tests and the
findings. No language model is called by the pipeline.

## License

MIT for the code. USGS data are public domain; partner data are as published through the
Water Quality Portal.
