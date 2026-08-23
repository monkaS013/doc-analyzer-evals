"""The typed target of extraction.

Using a Pydantic model as the schema does double duty: it validates the model's
output, and its JSON schema is handed to the LLM as the tool contract, so the
model returns exactly these fields.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractedDocument(BaseModel):
    """Fields pulled from an invoice/receipt-like document."""

    vendor_name: str | None = Field(default=None, description="Company that issued the document")
    document_number: str | None = Field(default=None, description="Invoice or receipt number")
    issue_date: str | None = Field(default=None, description="Issue date, any format as written")
    total_amount: str | None = Field(default=None, description="Grand total, digits as written")
    currency: str | None = Field(default=None, description="Currency code or symbol")


# The fields the evaluation scores, in a stable order.
FIELDS = list(ExtractedDocument.model_fields.keys())
