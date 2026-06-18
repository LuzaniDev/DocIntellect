import logging

from app.domain.document import DocumentType
from app.extractors.nlp.entity_extractor import EntityExtractor
from app.extractors.llm_fallback.extractor import LLMExtractor
from app.core.config import settings

logger = logging.getLogger(__name__)


class ExtractionStage:
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.llm_extractor = LLMExtractor()

    async def run(self, text: str, document_type: DocumentType) -> list[dict]:
        fields = self.entity_extractor.extract(text, document_type)

        if fields:
            avg_confidence = sum(f.get("confidence", 0) for f in fields) / len(fields)
        else:
            avg_confidence = 0.0

        if avg_confidence < settings.pipeline_confidence_threshold:
            logger.info("Confianca baixa, usando fallback LLM...")
            llm_fields = await self.llm_extractor.extract_fields(text, document_type.value)
            if llm_fields:
                for f in llm_fields:
                    f["extraction_method"] = "llm"
                fields = llm_fields

        logger.info(f"Extraidos {len(fields)} campos do documento")
        return fields
