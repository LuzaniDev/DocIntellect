import logging

from app.domain.document import DocumentType
from app.extractors.nlp.classifiers.document_classifier import DocumentClassifier

logger = logging.getLogger(__name__)


class ClassificationStage:
    def __init__(self):
        self.classifier = DocumentClassifier()

    async def run(self, text: str) -> tuple[DocumentType, float]:
        doc_type, confidence = self.classifier.classify(text)
        logger.info(f"Documento classificado como: {doc_type.value} (confianca: {confidence:.2f})")
        return doc_type, confidence
