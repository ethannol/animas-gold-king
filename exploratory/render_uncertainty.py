"""Render the separately recorded sensitivity; no model fits or baseline writes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / "reports/exploratory/two_stage_uncertainty"
    results = json.loads((output / "results.json").read_text())
    flat = {}
    lines = ["# Recorded exploratory two-stage uncertainty", "",
             ("Both models were refitted on calendar-block pairs samples; "
              "original timestamps and censoring were retained."),
             "", "| Block length (months) | Valid / attempted draws | Exploratory percentile interval (%) |",
             "| --- | --- | --- |"]
    for arm in results["sensitivity"]:
        length = arm["block_months"]
        flat[f"block{length}"] = dict(lo=arm["percentile_lo"], hi=arm["percentile_hi"],
                                      n_valid=arm["n_valid"], n_draws=arm["n_draws"])
        lo, hi = arm["percentile_lo"], arm["percentile_hi"]
        interval = f"{lo:+.2f} to {hi:+.2f}" if lo is not None else arm["status"]
        lines.append(f"| {length} | {arm['n_valid']} / {arm['n_draws']} | {interval} |")
    baseline = results["conditional_primary"]
    lines += ["", f"The original conditional point is {baseline['point']:+.2f} percent, with its conditional interval "
              f"{baseline['lo']:+.2f} to {baseline['hi']:+.2f} percent.", "",
              "These supplementary intervals do not replace the frozen verdict or identify causation.",
              "", "The occupied-block pairs method, few independent blocks and chosen lengths limit interpretation; "
              "nominal coverage is not independently established.", "",
              f"Measured on the Mac mini from source `{results['source_revision']}`, seed `{results['seed']}`. "
              "[Methods](two-stage-uncertainty.md), "
              "[machine-readable results](../reports/exploratory/two_stage_uncertainty/results.json), "
              "[all draw diagnostics](../reports/exploratory/two_stage_uncertainty/draws.csv).", ""]
    (output / "summary.json").write_text(json.dumps(flat, indent=2)+"\n")
    (ROOT / "docs/uncertainty-results.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
