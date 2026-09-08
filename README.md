# doc-analyzer-evals: extraction with a gold-standard eval

*[Português](README.pt-BR.md)*

Structured field extraction from documents like invoices and receipts, with a measurable evaluation attached. "How good is the extraction?" gets a numeric answer here, which is the part that usually gets skipped.

## What it does

Given a document's text, it returns a typed object holding vendor, document number, issue date, total and currency. The eval harness then scores those predictions against a gold-standard set, reporting per-field precision, recall, and F1. A threshold gate turns the eval into something a build can fail on.

## Why it's built this way

- **Typed extraction via tool use.** The target is a Pydantic model; its JSON schema is handed to the model as the tool contract, so the reply is a structured object, not prose to parse. Validation is the schema's job.
- **A real evaluation.** A gold-standard set of documents with expected fields drives per-field and micro-averaged precision/recall/F1, plus exact-match accuracy. Missing extractions show up as recall loss; spurious ones as precision loss.
- **Fair comparison through normalization.** Gold and prediction pass through the same normalizer before matching, so `R$ 1.234,56` and `1234.56`, or `12/03/2026` and `2026-03-12`, count as equal. Formatting differences cost nothing in the score; wrong data still does.
- **A gate, like in production.** `run_eval.py` exits non-zero when overall F1 is below the threshold, the same discipline you'd use to gate a release on retrieval quality.
- **Offline-testable.** The extractor is injected into the harness, so metrics, normalization and the rest of the scoring loop run under test with a fake extractor and no API key.

## Run the eval

```bash
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY
python eval/run_eval.py --min-f1 0.8
```

Output is a per-field table, the micro-averaged F1, exact-match accuracy, and a PASS/FAIL line (with a matching exit code).

## Tests

Metrics, normalization, the schema, and the harness (with a fake extractor) run with no API key:

```bash
python -m pytest -q
```

## Structure

```
docanalyzer/
├── schema.py       # ExtractedDocument (Pydantic): extraction target + tool contract
├── extractor.py    # Claude tool-use call (lazy import)
├── normalize.py    # money / date / text normalization for fair comparison
├── metrics.py      # precision / recall / F1 + the gate
└── harness.py      # ties gold set + extractor + metrics
eval/
├── gold_standard.jsonl   # fictional documents + expected fields
└── run_eval.py           # CLI: report + threshold gate
```

## Stack

Python · Anthropic (Claude, tool use) · Pydantic · pytest.

> The gold-standard documents are fictional.
