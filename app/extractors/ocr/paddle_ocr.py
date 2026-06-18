import logging

from app.extractors.ocr import OCREngine

logger = logging.getLogger(__name__)


class PaddleOCREngine(OCREngine):
    def __init__(self):
        self._ocr = None

    def _lazy_init(self):
        if self._ocr is None:
            try:
                from paddleocr import PaddleOCR
                self._ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            except ImportError:
                raise ImportError("PaddleOCR nao esta instalado. Execute: pip install docintellect-rpa[ocr]")

    async def extract_text(self, image_path: str, lang: str = "por") -> str:
        self._lazy_init()
        result = self._ocr.ocr(image_path, cls=True)
        text_parts = []
        for page in result:
            if page is None:
                continue
            for line in page:
                text_parts.append(line[1][0])
        return "\n".join(text_parts)

    async def extract_text_with_confidence(self, image_path: str, lang: str = "por") -> list[dict]:
        self._lazy_init()
        result = self._ocr.ocr(image_path, cls=True)
        entries = []
        for page in result:
            if page is None:
                continue
            for line in page:
                bbox, (text, confidence) = line
                entries.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox,
                })
        return entries
