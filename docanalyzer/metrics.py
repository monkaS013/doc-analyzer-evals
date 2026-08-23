"""Field-level precision / recall / F1 and a pass/fail gate.

A field counts as correct when the normalized prediction equals the normalized
gold value. Precision, recall, and F1 are computed per field and micro-averaged,
so both missing extractions (recall) and spurious ones (precision) are visible.
"""

from __future__ import annotations

from typing import Any

from .normalize import normalize_field


def _prf(tp: int, pred_pos: int, act_pos: int) -> dict[str, float]:
    precision = tp / pred_pos if pred_pos else 0.0
    recall = tp / act_pos if act_pos else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def score(pairs: list[tuple[dict, dict]], fields: list[str]) -> dict[str, Any]:
    """Score (gold, prediction) dict pairs over the given fields."""
    per_field: dict[str, Any] = {}
    m_tp = m_pred = m_act = m_exact = m_n = 0

    for field in fields:
        tp = pred_pos = act_pos = exact = n = 0
        for gold, pred in pairs:
            g = normalize_field(field, gold.get(field))
            p = normalize_field(field, pred.get(field))
            n += 1
            if p:
                pred_pos += 1
            if g:
                act_pos += 1
            if g and p and g == p:
                tp += 1
            if g == p:
                exact += 1
        stats = _prf(tp, pred_pos, act_pos)
        stats["accuracy"] = exact / n if n else 0.0
        stats["support"] = act_pos
        per_field[field] = stats
        m_tp += tp
        m_pred += pred_pos
        m_act += act_pos
        m_exact += exact
        m_n += n

    overall = _prf(m_tp, m_pred, m_act)
    overall["accuracy"] = m_exact / m_n if m_n else 0.0
    return {"overall": overall, "per_field": per_field}


def gate(metrics: dict[str, Any], min_f1: float) -> bool:
    """Return True if the overall F1 meets the threshold."""
    return metrics["overall"]["f1"] >= min_f1
