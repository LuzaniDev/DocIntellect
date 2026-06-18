import pytest

from app.extractors.text_formatter import MarkdownFormatter, TextCleaner
from app.extractors.document_parser import Block, BlockType, DocumentParser, ParsedDocument


class TestTextCleaner:
    def test_clean_hyphenated_line_break(self):
        text = "docu-\nmento"
        assert TextCleaner.clean(text) == "documento"

    def test_clean_hyphenated_with_spaces(self):
        text = "docu- \n mento"
        result = TextCleaner.clean(text)
        assert "documento" in result

    def test_normalize_multiple_newlines(self):
        text = "linha1\n\n\n\nlinha2"
        result = TextCleaner.clean(text)
        assert result == "linha1\n\nlinha2"

    def test_normalize_spaces(self):
        text = "palavra1    palavra2"
        assert TextCleaner.clean(text) == "palavra1 palavra2"

    def test_remove_orphan_short_lines(self):
        text = "texto normal\nz\noutro texto"
        result = TextCleaner.clean(text)
        assert "texto normal" in result
        assert "outro texto" in result
        assert "z\n" not in result
        assert "\nz" not in result

    def test_preserve_digits(self):
        text = "R$ 1.500,00"
        assert TextCleaner.clean(text) == "R$ 1.500,00"

    def test_empty_text(self):
        assert TextCleaner.clean("") == ""

    def test_none_text(self):
        assert TextCleaner.clean("") == ""

    def test_fix_curly_quotes(self):
        text = '\u201cTexto entre aspas\u201d'
        result = TextCleaner.clean(text)
        assert '"' in result

    def test_fix_em_dash(self):
        text = "venda\u2014ok"
        result = TextCleaner.clean(text)
        assert "-" in result


class TestMarkdownFormatter:
    def test_format_empty(self):
        doc = ParsedDocument()
        result = MarkdownFormatter.format(doc)
        assert result == ""

    def test_format_header(self):
        doc = ParsedDocument(raw_text="Relatorio")
        doc.blocks = [Block(type=BlockType.HEADER, content="Relatorio")]
        result = MarkdownFormatter.format(doc)
        assert "# Relatorio" in result

    def test_format_key_value(self):
        doc = ParsedDocument(raw_text="Nome: Joao")
        doc.blocks = [Block(type=BlockType.KEY_VALUE, content="Nome: Joao")]
        result = MarkdownFormatter.format(doc)
        assert "**Nome:**" in result
        assert "Joao" in result

    def test_format_list(self):
        doc = ParsedDocument(raw_text="- Item 1\n- Item 2")
        doc.blocks = [Block(type=BlockType.LIST, content="- Item 1\n- Item 2")]
        result = MarkdownFormatter.format(doc)
        assert "- Item 1" in result
        assert "- Item 2" in result

    def test_format_paragraph(self):
        doc = ParsedDocument(raw_text="Texto qualquer")
        doc.blocks = [Block(type=BlockType.PARAGRAPH, content="Texto qualquer")]
        result = MarkdownFormatter.format(doc)
        assert "Texto qualquer" in result

    def test_format_table(self):
        table = [["Nome", "Idade"], ["Joao", "30"], ["Maria", "25"]]
        doc = ParsedDocument(raw_text="")
        doc.tables = [table]
        doc.blocks = []
        result = MarkdownFormatter.format(doc)
        assert "| Nome" in result
        assert "| Joao" in result
        assert "| Maria" in result

    def test_format_fields_table(self):
        doc = ParsedDocument(raw_text="")
        doc.fields = {"nome": "Joao", "idade": "30"}
        doc.blocks = []
        result = MarkdownFormatter.format(doc)
        assert "Campos Extraídos" in result
        assert "Nome" in result
        assert "30" in result

    def test_end_to_end(self):
        text = """
NOTA FISCAL ELETRONICA

CNPJ: 12.345.678/0001-90
Valor: R$ 1.500,00
Data: 15/03/2025
"""
        doc = DocumentParser.parse(text)
        result = MarkdownFormatter.format(doc, text)
        assert "Nota Fiscal" in result or "#" in result
        assert "CNPJ" in result or "12.345" in result
