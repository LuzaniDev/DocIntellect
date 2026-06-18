import logging

from app.extractors.ocr.factory import create_ocr_engine

logger = logging.getLogger(__name__)


class OCRStage:
    def __init__(self):
        self.engine = create_ocr_engine()

    async def run(self, image_paths: list[str], lang: str = "por") -> str:
        if not image_paths:
            return ""

        all_text = []
        for img_path in image_paths:
            text = await self.engine.extract_text(img_path, lang=lang)
            all_text.append(text)
            logger.debug(f"OCR concluido: {img_path} ({len(text)} chars)")

        return "\n\n".join(all_text)

    async def run_with_confidence(self, image_paths: list[str], lang: str = "por") -> list[dict]:
        if not image_paths:
            return []

        all_entries = []
        for img_path in image_paths:
            entries = await self.engine.extract_text_with_confidence(img_path, lang=lang)
            all_entries.extend(entries)
        return all_entries
