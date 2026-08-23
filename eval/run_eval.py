"""Run the extractor over the gold set, print a report, and gate on F1.

    python eval/run_eval.py --min-f1 0.8

Exits non-zero if the overall F1 is below the threshold, so it can guard a build.
Needs ANTHROPIC_API_KEY, since it calls the real extractor.
"""

from __future__ import annotations

import argparse
import os
import sys

# Make the repo root importable when run as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docanalyzer.extractor import extract
from docanalyzer.harness import load_records, run_eval
from docanalyzer.metrics import gate


def _format(metrics: dict) -> str:
    lines = ["field            precision  recall     f1      support"]
    for field, s in metrics["per_field"].items():
        lines.append(
            f"{field:<16} {s['precision']:.3f}      {s['recall']:.3f}    "
            f"{s['f1']:.3f}   {s['support']}"
        )
    o = metrics["overall"]
    lines.append("-" * 52)
    lines.append(
        f"{'OVERALL (micro)':<16} {o['precision']:.3f}      {o['recall']:.3f}    "
        f"{o['f1']:.3f}"
    )
    lines.append(f"exact-match accuracy: {o['accuracy']:.3f}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate document extraction.")
    parser.add_argument("--gold", default="eval/gold_standard.jsonl")
    parser.add_argument(
        "--min-f1", type=float, default=float(os.environ.get("EVAL_MIN_F1", "0.8"))
    )
    args = parser.parse_args()

    records = load_records(args.gold)
    metrics, _ = run_eval(records, extract)
    print(_format(metrics))

    if gate(metrics, args.min_f1):
        print(f"\nPASS — F1 {metrics['overall']['f1']:.3f} >= {args.min_f1}")
        return 0
    print(f"\nFAIL — F1 {metrics['overall']['f1']:.3f} < {args.min_f1}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
