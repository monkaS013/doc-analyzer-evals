"""LLM extraction boundary.

The Pydantic model's JSON schema is passed to the model as a tool contract, so
the reply is a structured object, not prose to parse. ``anthropic`` is imported
lazily, so the package and its tests import without the SDK or an API key.
"""

from __future__ import annotations

import os

from .schema import ExtractedDocument

DEFAULT_MODEL = os.environ.get("DOCANALYZER_MODEL", "claude-haiku-4-5-20251001")

_SYSTEM = (
    "You extract structured fields from a document. Use only what is present in "
    "the text. If a field is not in the document, leave it null. Never guess."
)


def extract(text: str, *, model: str | None = None) -> ExtractedDocument:
    """Extract the typed fields from a document's text."""
    import anthropic  # lazy: keeps the package importable without the SDK

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    tool = {
        "name": "record_document",
        "description": "Record the fields extracted from the document.",
        "input_schema": ExtractedDocument.model_json_schema(),
    }
    message = client.messages.create(
        model=model or DEFAULT_MODEL,
        max_tokens=1024,
        system=_SYSTEM,
        tools=[tool],
        tool_choice={"type": "tool", "name": "record_document"},
        messages=[{"role": "user", "content": f"Document:\n\n{text}"}],
    )
    for block in message.content:
        if block.type == "tool_use" and block.name == "record_document":
            return ExtractedDocument(**block.input)
    return ExtractedDocument()
