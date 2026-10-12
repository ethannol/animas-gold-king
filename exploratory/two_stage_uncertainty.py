"""Remote-only supplementary full two-stage calendar-block uncertainty sensitivity."""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from animas.analysis import HEADLINE, PRIMARY, cell_series, load_samples, run_cell
from animas.its import select
from animas.uncertainty import calendar_block_sample

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=400)
    parser.add_argument("--block-months", nargs="+", type=int, default=[12, 24])
    parser.add_argument("--seed", type=int, default=20261012)
    args = parser.parse_args()
    df = select(cell_series(load_samples(), *HEADLINE), PRIMARY)
    primary = run_cell(df, PRIMARY)
    rows, summary = [], []
    for length in args.block_months:
        rng = np.random.default_rng(args.seed + length)
        for draw in range(args.draws):
            sample = calendar_block_sample(df, PRIMARY.release, length, rng)
            try:
                result = run_cell(sample, PRIMARY, hac_lags=0)
                ok = result["converged"] and result["cq_converged"]
                value = result["level_change_pct"]
                ok = bool(ok and np.isfinite(value))
                reason = "" if ok else "nonconverged or nonfinite"
            except (ValueError, np.linalg.LinAlgError, FloatingPointError) as error:
                ok, value, reason = False, np.nan, str(error)
            rows.append(dict(block_months=length, draw=draw, valid=ok,
                             level_change_pct=value, failure=reason))
            if draw % 50 == 0:
                print(length, draw, flush=True)
        vals = np.array([r["level_change_pct"] for r in rows if r["block_months"] == length and r["valid"]])
        enough = len(vals) >= max(100, .9 * args.draws)
        lo, hi = np.quantile(vals, [.025, .975]) if enough else [None, None]
        summary.append(dict(block_months=length, n_draws=args.draws, n_valid=len(vals),
                            status="exploratory interval" if enough else "abstain: insufficient valid draws",
                            percentile_lo=lo, percentile_hi=hi))
    out = ROOT / "reports/exploratory/two_stage_uncertainty"
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "draws.csv", index=False)
    payload = dict(exploratory=True, method="stratified calendar-block pairs bootstrap; both stages refitted",
                   conditional_primary=dict(point=primary["level_change_pct"], lo=primary["level_change_pct_lo"],
                                            hi=primary["level_change_pct_hi"]), sensitivity=summary,
                   seed=args.seed, source_revision=subprocess.check_output(
                       ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                   limitations=("occupied blocks resampled; dates retained; "
                                "few independent blocks; no causal attribution"),
                   baseline_unchanged=True)
    (out / "results.json").write_text(json.dumps(payload, indent=2, allow_nan=False))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
