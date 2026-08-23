"""Structured document extraction with a gold-standard evaluation harness."""

from .schema import ExtractedDocument, FIELDS
from .metrics import score, gate
from .harness import load_records, run_eval

__all__ = ["ExtractedDocument", "FIELDS", "score", "gate", "load_records", "run_eval"]
