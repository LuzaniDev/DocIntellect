import logging

from app.core.config import settings
from app.extractors.ocr import OCREngine

logger = logging.getLogger(__name__)


class _DummyEngine(OCREngine):
    """Fallback when no OCR engine is available."""
    async def extract_text(self, image_path: str, lang: str = "por") -> str:
        return ""

    async def extract_text_with_confidence(self, image_path: str, lang: str = "por") -> list[dict]:
        return [{"text": "", "confidence": 0.0, "bbox": [0, 0, 0, 0]}]


def create_ocr_engine() -> OCREngine:
    engine_name = settings.ocr_engine.lower()

    attempts = [engine_name]
    if engine_name == "paddle":
        attempts.append("tesseract")
    elif engine_name == "tesseract":
        attempts.append("paddle")

    for name in attempts:
        try:
            if name == "paddle":
                from app.extractors.ocr.paddle_ocr import PaddleOCREngine
                return PaddleOCREngine()
            elif name == "tesseract":
                from app.extractors.ocr.tesseract import TesseractEngine
                return TesseractEngine()
        except ImportError as e:
            logger.warning("Engine '%s' nao disponivel: %s", name, e)
            continue
        except Exception as e:
            logger.warning("Falha ao inicializar engine '%s': %s", name, e)
            continue

    logger.warning("Nenhum engine OCR disponivel, usando engine dummy")
    return _DummyEngine()
