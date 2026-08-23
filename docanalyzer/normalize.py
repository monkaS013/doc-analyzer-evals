"""Field normalization, so "R$ 1.234,56" and "1234.56" count as the same answer.

Both the gold value and the prediction pass through the same normalizer before
comparison — that's what makes the eval fair instead of punishing formatting.
"""

from __future__ import annotations

import re
from datetime import datetime

_WS_RE = re.compile(r"\s+")
_DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y"]


def normalize_text(value: str) -> str:
    return _WS_RE.sub(" ", value.strip().lower())


def normalize_date(value: str) -> str:
    s = value.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return normalize_text(s)


def normalize_money(value: str) -> str:
    s = re.sub(r"[^\d.,-]", "", value)
    if not s:
        return ""
    if "," in s and "." in s:
        # The rightmost separator is the decimal point.
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        # Comma-only: decimal if it's `,dd` at the end, otherwise a thousands sep.
        s = s.replace(",", ".") if re.search(r",\d{2}$", s) else s.replace(",", "")
    try:
        return f"{float(s):.2f}"
    except ValueError:
        return ""


def normalize_field(field: str, value) -> str:
    """Normalize a value according to what kind of field it is."""
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    if field.endswith("date"):
        return normalize_date(s)
    if field.endswith("amount"):
        return normalize_money(s)
    return normalize_text(s)
