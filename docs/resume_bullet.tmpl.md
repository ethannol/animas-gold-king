# Resume bullet (measured results only; rendered from the ledger)

- Built a pre-registered, flow-adjusted interrupted time series on {{prepare.sample_rows}}
  public water-quality records (Water Quality Portal, USGS Water Data API; {{prepare.n_orgs}}
  organisations, 2005 to 2025) to test whether the 2015 Gold King Mine release left a
  lasting signal in Cement Creek and the Animas River; censored (Tobit) regression with
  Newey-West uncertainty, a {{grid.n_fits}}-fit sensitivity grid, a blind change-point
  search and an upstream control, run under a verification harness ({{tests.n_tests}}
  tests, clean-rerun check, every reported number traced to a ledger).
- Showed that the apparent post-release decline in dissolved zinc ({{its.headline.level_change_pct:.0f}}
  percent, interval {{its.headline.level_change_pct_lo:.0f}} to
  {{its.headline.level_change_pct_hi:.0f}}) is not detectable against the full pre-period,
  depends on the pre-period start and post-period end, did not begin at the release
  (strongest blind change-point {{cp.headline.strongest_rel_release_months}} months away),
  and is inseparable from the treatment plant that started two months later;
  {{mult.n_bh_sig}} of {{mult.n_estimable}} estimable site-metal cells survive false-discovery
  control.
