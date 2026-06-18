import logging
from datetime import datetime

from app.domain.validation import ValidationResult

logger = logging.getLogger(__name__)


class ValidationStage:
    async def run(self, fields: list[dict]) -> list[ValidationResult]:
        results = []
        for field in fields:
            errors = []
            field_name = field.get("field_name", "")
            field_value = field.get("field_value", "")

            if field.get("confidence", 1.0) < 0.3:
                errors.append(f"Confianca muito baixa para {field_name}")

            if "data" in field_name.lower() or "vencimento" in field_name.lower():
                if not self._validate_date(field_value):
                    errors.append(f"Formato de data invalido: {field_value}")

            if "cpf" in field_name.lower() or "cnpj" in field_name.lower():
                if not self._validate_document(field_value):
                    errors.append(f"Documento invalido: {field_value}")

            if "valor" in field_name.lower():
                if not self._validate_amount(field_value):
                    errors.append(f"Formato de valor invalido: {field_value}")

            results.append(ValidationResult(
                field_name=field_name,
                passed=len(errors) == 0,
                errors=errors,
            ))

        return results

    def _validate_date(self, value: str) -> bool:
        try:
            datetime.strptime(value, "%d/%m/%Y")
            return True
        except (ValueError, TypeError):
            return False

    def _validate_document(self, value: str) -> bool:
        digits = "".join(filter(str.isdigit, value))
        if len(digits) == 11:
            return self._validate_cpf(digits)
        elif len(digits) == 14:
            return self._validate_cnpj(digits)
        return False

    def _validate_cpf(self, cpf: str) -> bool:
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        for i in range(9, 11):
            val = sum(int(cpf[j]) * (i + 1 - j) for j in range(i)) % 11
            val = 0 if val < 2 else 11 - val
            if int(cpf[i]) != val:
                return False
        return True

    def _validate_cnpj(self, cnpj: str) -> bool:
        if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
            return False
        for i in range(2):
            multipliers = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            if i == 1:
                multipliers = [6] + multipliers
            val = sum(int(cnpj[j]) * multipliers[j] for j in range(len(multipliers))) % 11
            val = 0 if val < 2 else 11 - val
            if int(cnpj[len(multipliers)]) != val:
                return False
        return True

    def _validate_amount(self, value: str) -> bool:
        import re
        return bool(re.match(r"^\d+(?:\.\d{3})*(?:,\d{2})?$", value.replace("R$", "").strip()))
