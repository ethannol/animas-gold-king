# Data dictionary

All inputs are public records retrieved on 2026-10-09 by `scripts/download.py` from the
query in `data/raw/query.json`; URLs, HTTP headers, SHA-256 digests and row counts are in
`data/raw/manifest.json`. Field definitions for the Water Quality Portal tables are in
`data/dictionary/wqp_fields.csv`, reused from the groundwater-audit sibling project, which
built it from the portal's user guide (field name, one-line definition). Nothing in
`data/raw/` is modified by the pipeline.

## wqp_result.csv

- Source: Water Quality Portal, legacy web service `/data/Result/search`, data profile
  `resultPhysChem`, `mimeType=csv`. Providers NWIS (USGS) and STORET (EPA WQX).
- One row represents: one analytical or field result (one characteristic, one fraction)
  from one sampling activity at one monitoring location. Candidate key: `ResultIdentifier`.
- Rows: 38,236 (NWIS 2,568; STORET 35,668) across 32 sites.
- Fields relied on (name: meaning; null convention):
  - `OrganizationIdentifier` / `OrganizationFormalName`: who submitted the record.
    `USGS-CO`, `USGS-NM` (NWIS); `CORIVWCH_WQX` Colorado River Watch; `ARSG` Animas River
    Stakeholders Group; `USEPA_REGION8` and `BPMWQX` EPA Region 8 (the latter the Bonita
    Peak Mining District Superfund programme); `21COL001`, `21COL001_WQX` Colorado
    Department of Public Health and Environment; `SOUTHUTE` Southern Ute Indian Tribe.
  - `MonitoringLocationIdentifier`: station; mapped to a reach and role by `query.json`.
  - `ActivityIdentifier`, `ActivityTypeCode`: the sampling event and its kind.
    `Sample-Routine`, `Sample`, `Field Msr/Obs` are population rows; `Quality Control
    Sample-*` rows are QC; `Field Msr/Obs-Portable Data Logger` rows are daily data-logger
    statistics (`StatisticalBaseCode` Mean/Minimum/Maximum), not samples.
  - `ActivityMediaName` / `ActivityMediaSubdivisionName`: Water, Sediment, Soil, Tissue.
  - `ActivityStartDate` (`YYYY-MM-DD`), `ActivityStartTime/Time`, time zone.
  - `CharacteristicName`: analyte. Requested: Zinc, Copper, Lead, Cadmium, Iron,
    Manganese, Aluminum, Arsenic, pH, Specific conductance, Flow, Stream flow,
    instantaneous, Flow rate, instantaneous.
  - `ResultSampleFractionText`: Dissolved; Total, Total Recoverable, Total Recovrble,
    Recoverable (whole-water digestion); blank for field parameters and for some USGS
    metal rows; Suspended; Unfiltered, field.
  - `ResultMeasureValue`, `ResultMeasure/MeasureUnitCode`: value and unit. Units seen
    for metals: ug/L, ug/l, mg/L, mg/kg (sediment). Conductance: uS/cm, umho/cm,
    uS/cm @25C, mS/cm. pH: std units, None, blank. A handful of values are `<x` strings.
  - `ResultDetectionConditionText`: `Not Detected`, `Not Detected at Detection Limit`,
    `*Non-detect`, `Detected Not Quantified` (treated as censored), `Not Reported` (no
    value), `Present Above Quantification Limit`; blank means a reported value.
  - `DetectionQuantitationLimitTypeName`, `DetectionQuantitationLimitMeasure/MeasureValue`,
    `.../MeasureUnitCode`: the reporting or detection limit and its unit. Colorado River
    Watch populates the limit only from 2013 on for detected rows, and always for
    non-detects.
  - `MeasureQualifierCode`: laboratory qualifiers (`U`, `DL`, `J`, ...).
  - `ResultAnalyticalMethod/MethodIdentifier`, `MethodName`, `LaboratoryName`, `USGSPCode`,
    `ResultStatusIdentifier`, `ResultValueTypeName`: method, lab, USGS parameter code,
    review status, actual/estimated/calculated.
- Known quirks: the same query on the WQX3 `fullPhysChem` profile returned 35,668 rows,
  exactly the STORET count: the WQX3 profile omitted every NWIS row on 2026-10-09.

## wqp_station.csv

- Source: `/data/Station/search` for the same site list. One row per monitoring location
  (32). Fields used: identifier, name, organisation, type, latitude, longitude, HUC8,
  drainage area.

## usgs_daily_USGS-<gauge>.csv (five files)

- Source: USGS Water Data API, OGC API Features collection `daily`,
  `https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items`, `f=csv`,
  `parameter_code=00060` (discharge), `statistic_id=00003` (daily mean),
  `datetime=2005-01-01/2026-10-09`. Response header `api-version: 1.9.8`.
- One row represents: one daily mean discharge value for one gauge. Key:
  (`monitoring_location_id`, `time`).
- Fields: `time` (date), `value` (ft^3/s, string), `unit_of_measure`, `approval_status`
  (Approved/Provisional), `qualifier` (list such as `['ESTIMATED']`, `['ICE']`),
  `time_series_id`, `last_modified`, `x`, `y`.
- Rows: 7,951 per gauge (7,947 for 09359020) for 2005-01-01 to 2026-10-08.

## query.json and manifest.json

- `query.json`: the full query, the reach definitions (site to reach, role, paired gauge)
  and notes on how the site list was chosen. `manifest.json`: download date, per-file
  URL, status, headers, SHA-256, bytes, rows; probes of the WQX3 profile and the legacy
  `waterservices.usgs.gov/nwis/dv` endpoint.
