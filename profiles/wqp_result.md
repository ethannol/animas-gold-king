# Profile: wqp_result

Source: `data/raw/wqp_result.csv` (sha256 `7fab0e732d52`)
Rows: 38236  Columns: 81  Exact duplicate rows: 0
Candidate keys: [['ResultIdentifier']]

| field | dtype | nulls | unique | notes |
|---|---|---|---|---|
| OrganizationIdentifier | str | 0.0% | 9 | top: CORIVWCH_WQX(16706), ARSG(6217), SOUTHUTE(6146) |
| OrganizationFormalName | str | 0.0% | 9 | top: Colorado River Watch(16706), Animas River Stakeholders Group (Colorado) (Volunteer)(6217), Southern Ute Tribe(6146) |
| ActivityIdentifier | str | 0.0% | 5598 | top: ARSG-A68070620051A680720050(111), ARSG-A72070620051A720720050(111), ARSG-CC48070620051CC480720050(111) |
| ActivityTypeCode | str | 0.0% | 9 | top: Sample-Routine(28316), Field Msr/Obs-Portable Data Logger(5016), Field Msr/Obs(4154) |
| ActivityMediaName | str | 0.0% | 4 | top: Water(36734), Sediment(1310), Tissue(160) |
| ActivityMediaSubdivisionName | str | 35.9% | 4 | top: Surface Water(23714), Surface Water Sediment(662), Surface Soil/Sediment(120) |
| ActivityStartDate | str | 0.0% | 1675 | dates 2005-01-10 to 2026-07-29 |
| ActivityStartTime/Time | str | 10.7% | 273 | dates 2026-10-09 to 2026-10-09 |
| ActivityStartTime/TimeZoneCode | str | 10.7% | 2 | top: MST(29537), MDT(4591) |
| ActivityEndDate | str | 86.9% | 1040 | dates 2016-03-14 to 2021-08-31 |
| ActivityEndTime/Time | str | 86.9% | 2 | dates 2026-10-09 to 2026-10-09 |
| ActivityEndTime/TimeZoneCode | str | 86.9% | 2 | top: MST(5016), MDT(4) |
| ActivityRelativeDepthName | float64 | 100.0% | 0 |  |
| ActivityDepthHeightMeasure/MeasureValue | float64 | 100.0% | 0 |  |
| ActivityDepthHeightMeasure/MeasureUnitCode | float64 | 100.0% | 0 |  |
| ActivityDepthAltitudeReferencePointText | str | 99.5% | 1 | top: Surface(210) |
| ActivityTopDepthHeightMeasure/MeasureValue | float64 | 100.0% | 0 |  |
| ActivityTopDepthHeightMeasure/MeasureUnitCode | float64 | 100.0% | 0 |  |
| ActivityBottomDepthHeightMeasure/MeasureValue | float64 | 100.0% | 0 |  |
| ActivityBottomDepthHeightMeasure/MeasureUnitCode | float64 | 100.0% | 0 |  |
| ProjectIdentifier | str | 6.7% | 11 | mixed numeric/text: ['ARSGDATA', 'Ambient Monitoring', 'SWMN', 'Quarterly Annual', 'Special_Studies']; top: 1(16706), ARSGDATA(6217), Ambient Monitoring;Animas_SanJuan_Watershed(5022) |
| ProjectName | str | 7.0% | 12 | top: Colorado River Watch(16706), ARSG Data(6217), Ambient Monitoring;Gold King Mine Release(5022) |
| ActivityConductingOrganizationText | str | 85.9% | 4 | top: CDPHE-WQCD(2838), U.S. Geological Survey-Water Resources Discipline(1611), U.S. Geological Survey(937) |
| MonitoringLocationIdentifier | str | 0.0% | 32 | top: SOUTHUTE-AR 2-7(6146), CORIVWCH_WQX-103(4376), CORIVWCH_WQX-323(4255) |
| MonitoringLocationName | str | 7.0% | 22 | top: Animas River 2-7(6146), Animas - 13th St Br(4376), Cement Cr - Cement Cr(4255) |
| ActivityCommentText | str | 78.4% | 158 | top: BOR, Cement Creek at mout(1313), CRW, Animas River below C(1251), BOR, Animas River below C(1034) |
| SampleAquifer | float64 | 100.0% | 0 |  |
| HydrologicCondition | str | 93.3% | 7 | top: Stable, normal stage(1803), Falling stage(307), Stable, high stage(212) |
| HydrologicEvent | str | 93.3% | 3 | top: Routine sample(1806), Snowmelt(474), Storm(288) |
| ActivityLocation/LatitudeMeasure | float64 | 7.0% | 25 | min 37.0323, median 37.7906, max 37.82 |
| ActivityLocation/LongitudeMeasure | float64 | 7.0% | 25 | min -107.886, median -107.668, max -107.658; 35550 negative |
| SampleCollectionMethod/MethodIdentifier | str | 27.1% | 18 | top: SM 1060B(16706), UNKNOWN(2469), STREAM_1_WQX(2412) |
| SampleCollectionMethod/MethodIdentifierContext | str | 27.1% | 9 | top: CORIVWCH_WQX(16706), 21COL001_WQX(2838), ARSG(2469) |
| SampleCollectionMethod/MethodName | str | 27.1% | 18 | top: SM 1060B(16706), unknown sample collection(2469), WQCD Stream Sampling Procedure(2412) |
| SampleCollectionMethod/MethodDescriptionText | str | 92.8% | 2 | top: unknown sample collection(2469), SAP(303) |
| SampleCollectionEquipmentName | str | 23.4% | 17 | top: Water Bottle(19463), Miscellaneous (Other)(3865), Water Sampler (Other)(2412) |
| ResultIdentifier | str | 0.0% | 38236 | top: NWIS-88923543(1), NWIS-88922981(1), NWIS-88922707(1) |
| ResultDetectionConditionText | str | 92.1% | 5 | top: Not Detected at Detection Limit(1316), Not Detected(1271), Detected Not Quantified(243) |
| MethodSpeciationName | float64 | 100.0% | 0 |  |
| CharacteristicName | str | 0.0% | 12 | top: Flow(3765), Specific conductance(3627), pH(3498) |
| ResultSampleFractionText | str | 29.2% | 6 | top: Dissolved(13081), Total(12417), Total Recoverable(1036) |
| ResultMeasureValue | str | 6.2% | 10204 | CENSORED: {'lt_prefixed': 14, 'markers': 0}; mixed numeric/text: ['<0.12', '<16', '<0.6', '<3.2']; top: 0(2607), 20(302), 1(241) |
| ResultMeasure/MeasureUnitCode | str | 10.2% | 15 | top: ug/L(22053), ft3/sec(3764), mS/cm(3130) |
| MeasureQualifierCode | str | 84.0% | 15 | CENSORED: {'lt_prefixed': 0, 'markers': 4041}; top: DL(2252), U(1789), J(1147) |
| ResultStatusIdentifier | str | 0.0% | 4 | top: Final(18611), Validated(16607), Accepted(1875) |
| StatisticalBaseCode | str | 86.9% | 3 | top: Mean(1672), Maximum(1672), Minimum(1672) |
| ResultValueTypeName | str | 0.6% | 3 | top: Actual(32985), Calculated(5016), Estimated(14) |
| ResultWeightBasisText | str | 98.4% | 2 | top: Wet(400), Dry(208) |
| ResultTimeBasisText | str | 86.9% | 1 | top: 24 Hours(5016) |
| ResultTemperatureBasisText | str | 99.4% | 1 | top: 25 deg C(247) |
| ResultParticleSizeBasisText | float64 | 100.0% | 0 |  |
| DataQuality/PrecisionValue | float64 | 100.0% | 0 |  |
| DataQuality/BiasValue | float64 | 100.0% | 0 |  |
| DataQuality/ConfidenceIntervalValue | float64 | 100.0% | 0 |  |
| DataQuality/UpperConfidenceLimitValue | float64 | 100.0% | 0 |  |
| DataQuality/LowerConfidenceLimitValue | float64 | 100.0% | 0 |  |
| ResultCommentText | str | 95.4% | 85 | top: Metals Analysis(303), Metals in Solids by ICP-AES(229), Metals in Water by ICP-AES(186) |
| USGSPCode | float64 | 93.3% | 28 | min 61, median 1049, max 90095 |
| ResultDepthHeightMeasure/MeasureValue | float64 | 100.0% | 0 |  |
| ResultDepthHeightMeasure/MeasureUnitCode | float64 | 100.0% | 0 |  |
| ResultDepthAltitudeReferencePointText | str | 99.9% | 1 | top: Surface(30) |
| SubjectTaxonomicName | str | 99.6% | 9 | top: Pantosteus discobolus(48), Salmo trutta(30), Catostomus latipinnis(24) |
| SampleTissueAnatomyName | str | 99.6% | 2 | top: Muscle/Muscle Tissue(144), Tissue, Unspecified(16) |
| BinaryObjectFileName | float64 | 100.0% | 0 |  |
| BinaryObjectFileTypeCode | float64 | 100.0% | 0 |  |
| ResultFileUrl | float64 | 100.0% | 0 |  |
| ResultAnalyticalMethod/MethodIdentifier | str | 16.2% | 38 | mixed numeric/text: ['EL006', 'PLM43', 'PLM48', 'PLA15', 'PLA11']; top: 200.15(15390), USGS(3505), UNKNOWN(2712) |
| ResultAnalyticalMethod/MethodIdentifierContext | str | 16.2% | 5 | top: USEPA(23951), ARSG(6217), USGS(1529) |
| ResultAnalyticalMethod/MethodName | str | 16.5% | 38 | top: Metals in Water by Nebulization and ICP-AES(15390), USGS est# provisional(3505), unknown analytical procedure(2712) |
| ResultAnalyticalMethod/MethodUrl | float64 | 100.0% | 0 |  |
| ResultAnalyticalMethod/MethodDescriptionText | str | 75.5% | 19 | top: https://www.nemi.gov/methods/method_summary/4665/(3448), https://www.nemi.gov/methods/method_summary/4690/(2837), https://www.nemi.gov/methods/method_summary/4685/(1182) |
| LaboratoryName | str | 84.7% | 13 | top: LSD(1970), USGS-National Water Quality Lab, Denver, CO(981), AGAT Laboratories, Mississauga, Ontario, Canada(704) |
| AnalysisStartDate | str | 42.3% | 1218 | dates 1930-01-02 to 2026-08-05 |
| ResultLaboratoryCommentText | str | 99.4% | 14 | top: sample was diluted(72), see result laboratory comment(66), below the reporting level but at or above the detection level(32) |
| ResultDetectionQuantitationLimitUrl | str | 56.1% | 16777 | top: https://waterqualitydata.us/data/providers/STORET/organizations/ARSG/activities/ARSG-A72091520051A72C0920050/results/526631744/resdetectqntlmts(1), https://waterqualitydata.us/data/providers/STORET/organizations/ARSG/activities/ARSG-A68070620051A68C0720050/results/526571424/resdetectqntlmts(1), https://waterqualitydata.us/data/providers/STORET/organizations/ARSG/activities/ARSG-A68040920051A68C0420050/results/526563078/resdetectqntlmts(1) |
| DetectionQuantitationLimitTypeName | str | 52.5% | 14 | top: Lower Reporting Limit(13492), Method Detection Level(2125), Lower Quantitation Limit(1187) |
| DetectionQuantitationLimitMeasure/MeasureValue | float64 | 52.5% | 398 | min 0, median 4.9, max 5080 |
| DetectionQuantitationLimitMeasure/MeasureUnitCode | str | 52.5% | 8 | top: ug/L(14093), mg/L(1301), ug/l(1288) |
| LabSamplePreparationUrl | float64 | 100.0% | 0 |  |
| LastUpdated | str | 7.0% | 2278 | dates 2016-03-22 to 2026-09-15 |
| ProviderName | str | 0.0% | 2 | top: STORET(35668), NWIS(2568) |
