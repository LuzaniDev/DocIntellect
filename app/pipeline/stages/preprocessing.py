import logging
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class PreprocessingResult:
    text: str | None = None
    image_paths: list[str] = field(default_factory=list)

    @property
    def has_images(self) -> bool:
        return len(self.image_paths) > 0

    @property
    def has_text(self) -> bool:
        return bool(self.text)


class PreprocessingStage:
    SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

    async def run(self, file_path: str) -> PreprocessingResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")
        ext = path.suffix.lower()

        if ext in self.SUPPORTED_IMAGE_EXTENSIONS:
            return PreprocessingResult(image_paths=[file_path])

        if ext == ".pdf":
            return self._process_pdf(file_path)

        raise ValueError(f"Formato de arquivo nao suportado: {ext}")

    def _process_pdf(self, pdf_path: str) -> PreprocessingResult:
        import fitz

        doc = fitz.open(pdf_path)

        raw_text = ""
        for page in doc:
            raw_text += page.get_text()

        raw_text = raw_text.strip()

        MIN_TEXT_LENGTH = 50
        if len(raw_text) >= MIN_TEXT_LENGTH:
            logger.info(f"PDF digital: {len(raw_text)} caracteres extraidos diretamente")
            doc.close()
            return PreprocessingResult(text=raw_text)

        logger.info(f"PDF escaneado ou com pouco texto ({len(raw_text)} chars). Renderizando para OCR...")
        image_paths = self._render_pdf_to_images(doc, pdf_path)
        doc.close()
        return PreprocessingResult(image_paths=image_paths)

    def _render_pdf_to_images(self, doc, pdf_path: str, dpi: int = 300) -> list[str]:
        output_dir = Path(pdf_path).parent / ".pages"
        output_dir.mkdir(parents=True, exist_ok=True)

        image_paths = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=dpi)
            image_path = str(output_dir / f"page_{page_num + 1}.png")
            pix.save(image_path)
            image_paths.append(image_path)

        logger.info(f"PDF renderizado: {len(image_paths)} pagina(s) para OCR")
        return image_paths
