from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    storage_path: str
    file_size: int
    mime_type: str


class ExtractedFieldResponse(BaseModel):
    model_config = {"from_attributes": True}
    field_name: str
    field_value: str | None = None
    confidence: float = 0.0
    extraction_method: str = "ocr"


class StructuredBlockResponse(BaseModel):
    type: str = "paragraph"
    content: str = ""
    metadata: dict = Field(default_factory=dict)


class StructuredTableResponse(BaseModel):
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)


class ExtractionResponse(BaseModel):
    document_id: str
    document_type: str | None = None
    classification_confidence: float = 0.0
    fields: list[ExtractedFieldResponse] = Field(default_factory=list)
    raw_text: str | None = None
    overall_confidence: float = 0.0
    needs_review: bool = False
    structured_blocks: list[StructuredBlockResponse] = Field(default_factory=list)
    tables: list[StructuredTableResponse] = Field(default_factory=list)
    formatted_markdown: str = ""
