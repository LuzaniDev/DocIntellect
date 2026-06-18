from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    field_name: str
    field_value: str | None = None
    confidence: float = 0.0
    extraction_method: str = "ocr"
    validated: bool = False
    corrected_value: str | None = None


class StructuredBlock(BaseModel):
    type: str = "paragraph"
    content: str = ""
    metadata: dict = Field(default_factory=dict)


class StructuredTable(BaseModel):
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    document_id: str = ""
    document_type: str | None = None
    classification_confidence: float = 0.0
    fields: list[ExtractedField] = Field(default_factory=list)
    raw_text: str | None = None
    overall_confidence: float = 0.0
    needs_review: bool = False
    structured_blocks: list[StructuredBlock] = Field(default_factory=list)
    tables: list[StructuredTable] = Field(default_factory=list)
    formatted_markdown: str = ""
