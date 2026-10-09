"""Step 1: raw snapshot -> comparable sample table (data/derived/), with the exclusion log."""

import pandas as pd
from cairn import censored_values, record

from animas import prepare

summary = prepare.run()
for k, v in summary.items():
    record(f"prepare.{k}", v)

samples = pd.read_csv(prepare.DERIVED / "samples.csv", parse_dates=["date"])
censored_values(samples["value_raw"].astype(str).where(~samples["censored"], "<" + samples["rl"].astype(str)),
                name="censored_values(samples)")
log = pd.read_csv(prepare.DERIVED / "exclusion_log.csv")
for _, r in log.iterrows():
    record(f"prepare.excl.{r['step']}", int(r["rows_removed"]), unit="rows", note=r["rule"])
record("prepare.n_censored", int(samples["censored"].sum()), n=len(samples))
record("prepare.share_censored", float(samples["censored"].mean()))
record("prepare.first_date", str(samples["date"].min().date()))
record("prepare.last_date", str(samples["date"].max().date()))
rw = samples[samples["org"] == "CORIVWCH_WQX"]
record("prepare.riverwatch_rows", len(rw))
record("prepare.riverwatch_first", str(rw["date"].min().date()))
record("prepare.riverwatch_last", str(rw["date"].max().date()))
print(summary)
