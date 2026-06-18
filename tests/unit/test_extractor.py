import pytest

from app.domain.document import DocumentType
from app.extractors.nlp.entity_extractor import EntityExtractor


class TestEntityExtractor:
    @pytest.fixture
    def extractor(self):
        return EntityExtractor()

    def test_extract_invoice(self, extractor):
        text = """
        NOTA FISCAL ELETRONICA
        CNPJ: 12.345.678/0001-90
        Valor Total: R$ 1.500,00
        Data: 15/03/2025
        N°: 123456
        """
        fields = extractor.extract(text, DocumentType.INVOICE)
        names = [f["field_name"] for f in fields]
        assert "cnpj_emitente" in names
        assert "valor_total" in names
        assert "data_emissao" in names
        assert "numero_nota" in names

    def test_extract_contract(self, extractor):
        text = """
        CONTRATO DE PRESTACAO DE SERVICOS
        Contratante: Empresa X Ltda
        Contratada: Empresa Y S.A.
        Valor: R$ 50.000,00
        Prazo: 30 dias
        """
        fields = extractor.extract(text, DocumentType.CONTRACT)
        names = [f["field_name"] for f in fields]
        assert "partes" in names
        assert "valor_contrato" in names
        assert "prazo" in names

    def test_extract_medical(self, extractor):
        text = """
        LAUDO MEDICO
        Paciente: Joao Silva
        CID: I10.0
        Data do Exame: 10/01/2025
        """
        fields = extractor.extract(text, DocumentType.MEDICAL_REPORT)
        names = [f["field_name"] for f in fields]
        assert "paciente" in names
        assert "cid" in names
        assert "data_exame" in names

    def test_extract_identity(self, extractor):
        text = """
        RG: 12.345.678-9
        CPF: 123.456.789-00
        Nome: Maria Oliveira
        """
        fields = extractor.extract(text, DocumentType.IDENTITY)
        names = [f["field_name"] for f in fields]
        assert "cpf" in names
        assert "rg" in names
        assert "nome" in names

    def test_extract_receipt(self, extractor):
        text = "Recebo de Fulano a importancia de R$ 200,00. Data: 05/12/2025"
        fields = extractor.extract(text, DocumentType.RECEIPT)
        names = [f["field_name"] for f in fields]
        assert "valor" in names
        assert "data" in names

    def test_extract_generic_unknown(self, extractor):
        text = "Texto aleatorio sem dados especificos"
        fields = extractor.extract(text, DocumentType.OTHER)
        assert fields == []

    def test_extract_invoice_confidence_values(self, extractor):
        text = """
        NOTA FISCAL
        CNPJ: 12.345.678/0001-90
        """
        fields = extractor.extract(text, DocumentType.INVOICE)
        for f in fields:
            assert 0 < f["confidence"] <= 1.0
            assert "field_name" in f
            assert "field_value" in f
