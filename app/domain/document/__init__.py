from enum import Enum


class DocumentType(str, Enum):
    INVOICE = "nota_fiscal"
    CONTRACT = "contrato"
    MEDICAL_REPORT = "laudo_medico"
    IDENTITY = "documento_identidade"
    RECEIPT = "recibo"
    PAYMENT_SLIP = "boleto"
    BANK_STATEMENT = "extrato_bancario"
    OTHER = "outro"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    CLASSIFIED = "classified"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    FAILED = "failed"
    REVIEW_NEEDED = "review_needed"
    COMPLETED = "completed"


__all__ = ["DocumentType", "DocumentStatus"]
