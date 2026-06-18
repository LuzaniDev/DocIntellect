import re
from typing import Optional

from app.domain.document import DocumentType


class EntityExtractor:
    def extract(self, text: str, document_type: DocumentType) -> list[dict]:
        extractors = {
            DocumentType.INVOICE: self._extract_invoice,
            DocumentType.CONTRACT: self._extract_contract,
            DocumentType.MEDICAL_REPORT: self._extract_medical,
            DocumentType.IDENTITY: self._extract_identity,
            DocumentType.RECEIPT: self._extract_receipt,
            DocumentType.PAYMENT_SLIP: self._extract_payment_slip,
        }

        extractor = extractors.get(document_type, self._extract_generic)
        return extractor(text)

    def _extract_invoice(self, text: str) -> list[dict]:
        fields = []
        cnpj = self._find_pattern(text, r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")
        if cnpj:
            fields.append({"field_name": "cnpj_emitente", "field_value": cnpj, "confidence": 0.9})

        valor = self._find_pattern(text, r"(?:R\$|Valor\s*Total[:\s]*)\s*([\d.,]+)")
        if valor:
            fields.append({"field_name": "valor_total", "field_value": valor, "confidence": 0.85})

        data = self._find_pattern(text, r"\d{2}/\d{2}/\d{4}")
        if data:
            fields.append({"field_name": "data_emissao", "field_value": data, "confidence": 0.8})

        numero = self._find_pattern(text, r"(?:N[°º]|Numero|Número)[.:\s]*(\d+)")
        if numero:
            fields.append({"field_name": "numero_nota", "field_value": numero, "confidence": 0.85})

        return fields

    def _extract_contract(self, text: str) -> list[dict]:
        fields = []
        partes = re.findall(r"(?:contratante|contratada)[:\s]+(.+?)(?:\n|$)", text, re.IGNORECASE)
        if partes:
            fields.append({"field_name": "partes", "field_value": "; ".join(partes), "confidence": 0.7})

        valor = self._find_pattern(text, r"(?:R\$|valor\s*)[:\s]*([\d.,]+)")
        if valor:
            fields.append({"field_name": "valor_contrato", "field_value": valor, "confidence": 0.8})

        dias = re.findall(r"\d+\s*dias?", text, re.IGNORECASE)
        if dias:
            fields.append({"field_name": "prazo", "field_value": dias[0], "confidence": 0.7})

        return fields

    def _extract_medical(self, text: str) -> list[dict]:
        fields = []
        paciente = self._find_pattern(text, r"(?:paciente|nome)[:\s]+(.+?)(?:\n|$)", re.IGNORECASE)
        if paciente:
            fields.append({"field_name": "paciente", "field_value": paciente, "confidence": 0.8})

        cid = self._find_pattern(text, r"[A-Z]\d{2}\.\d")
        if cid:
            fields.append({"field_name": "cid", "field_value": cid, "confidence": 0.9})

        data = self._find_pattern(text, r"\d{2}/\d{2}/\d{4}")
        if data:
            fields.append({"field_name": "data_exame", "field_value": data, "confidence": 0.8})

        return fields

    def _extract_identity(self, text: str) -> list[dict]:
        fields = []
        cpf = self._find_pattern(text, r"\d{3}\.\d{3}\.\d{3}-\d{2}")
        if cpf:
            fields.append({"field_name": "cpf", "field_value": cpf, "confidence": 0.9})

        rg = self._find_pattern(text, r"\d{1,2}\.\d{3}\.\d{3}[-]?\d{1}")
        if rg:
            fields.append({"field_name": "rg", "field_value": rg, "confidence": 0.85})

        nome = self._find_pattern(text, r"(?:nome)[:\s]+(.+?)(?:\n|$)", re.IGNORECASE)
        if nome:
            fields.append({"field_name": "nome", "field_value": nome, "confidence": 0.8})

        return fields

    def _extract_receipt(self, text: str) -> list[dict]:
        fields = []
        valor = self._find_pattern(text, r"(?:R\$|valor)[:\s]*([\d.,]+)")
        if valor:
            fields.append({"field_name": "valor", "field_value": valor, "confidence": 0.85})

        data = self._find_pattern(text, r"\d{2}/\d{2}/\d{4}")
        if data:
            fields.append({"field_name": "data", "field_value": data, "confidence": 0.8})

        return fields

    def _extract_payment_slip(self, text: str) -> list[dict]:
        fields = []
        codigo = self._find_pattern(text, r"(?:\d{4}\s?){5}\d")
        if codigo:
            fields.append({"field_name": "codigo_barras", "field_value": codigo, "confidence": 0.9})

        valor = self._find_pattern(text, r"(?:R\$|valor)[:\s]*([\d.,]+)")
        if valor:
            fields.append({"field_name": "valor", "field_value": valor, "confidence": 0.85})

        vencimento = self._find_pattern(text, r"(?:vencimento|vencto)[:\s]+(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
        if vencimento:
            fields.append({"field_name": "vencimento", "field_value": vencimento, "confidence": 0.85})

        return fields

    def _extract_generic(self, text: str) -> list[dict]:
        fields = []
        data = self._find_pattern(text, r"\d{2}/\d{2}/\d{4}")
        if data:
            fields.append({"field_name": "data", "field_value": data, "confidence": 0.5})

        cnpj_cpf = self._find_pattern(text, r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2}")
        if cnpj_cpf:
            fields.append({"field_name": "documento", "field_value": cnpj_cpf, "confidence": 0.6})

        valor = self._find_pattern(text, r"R\$\s*[\d.,]+")
        if valor:
            fields.append({"field_name": "valor", "field_value": valor, "confidence": 0.5})

        return fields

    def _find_pattern(self, text: str, pattern: str, flags: int = 0) -> Optional[str]:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1) if match.lastindex else match.group(0)
        return None
