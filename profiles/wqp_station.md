# Profile: wqp_station

Source: `data/raw/wqp_station.csv` (sha256 `638f2edc592a`)
Rows: 32  Columns: 37  Exact duplicate rows: 0
Candidate keys: [['MonitoringLocationIdentifier']]

| field | dtype | nulls | unique | notes |
|---|---|---|---|---|
| OrganizationIdentifier | str | 0.0% | 9 | top: USEPA_REGION8(7), 21COL001_WQX(5), BPMWQX(5) |
| OrganizationFormalName | str | 0.0% | 9 | top: USEPA Region 8(7), Colorado Dept. of Public Health & Environment-WQCD(5), Bonita Peak Mining(5) |
| MonitoringLocationIdentifier | str | 0.0% | 32 | top: USGS-09358000(1), USGS-09358550(1), USGS-09359020(1) |
| MonitoringLocationName | str | 0.0% | 28 | top: A68(2), A72(2), CC48(2) |
| MonitoringLocationTypeName | str | 0.0% | 3 | top: River/Stream(22), Stream(5), CERCLA Superfund Site(5) |
| MonitoringLocationDescriptionText | str | 71.9% | 9 | top: The site is by USGS station 09359020, sometimes referred to as A-72.(1), 14th Street Gauge @ 13th Street Bridge(1), Animas Gauge below Silverton(1) |
| HUCEightDigitCode | int64 | 0.0% | 1 | min 1.40801e+07, median 1.40801e+07, max 1.40801e+07 |
| DrainageAreaMeasure/MeasureValue | float64 | 84.4% | 5 | min 20.1, median 146, max 1090 |
| DrainageAreaMeasure/MeasureUnitCode | str | 84.4% | 1 | top: sq mi(5) |
| ContributingDrainageAreaMeasure/MeasureValue | float64 | 100.0% | 0 |  |
| ContributingDrainageAreaMeasure/MeasureUnitCode | float64 | 100.0% | 0 |  |
| LatitudeMeasure | float64 | 0.0% | 31 | min 37.0323, median 37.7901, max 37.82 |
| LongitudeMeasure | float64 | 0.0% | 31 | min -107.886, median -107.668, max -107.658; 32 negative |
| SourceMapScaleNumeric | float64 | 46.9% | 4 | min 0, median 24000, max 160000 |
| HorizontalAccuracyMeasure/MeasureValue | float64 | 84.4% | 2 | min 1, median 5, max 5 |
| HorizontalAccuracyMeasure/MeasureUnitCode | str | 84.4% | 1 | top: seconds(5) |
| HorizontalCollectionMethodName | str | 0.0% | 7 | top: Interpolation-Map(8), GPS-Unspecified(8), GPS Code (Pseudo Range) Standard Position (SA Off)(5) |
| HorizontalCoordinateReferenceSystemDatumName | str | 0.0% | 2 | top: NAD83(22), WGS84(10) |
| VerticalMeasure/MeasureValue | float64 | 65.6% | 11 | min 0, median 9199, max 9380 |
| VerticalMeasure/MeasureUnitCode | str | 65.6% | 2 | top: ft(6), feet(5) |
| VerticalAccuracyMeasure/MeasureValue | float64 | 84.4% | 5 | min 0.14, median 4.3, max 15 |
| VerticalAccuracyMeasure/MeasureUnitCode | str | 84.4% | 1 | top: feet(5) |
| VerticalCollectionMethodName | str | 68.8% | 6 | top: Topographic Map Interpolation(5), Interpolated from topographic map.(1), Unknown.(1) |
| VerticalCoordinateReferenceSystemDatumName | str | 65.6% | 4 | top: SEALV(5), NGVD29(3), NAVD88(2) |
| CountryCode | str | 0.0% | 1 | top: US(32) |
| StateCode | int64 | 0.0% | 1 | min 8, median 8, max 8 |
| CountyCode | int64 | 0.0% | 2 | min 67, median 111, max 111 |
| AquiferName | float64 | 100.0% | 0 |  |
| LocalAqfrName | float64 | 100.0% | 0 |  |
| FormationTypeText | float64 | 100.0% | 0 |  |
| AquiferTypeName | float64 | 100.0% | 0 |  |
| ConstructionDateText | float64 | 100.0% | 0 |  |
| WellDepthMeasure/MeasureValue | float64 | 100.0% | 0 |  |
| WellDepthMeasure/MeasureUnitCode | float64 | 100.0% | 0 |  |
| WellHoleDepthMeasure/MeasureValue | float64 | 100.0% | 0 |  |
| WellHoleDepthMeasure/MeasureUnitCode | float64 | 100.0% | 0 |  |
| ProviderName | str | 0.0% | 2 | top: STORET(27), NWIS(5) |
