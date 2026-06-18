import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMExtractor:
    def __init__(self):
        self._client = None

    def _lazy_init(self):
        if self._client is not None:
            return

        provider = settings.llm_provider.lower()
        if provider == "openai":
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.llm_api_key)
        else:
            raise ValueError(f"Provedor LLM nao suportado: {provider}")

    async def extract_fields(self, text: str, document_type: str) -> list[dict]:
        if not settings.llm_api_key:
            logger.warning("LLM_API_KEY nao configurada. Pulando extracao via LLM.")
            return []

        self._lazy_init()

        prompt = f"""
        Extraia os campos estruturados do documento abaixo.
        Tipo do documento: {document_type}

        Texto extraido:
        ---
        {text[:4000]}
        ---

        Responda APENAS com um JSON array de objetos, cada um com:
        - "field_name": nome do campo
        - "field_value": valor extraido
        - "confidence": confianca (0.0 a 1.0)

        Exemplo:
        [{{"field_name": "cnpj", "field_value": "12.345.678/0001-90", "confidence": 0.95}}]
        """

        try:
            response = await self._client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.llm_temperature,
                max_tokens=1000,
            )

            content = response.choices[0].message.content.strip()
            content = content.replace("```json", "").replace("```", "").strip()
            fields = json.loads(content)
            return fields if isinstance(fields, list) else []
        except Exception as e:
            logger.error(f"Erro ao extrair via LLM: {e}")
            return []
