import pytest

from app.domain.document import DocumentType
from app.extractors.nlp.classifiers.document_classifier import DocumentClassifier


class TestDocumentClassifier:
    @pytest.fixture
    def classifier(self):
        return DocumentClassifier()

    def test_classify_invoice(self, classifier):
        text = """
        NOTA FISCAL ELETRONICA
        CNPJ: 12.345.678/0001-90
        Inscricao Estadual: 123456789
        ICMS: 18%
        Valor Total: R$ 1.500,00
        """
        doc_type, confidence = classifier.classify(text)
        assert doc_type == DocumentType.INVOICE
        assert confidence > 0.3

    def test_classify_contract(self, classifier):
        text = """
        CONTRATO DE PRESTACAO DE SERVICOS
        Contratante: Empresa X
        Contratada: Empresa Y
        Vigencia: 12 meses
        """
        doc_type, confidence = classifier.classify(text)
        assert doc_type == DocumentType.CONTRACT
        assert confidence > 0.3

    def test_classify_medical(self, classifier):
        text = """
        LAUDO MEDICO
        Paciente: Joao Silva
        Diagnostico: Hipertensao
        CID: I10
        """
        doc_type, confidence = classifier.classify(text)
        assert doc_type == DocumentType.MEDICAL_REPORT

    def test_classify_unknown(self, classifier):
        text = "Texto generico sem palavras-chave de nenhum tipo de documento"
        doc_type, confidence = classifier.classify(text)
        assert doc_type == DocumentType.OTHER
        assert confidence == 0.0
