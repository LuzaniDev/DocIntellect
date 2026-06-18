"""Limpeza de texto OCR e formatacao inteligente em Markdown."""

import re

from app.extractors.document_parser import BlockType, DocumentParser, ParsedDocument


class TextCleaner:
    """Limpa e normaliza texto proveniente de OCR ou extracao de PDF."""

    # Padroes comuns de erros de OCR em portugues
    OCR_FIXES = [
        (r"([a-z])-\n\s*([a-z])", r"\1\2"),
        (r"([a-z])-\s*\n\s*([a-z])", r"\1\2"),
        (r"\n{3,}", "\n\n"),
        (r"[ \t]{2,}", " "),
    ]

    # Caracteres nao imprimiveis exceto quebras de linha
    PRINTABLE = re.compile(r"[^\S\n]|.", re.UNICODE)

    @classmethod
    def clean(cls, text: str) -> str:
        if not text:
            return text

        for pattern, replacement in cls.OCR_FIXES[:2]:
            text = re.sub(pattern, replacement, text)

        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)

        text = cls._fix_orphan_lines(text)
        text = cls._fix_common_ocr_errors(text)

        return text.strip()

    @classmethod
    def _fix_orphan_lines(cls, text: str) -> str:
        lines = text.split("\n")
        fixed = []
        for line in lines:
            stripped = line.strip()
            if len(stripped) <= 3 and stripped and not stripped.isdigit():
                continue
            fixed.append(line)
        return "\n".join(fixed)

    @classmethod
    def _fix_common_ocr_errors(cls, text: str) -> str:
        trocas = [
            ("|", "I"),
            ("\u201c", '"'),
            ("\u201d", '"'),
            ("\u2013", "-"),
            ("\u2014", "-"),
            ("\u00b0", "º"),
        ]
        for velho, novo in trocas:
            text = text.replace(velho, novo)
        return text


class MarkdownFormatter:
    """Gera Markdown bonito a partir do documento estruturado."""

    @classmethod
    def format(cls, doc: ParsedDocument, raw_text: str | None = None) -> str:
        parts: list[str] = []

        doc_type = cls._infer_document_type(doc)

        if doc_type:
            parts.append(f"# {doc_type}")
            parts.append("")

        for i, block in enumerate(doc.blocks):
            formatted = cls._format_block(block, i)
            if formatted:
                parts.append(formatted)

        if doc.tables:
            parts.append("")
            parts.append("## Tabelas")
            parts.append("")
            for table in doc.tables:
                table_md = cls._format_table(table)
                parts.append(table_md)
                parts.append("")

        if doc.fields:
            parts.append("")
            parts.append("## Campos Extraídos")
            parts.append("")
            parts.append("| Campo | Valor |")
            parts.append("|-------|-------|")
            for key, value in doc.fields.items():
                label = key.replace("_", " ").title()
                parts.append(f"| {label} | {value} |")
            parts.append("")

        return "\n".join(parts)

    @classmethod
    def _format_block(cls, block, index: int) -> str | None:
        t = block.type
        content = block.content.strip()

        if not content:
            return None

        if t == BlockType.HEADER:
            if content.startswith("#"):
                return content
            if index == 0:
                return f"# {content}"
            return f"## {content}"

        if t == BlockType.KEY_VALUE:
            lines = []
            for line in content.split("\n"):
                m = DocumentParser.KV_PATTERN.match(line.strip())
                if m:
                    key = m.group(1).strip().replace("_", " ").title()
                    value = m.group(2).strip()
                    lines.append(f"- **{key}:** {value}")
                else:
                    lines.append(line)
            return "\n".join(lines)

        if t == BlockType.LIST:
            lines = []
            for line in content.split("\n"):
                clean = line.lstrip("- *•\u2022").strip()
                lines.append(f"- {clean}")
            return "\n".join(lines)

        if t == BlockType.TABLE:
            return None

        if t == BlockType.PARAGRAPH:
            return content

        return content

    @classmethod
    def _format_table(cls, table_data: list[list[str]]) -> str:
        if not table_data:
            return ""
        header = table_data[0]
        rows = table_data[1:] if len(table_data) > 1 else []

        total_cols = len(header)

        col_widths = [len(h) for h in header]
        for row in rows:
            for i, cell in enumerate(row):
                if i < total_cols:
                    col_widths[i] = max(col_widths[i], len(cell))

        parts = []
        header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(header)) + " |"
        sep_line = "|-" + "-|-".join("-" * w for w in col_widths) + "-|"
        parts.append(header_line)
        parts.append(sep_line)

        for row in rows:
            padded = row + [""] * (total_cols - len(row))
            line = "| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(padded[:total_cols])) + " |"
            parts.append(line)

        return "\n".join(parts)

    @classmethod
    def _infer_document_type(cls, doc: ParsedDocument) -> str | None:
        keywords = {
            "nota fiscal": "Nota Fiscal",
            "contrato": "Contrato",
            "laudo": "Laudo Médico",
            "recibo": "Recibo",
            "boleto": "Boleto Bancário",
            "identidade": "Documento de Identidade",
            "rg": "Documento de Identidade",
            "cpf": "Documento",
            "extrato": "Extrato Bancário",
        }

        text_lower = doc.raw_text.lower()
        for keyword, label in keywords.items():
            if keyword in text_lower:
                return label

        if doc.fields:
            keys = " ".join(doc.fields.keys())
            for keyword, label in keywords.items():
                if keyword in keys:
                    return label

        return None
