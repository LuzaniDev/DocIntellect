import logging
import os

import pytesseract
from PIL import Image

from app.core.config import settings
from app.extractors.ocr import OCREngine

logger = logging.getLogger(__name__)


class TesseractEngine(OCREngine):
    def __init__(self):
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
        if settings.tessdata_prefix and os.path.isdir(settings.tessdata_prefix):
            os.environ["TESSDATA_PREFIX"] = settings.tessdata_prefix

    async def extract_text(self, image_path: str, lang: str = "por") -> str:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()

    async def extract_text_with_confidence(self, image_path: str, lang: str = "por") -> list[dict]:
        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
        entries = []
        for i in range(len(data["text"])):
            if data["text"][i].strip():
                entries.append({
                    "text": data["text"][i],
                    "confidence": int(data["conf"][i]) / 100.0,
                    "bbox": {
                        "x": data["left"][i],
                        "y": data["top"][i],
                        "w": data["width"][i],
                        "h": data["height"][i],
                    },
                })
        return entries
