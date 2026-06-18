"""Parser inteligente de documentos: detecta tabelas, seções, listas e pares chave-valor."""

import re
from dataclasses import dataclass, field
from enum import Enum


class BlockType(str, Enum):
    HEADER = "header"
    KEY_VALUE = "key_value"
    TABLE = "table"
    LIST = "list"
    PARAGRAPH = "paragraph"
    EMPTY = "empty"


@dataclass
class Block:
    type: BlockType
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class ParsedDocument:
    blocks: list[Block] = field(default_factory=list)
    tables: list[list[list[str]]] = field(default_factory=list)
    fields: dict[str, str] = field(default_factory=dict)
    raw_text: str = ""


class DocumentParser:
    HEADER_PATTERNS = [
        re.compile(r"^(#{1,3}\s+|\d+[.\)]\s+[A-Z]|(?:nota\s*fiscal|contrato|laudo|recibo|relatorio|certidao|atestado|boleto|extrato)\b)", re.IGNORECASE),
        re.compile(r"^[A-ZÀ-Ú][A-ZÀ-Ú\s\-/:]{4,}$"),
    ]

    KV_PATTERN = re.compile(r"^([A-Za-zÀ-Ú][A-Za-zÀ-Ú\s\-/.]{1,40}?)\s*[:=]\s*(.+?)$", re.IGNORECASE)

    @classmethod
    def parse(cls, text: str) -> ParsedDocument:
        if not text:
            return ParsedDocument()

        doc = ParsedDocument(raw_text=text)
        lines = text.split("\n")
        blocks = cls._split_blocks(lines)
        doc.blocks = blocks

        for block in blocks:
            if block.type == BlockType.TABLE:
                table = cls._parse_table(block.content)
                if table:
                    doc.tables.append(table)

        doc.fields = cls._extract_fields(blocks)

        return doc

    @classmethod
    def _split_blocks(cls, lines: list[str]) -> list[Block]:
        blocks: list[Block] = []
        current_lines: list[str] = []
        current_type: BlockType | None = None

        def flush():
            if not current_lines:
                return
            content = "\n".join(current_lines)
            blocks.append(Block(type=current_type or BlockType.PARAGRAPH, content=content))
            current_lines.clear()

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_type is not None:
                    flush()
                current_type = None
                continue

            detected = cls._detect_block_type(stripped, current_type)

            if detected in (BlockType.HEADER, BlockType.TABLE, BlockType.LIST) and detected != current_type:
                flush()
                current_type = detected

            elif detected == BlockType.KEY_VALUE and current_type not in (BlockType.TABLE,):
                flush()
                current_type = BlockType.KEY_VALUE

            elif current_type is None:
                current_type = BlockType.PARAGRAPH

            current_lines.append(stripped)

        flush()
        return blocks

    @classmethod
    def _detect_block_type(cls, line: str, current: BlockType | None) -> BlockType:
        if any(p.match(line) for p in cls.HEADER_PATTERNS):
            return BlockType.HEADER

        if cls.KV_PATTERN.match(line):
            return BlockType.KEY_VALUE

        if cls._looks_like_table(line):
            return BlockType.TABLE

        if line.startswith(("- ", "* ", "•", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            return BlockType.LIST

        return BlockType.PARAGRAPH

    @classmethod
    def _looks_like_table(cls, line: str) -> bool:
        if line.count("|") >= 2:
            return True

        parts = line.split()
        if len(parts) >= 4:
            sizes = [len(p) for p in parts]
            if max(sizes) - min(sizes) < 15 and len(parts) <= 12:
                return True

        return False

    @classmethod
    def _parse_table(cls, text: str) -> list[list[str]]:
        rows = text.split("\n")
        table: list[list[str]] = []

        for row in rows:
            if "|" in row:
                cells = [c.strip() for c in row.split("|") if c.strip()]
            else:
                cells = [c for c in row.split() if c]

            if len(cells) >= 2:
                table.append(cells)

        return table if len(table) >= 2 else []

    @classmethod
    def _extract_fields(cls, blocks: list[Block]) -> dict[str, str]:
        fields: dict[str, str] = {}

        for block in blocks:
            if block.type == BlockType.KEY_VALUE:
                for line in block.content.split("\n"):
                    m = cls.KV_PATTERN.match(line.strip())
                    if m:
                        key = m.group(1).strip().lower().replace(" ", "_")
                        value = m.group(2).strip()
                        fields[key] = value

        return fields

    @classmethod
    def to_markdown(cls, doc: ParsedDocument) -> str:
        parts: list[str] = []

        for block in doc.blocks:
            if block.type == BlockType.HEADER:
                if not block.content.startswith("#"):
                    parts.append(f"### {block.content}")
                else:
                    parts.append(block.content)

            elif block.type == BlockType.KEY_VALUE:
                for line in block.content.split("\n"):
                    m = cls.KV_PATTERN.match(line.strip())
                    if m:
                        parts.append(f"- **{m.group(1).strip()}:** {m.group(2).strip()}")
                    else:
                        parts.append(line)

            elif block.type == BlockType.TABLE:
                table = cls._parse_table(block.content)
                if table:
                    header = "| " + " | ".join(table[0]) + " |"
                    sep = "| " + " | ".join(["---"] * len(table[0])) + " |"
                    body = ["| " + " | ".join(row) + " |" for row in table[1:]]
                    parts.append(header)
                    parts.append(sep)
                    parts.extend(body)

            elif block.type == BlockType.LIST:
                for line in block.content.split("\n"):
                    parts.append(f"- {line.lstrip('- *•').strip()}")

            else:
                parts.append(block.content)

            parts.append("")

        return "\n".join(parts)
