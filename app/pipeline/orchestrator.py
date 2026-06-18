import logging

from app.domain.document import DocumentStatus
from app.domain.extraction import ExtractedField, ExtractionResult, StructuredBlock, StructuredTable
from app.extractors.document_parser import BlockType, DocumentParser
from app.extractors.smart_parse import SmartParser
from app.pipeline.stages.preprocessing import PreprocessingStage
from app.pipeline.stages.ocr_stage import OCRStage
from app.pipeline.stages.classification_stage import ClassificationStage
from app.pipeline.stages.extraction_stage import ExtractionStage
from app.pipeline.stages.validation_stage import ValidationStage

logger = logging.getLogger(__name__)

TYPE_MAP = {
    BlockType.HEADER: "header",
    BlockType.KEY_VALUE: "key_value",
    BlockType.TABLE: "table",
    BlockType.LIST: "list",
    BlockType.PARAGRAPH: "paragraph",
}


class PipelineOrchestrator:
    def __init__(self):
        self.preprocessing = PreprocessingStage()
        self.ocr = OCRStage()
        self.classification = ClassificationStage()
        self.extraction = ExtractionStage()
        self.validation = ValidationStage()
        self.smart_parser = SmartParser()

    async def process_document(self, file_path: str) -> ExtractionResult:
        logger.info(f"Iniciando pipeline para: {file_path}")

        pre_result = await self.preprocessing.run(file_path)

        if pre_result.has_text:
            raw_text = pre_result.text
            logger.info(f"Texto extraido diretamente do PDF: {len(raw_text)} chars")
        elif pre_result.has_images:
            raw_text = await self.ocr.run(pre_result.image_paths)
            logger.info(f"OCR concluido: {len(raw_text)} chars extraidos de {len(pre_result.image_paths)} imagem(ns)")
        else:
            raise RuntimeError("Preprocessamento nao retornou texto nem imagens")

        doc_type, class_confidence = await self.classification.run(raw_text)
        logger.info(f"Classificacao: {doc_type.value} ({class_confidence:.2f})")

        extracted_fields = await self.extraction.run(raw_text, doc_type)
        logger.info(f"Extracao: {len(extracted_fields)} campos encontrados")

        validation_results = await self.validation.run(extracted_fields)
        logger.info(f"Validacao: {sum(1 for v in validation_results if v.passed)}/{len(validation_results)} campos validos")

        fields = []
        needs_review = False
        for field_data, validation in zip(extracted_fields, validation_results):
            if not validation.passed:
                needs_review = True
            fields.append(ExtractedField(
                field_name=field_data.get("field_name", ""),
                field_value=field_data.get("field_value"),
                confidence=field_data.get("confidence", 0.0),
                extraction_method=field_data.get("extraction_method", "ocr"),
            ))

        overall_conf = sum(f.confidence for f in fields) / len(fields) if fields else 0.0

        parsed = await self.smart_parser.parse(raw_text, doc_type.value)

        structured_blocks = [
            StructuredBlock(type=TYPE_MAP.get(b.type, "paragraph"), content=b.content, metadata=b.metadata)
            for b in parsed.blocks
        ]

        tables = [
            StructuredTable(headers=t[0] if t else [], rows=t[1:] if len(t) > 1 else [])
            for t in parsed.tables
        ]

        formatted_md = self.smart_parser.heuristic.to_markdown(parsed)

        return ExtractionResult(
            document_type=doc_type.value,
            classification_confidence=class_confidence,
            fields=fields,
            raw_text=raw_text[:5000],
            overall_confidence=overall_conf,
            needs_review=needs_review or overall_conf < 0.6,
            structured_blocks=structured_blocks,
            tables=tables,
            formatted_markdown=formatted_md,
        )
