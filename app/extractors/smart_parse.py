"""Parser inteligente via LLM para estruturar documentos complexos."""

import json
import logging

from app.core.config import settings
from app.extractors.document_parser import Block, BlockType, DocumentParser, ParsedDocument

logger = logging.getLogger(__name__)


class SmartParser:
    def __init__(self):
        self._client = None
        self.heuristic = DocumentParser()

    def _lazy_init(self):
        if self._client is not None or not settings.llm_api_key:
            return
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.llm_api_key)
        except Exception as e:
            logger.warning(f"Erro ao iniciar LLM: {e}")

    @property
    def llm_disponivel(self) -> bool:
        return bool(settings.llm_api_key)

    async def parse(self, text: str, document_type: str = "") -> ParsedDocument:
        doc = self.heuristic.parse(text)

        if self.llm_disponivel:
            self._lazy_init()
            if self._client:
                try:
                    llm_doc = await self._parse_via_llm(text, document_type)
                    if llm_doc:
                        return llm_doc
                except Exception as e:
                    logger.warning(f"LLM parse falhou, usando heuristica: {e}")

        return doc

    async def _parse_via_llm(self, text: str, document_type: str) -> ParsedDocument | None:
        prompt = f"""Analise o documento abaixo e extraia APENAS um JSON com esta estrutura exata:
{{
  "tables": [["col1", "col2"], ["val1", "val2"]],
  "fields": {{"nome_do_campo": "valor"}},
  "sections": ["nome da secao 1", "nome da secao 2"],
  "summary": "breve resumo do documento"
}}

Tipo do documento: {document_type or "desconhecido"}

Texto:
---
{text[:6000]}
---

Responda APENAS com o JSON puro, sem markdown."""

        response = await self._client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.05,
            max_tokens=1500,
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)

        doc = ParsedDocument(raw_text=text)
        doc.fields = data.get("fields", {})

        for section in data.get("sections", []):
            doc.blocks.append(Block(type=BlockType.HEADER, content=section))

        for key, value in doc.fields.items():
            doc.blocks.append(
                Block(type=BlockType.KEY_VALUE, content=f"{key}: {value}", metadata={"key": key, "value": value})
            )

        for table_data in data.get("tables", []):
            table_text = "\n".join("\t".join(row) for row in table_data)
            doc.blocks.append(Block(type=BlockType.TABLE, content=table_text))
            doc.tables.append(table_data)

        if data.get("summary"):
            doc.blocks.insert(0, Block(type=BlockType.PARAGRAPH, content=f"**Resumo:** {data['summary']}"))

        if not doc.blocks:
            doc.blocks = self.heuristic.parse(text).blocks

        return doc
