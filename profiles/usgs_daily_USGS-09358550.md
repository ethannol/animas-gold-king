# Profile: usgs_daily_USGS-09358550

Source: `data/raw/usgs_daily_USGS-09358550.csv` (sha256 `99ea61e35934`)
Rows: 7951  Columns: 12  Exact duplicate rows: 0
Candidate keys: [['time']]

| field | dtype | nulls | unique | notes |
|---|---|---|---|---|
| x | float64 | 0.0% | 1 | min -107.664, median -107.664, max -107.664; 7951 negative |
| y | float64 | 0.0% | 1 | min 37.8197, median 37.8197, max 37.8197 |
| time_series_id | str | 0.0% | 1 | top: b661bfc8ac7d4442b9371ac20bbc50cc(7951) |
| monitoring_location_id | str | 0.0% | 1 | top: USGS-09358550(7951) |
| parameter_code | int64 | 0.0% | 1 | min 60, median 60, max 60 |
| statistic_id | int64 | 0.0% | 1 | min 3, median 3, max 3 |
| time | str | 0.0% | 7951 | dates 2005-01-01 to 2026-10-08 |
| value | float64 | 0.3% | 993 | min 9.43, median 16.9, max 408 |
| unit_of_measure | str | 0.0% | 1 | top: ft^3/s(7951) |
| approval_status | str | 0.0% | 2 | top: Approved(7682), Provisional(269) |
| qualifier | str | 78.3% | 4 | top: ['ESTIMATED'](1549), ['ESTIMATED', 'ICE'](100), ['ICE'](69) |
| last_modified | str | 0.0% | 139 | dates 2025-03-10 to 2026-10-09 |
