from pydantic import BaseModel


class ValidationRule(BaseModel):
    field_name: str
    rule_type: str
    pattern: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    required: bool = False
    error_message: str = ""


class ValidationResult(BaseModel):
    field_name: str
    passed: bool
    errors: list[str] = []
