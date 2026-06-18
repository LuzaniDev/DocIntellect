import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.schemas.document import DocumentResponse, ExtractedFieldResponse, ExtractionResponse, StructuredBlockResponse, StructuredTableResponse
from app.core.config import settings
from app.domain.document import DocumentStatus
from app.pipeline.orchestrator import PipelineOrchestrator
from app.storage import LocalStorage

router = APIRouter()
orchestrator = PipelineOrchestrator()
storage = LocalStorage(settings.storage_local_path)

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/tiff",
    "image/bmp",
}

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

_doc_store: dict[str, str] = {}


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo nao suportado: {file.content_type}. Permitidos: PDF, PNG, JPEG, TIFF, BMP",
        )

    content = await file.read()
    doc_id = str(uuid.uuid4())
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        extension = ".png"
    storage_name = f"{doc_id}{extension}"

    saved_path = await storage.save(storage_name, content)
    _doc_store[doc_id] = str(Path(settings.storage_local_path) / storage_name)

    return DocumentResponse(
        id=doc_id,
        filename=file.filename,
        status=DocumentStatus.UPLOADED.value,
        storage_path=saved_path,
        file_size=len(content),
        mime_type=file.content_type or "application/octet-stream",
    )


@router.post("/process/{document_id}", response_model=ExtractionResponse)
async def process_document(document_id: str):
    file_path = _doc_store.get(document_id)
    if not file_path or not Path(file_path).exists():
        base = Path(settings.storage_local_path)
        for ext in ALLOWED_EXTENSIONS:
            candidate = base / f"{document_id}{ext}"
            if candidate.exists():
                file_path = str(candidate)
                break
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {document_id} nao encontrado",
            )

    result = await orchestrator.process_document(file_path)

    return ExtractionResponse(
        document_id=document_id,
        document_type=result.document_type,
        classification_confidence=result.classification_confidence,
        fields=[ExtractedFieldResponse(**f.model_dump()) for f in result.fields],
        raw_text=result.raw_text,
        overall_confidence=result.overall_confidence,
        needs_review=result.needs_review,
        structured_blocks=[StructuredBlockResponse(**b.model_dump()) for b in result.structured_blocks],
        tables=[StructuredTableResponse(**t.model_dump()) for t in result.tables],
        formatted_markdown=result.formatted_markdown,
    )
