# Exploratory full two-stage uncertainty

The original ITS intervals condition on the estimated concentration-discharge adjustment. This supplementary pairs-bootstrap sensitivity resamples occupied calendar blocks separately before and after the release, preserving all measurement/discharge/censoring pairs and their original timestamps. The plume-free primary window is used. Both C-Q and ITS models are refitted on every draw; nothing is substituted for non-detects. Original trend and seasonal design values remain tied to dates.

```sh
uv run python exploratory/two_stage_uncertainty.py --draws 400 --block-months 12 24
```

Run on the analysis machine only. Separate outputs in `reports/exploratory/two_stage_uncertainty/` include every draw, convergence failures, percentile intervals, seed and source revision. A sensitivity arm abstains unless at least 90% of draws and at least 100 draws converge. This is a calendar-block pairs sensitivity, not a claim of calibrated coverage or causal attribution: occupied blocks and few independent long blocks constrain interpretation. Block lengths were chosen after the preregistration, and the frozen primary point, intervals and verdict remain unchanged.

[Recorded supplementary results](uncertainty-results.md). Regenerate its table with `uv run python exploratory/render_uncertainty.py`; no model fits occur in that command.

The required prepared sample table is committed, so this supplementary command needs no numbered preparation step and writes no primary ledger/check bookkeeping.
