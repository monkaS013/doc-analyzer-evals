"""Glue between the gold set, an extractor, and the metrics.

``run_eval`` takes the extractor as an argument, so tests drive the whole harness
with a fake extractor and no network call.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from .metrics import score
from .schema import FIELDS


def load_records(path: str) -> list[dict]:
    """Load a gold-standard JSONL file: one {"text", "expected"} object per line."""
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def run_eval(
    records: list[dict],
    extract_fn: Callable[[str], Any],
    fields: list[str] = FIELDS,
) -> tuple[dict, list[tuple[dict, dict]]]:
    """Run the extractor over every record and score it. Returns (metrics, pairs)."""
    pairs: list[tuple[dict, dict]] = []
    for rec in records:
        pred = extract_fn(rec["text"])
        pred_dict = pred.model_dump() if hasattr(pred, "model_dump") else dict(pred)
        pairs.append((rec["expected"], pred_dict))
    return score(pairs, fields), pairs
