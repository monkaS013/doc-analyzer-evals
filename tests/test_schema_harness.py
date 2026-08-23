from docanalyzer.harness import load_records, run_eval
from docanalyzer.schema import FIELDS, ExtractedDocument


def test_fields_and_defaults():
    assert FIELDS == [
        "vendor_name",
        "document_number",
        "issue_date",
        "total_amount",
        "currency",
    ]
    doc = ExtractedDocument()
    assert all(getattr(doc, f) is None for f in FIELDS)


def test_extra_keys_are_ignored():
    doc = ExtractedDocument(vendor_name="Acme", unknown="x")
    assert doc.vendor_name == "Acme"
    assert not hasattr(doc, "unknown")


def test_gold_standard_file_loads():
    records = load_records("eval/gold_standard.jsonl")
    assert len(records) >= 5
    assert all("text" in r and "expected" in r for r in records)


def test_harness_scores_a_perfect_extractor():
    records = load_records("eval/gold_standard.jsonl")

    def perfect(text):
        # Look up the record by its text and echo the expected values back.
        for r in records:
            if r["text"] == text:
                return ExtractedDocument(**r["expected"])
        return ExtractedDocument()

    metrics, pairs = run_eval(records, perfect)
    assert len(pairs) == len(records)
    assert metrics["overall"]["f1"] == 1.0


def test_harness_penalizes_a_blank_extractor():
    records = load_records("eval/gold_standard.jsonl")
    metrics, _ = run_eval(records, lambda text: ExtractedDocument())
    assert metrics["overall"]["recall"] == 0.0
    assert metrics["overall"]["f1"] == 0.0
