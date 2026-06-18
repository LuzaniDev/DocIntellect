from abc import ABC, abstractmethod


class OCREngine(ABC):
    @abstractmethod
    async def extract_text(self, image_path: str, lang: str = "por") -> str:
        ...

    @abstractmethod
    async def extract_text_with_confidence(self, image_path: str, lang: str = "por") -> list[dict]:
        ...
