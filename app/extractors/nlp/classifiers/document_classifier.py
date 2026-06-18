import re
from typing import Optional

from app.domain.document import DocumentType


class DocumentClassifier:
    KEYWORD_MAP: dict[DocumentType, list[str]] = {
        DocumentType.INVOICE: [
            "nota fiscal", "nf-e", "nfe", "danfe", "cnpj", "inscricao estadual",
            "icms", "nfse", "nota fiscal de servico", "fatura",
        ],
        DocumentType.CONTRACT: [
            "contrato", "clausula", "firmado", "contratante", "contratada",
            "vigencia", "partes", "assinatura",
        ],
        DocumentType.MEDICAL_REPORT: [
            "laudo", "paciente", "diagnostico", "exame", "medico",
            "cid", "prescricao", "receita medica", "atestado",
        ],
        DocumentType.IDENTITY: [
            "rg", "cpf", "identidade", "registro geral", "certidao",
            "passaporte", "carteira",
        ],
        DocumentType.RECEIPT: [
            "recibo", "recebemos", "pagamento", "valor", "quitacao",
        ],
        DocumentType.PAYMENT_SLIP: [
            "boleto", "codigo de barras", "linha digitavel", "vencimento",
            "beneficiario", "pagador",
        ],
        DocumentType.BANK_STATEMENT: [
            "extrato", "saldo", "credito", "debito", "agencia", "conta corrente",
        ],
    }

    def classify(self, text: str) -> tuple[DocumentType, float]:
        text_lower = text.lower()
        scores: dict[DocumentType, float] = {}

        for doc_type, keywords in self.KEYWORD_MAP.items():
            score = 0.0
            for keyword in keywords:
                matches = len(re.findall(re.escape(keyword), text_lower))
                score += matches * (1.0 / len(keywords))
            scores[doc_type] = min(score, 1.0)

        best_type: DocumentType = DocumentType.OTHER
        best_score: float = 0.0

        for doc_type, score in scores.items():
            if score > best_score:
                best_score = score
                best_type = doc_type

        return best_type, best_score
