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
| USGS Water Data API `https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items` | `parameter_code=00060`, `statistic_id=00003`, `datetime=2005-01-01/2026-10-09`, `limit=10000`, `f=csv` | HTTP 200, `api-version: 1.9.8`, 7,951 rows per gauge in one page (the downloader refuses a page that hits the limit). Note: the collection metadata links to `/ogcapi/v1/`; `v0` still answers. **Used.** |
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
| Sunnyside Mine / American Tunnel bulkheads | 1996 to 2002 (the brief said 2003; the EPA documents say 2002) | EPA Region 8 Action Memorandum, Red and Bonita Mine removal action, 2014-09-24 (SEMS DocID 1289901): "Flows from Red and Bonita Mine, Gold King (Level 7) Mine, and Mogul Mine all experienced significant increases following the construction of concrete bulkheads in Sunnyside Mine - American Tunnel between 1996 and 2002. ... Flow from the American Tunnel was reportedly approximately 1,700 gpm when it was treated prior to the final bulkhead installation." https://www.epa.gov/sites/default/files/2015-08/documents/1289901.pdf . Same wording in the EPA Community Involvement Plan for the Red and Bonita removal, January 2015: https://www.epa.gov/sites/default/files/2015-06/documents/upper-animas-red-and-bonita-removal-community-involvement-plan-1-16-2015.pdf , which adds that "water treatment of the discharge from the American Tunnel and Cement Creek was discontinued" after the bulkheads. Background on the watershed: Church, Von Guerard and Finger, eds., 2007, USGS Professional Paper 1651, https://doi.org/10.3133/pp1651 . |
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
