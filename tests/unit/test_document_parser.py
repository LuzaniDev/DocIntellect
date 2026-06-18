import pytest

from app.extractors.document_parser import BlockType, DocumentParser


class TestDocumentParser:
    def test_parse_empty(self):
        doc = DocumentParser.parse("")
        assert doc.blocks == []
        assert doc.tables == []
        assert doc.fields == {}

    def test_parse_headers(self):
        text = """
NOTA FISCAL ELETRONICA

algum conteudo qualquer

RELATORIO FINAL
"""
        doc = DocumentParser.parse(text)
        headers = [b for b in doc.blocks if b.type == BlockType.HEADER]
        assert len(headers) >= 2

    def test_parse_key_value(self):
        text = """
Nome: Joao Silva
CPF: 123.456.789-00
Email: joao@teste.com
"""
        doc = DocumentParser.parse(text)
        kv_blocks = [b for b in doc.blocks if b.type == BlockType.KEY_VALUE]
        assert len(kv_blocks) >= 1
        assert "nome" in doc.fields
        assert "cpf" in doc.fields

    def test_parse_table_with_pipes(self):
        text = """
Item | Qtd | Valor
Caneta | 10 | 5,00
Lapis | 5 | 2,50
"""
        doc = DocumentParser.parse(text)
        tables = doc.tables
        assert len(tables) >= 1
        assert len(tables[0]) >= 2

    def test_parse_list(self):
        text = """
- Item um
- Item dois
- Item tres
"""
        doc = DocumentParser.parse(text)
        list_blocks = [b for b in doc.blocks if b.type == BlockType.LIST]
        assert len(list_blocks) >= 1

    def test_to_markdown(self):
        text = """
# Titulo
Nome: Joao
Valor: R$ 100
"""
        doc = DocumentParser.parse(text)
        md = DocumentParser.to_markdown(doc)
        assert "Titulo" in md
        assert "Joao" in md
        assert "R$ 100" in md

    def test_header_patterns(self):
        text = "1. PRIMEIRA CLAUSULA"
        doc = DocumentParser.parse(text)
        assert any(b.type == BlockType.HEADER for b in doc.blocks)
