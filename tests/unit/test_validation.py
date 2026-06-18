import pytest

from app.pipeline.stages.validation_stage import ValidationStage


class TestValidationStage:
    @pytest.fixture
    def validator(self):
        return ValidationStage()

    @pytest.mark.asyncio
    async def test_valid_cpf(self, validator):
        assert validator._validate_cpf("52998224725")

    @pytest.mark.asyncio
    async def test_invalid_cpf(self, validator):
        assert not validator._validate_cpf("11111111111")

    @pytest.mark.asyncio
    async def test_valid_cnpj(self, validator):
        assert validator._validate_cnpj("11444777000161")

    @pytest.mark.asyncio
    async def test_invalid_cnpj(self, validator):
        assert not validator._validate_cnpj("00000000000000")

    @pytest.mark.asyncio
    async def test_valid_date(self, validator):
        assert validator._validate_date("15/03/2025")

    @pytest.mark.asyncio
    async def test_invalid_date(self, validator):
        assert not validator._validate_date("32/13/2025")
