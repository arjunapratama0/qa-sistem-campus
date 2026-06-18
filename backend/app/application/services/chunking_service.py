from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Any

from app.application.services.pdf_service import ExtractedPage
from app.core.config import get_settings

settings = get_settings()

TARGET_CHARS_PER_WORD = 6
MIN_CHUNK_CHARS = 120
PEDOMAN_BODY_START_PAGE = 25


@dataclass(frozen=True)
class TextBlock:
    text: str
    source_file: str
    doc_type: str
    page: int | None
    chapter: str
    section: str
    subsection: str
    block_type: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class TextChunk:
    content: str
    page_number: int | None
    section_title: str | None
    metadata: dict
    source_chunk_id: str


class ChunkingService:
    def chunk_pages(self, pages: list[ExtractedPage | tuple[int, str, dict]], source_file: str) -> list[TextChunk]:
        extracted_pages = [self._coerce_page(page, source_file) for page in pages]
        cleaned_pages = [ExtractedPage(page.page_number, self._clean_markdown_for_rag(page.content), page.metadata) for page in extracted_pages]
        blocks = self._parse_pages_to_blocks(cleaned_pages, source_file)
        return self._chunk_blocks(blocks)

    def _coerce_page(self, page: ExtractedPage | tuple[int, str, dict], source_file: str) -> ExtractedPage:
        if isinstance(page, ExtractedPage):
            return page
        page_number, content, metadata = page
        return ExtractedPage(page_number=page_number, content=content, metadata={"source_file": source_file, **metadata})

    def _clean_markdown_for_rag(self, markdown_text: str) -> str:
        cleaned_lines = []
        for raw_line in markdown_text.splitlines():
            line = self._fix_doubled_char_line(raw_line)
            line = line.replace("\x00", " ")
            line = re.sub(r"[ \t]+", " ", line).strip()
            line = self._remove_known_footer_noise(line)
            if self._is_empty_extraction_line(line):
                line = ""
            cleaned_lines.append(line)

        normalized = []
        previous_blank = False
        for line in cleaned_lines:
            blank = line == ""
            if blank and previous_blank:
                continue
            normalized.append(line)
            previous_blank = blank
        return re.sub(r"\n{3,}", "\n\n", "\n".join(normalized)).strip()

    def _fix_doubled_char_line(self, line: str) -> str:
        if len(line) < 20:
            return line
        non_space = [char for char in line if not char.isspace()]
        repeated_pairs = sum(1 for index in range(len(line) - 1) if line[index] == line[index + 1] and not line[index].isspace())
        if repeated_pairs / max(len(non_space), 1) >= 0.25:
            return re.sub(r"(.)\1", r"\1", line)
        return line

    def _remove_known_footer_noise(self, line: str) -> str:
        line = re.sub(
            r"\b(?:[ivxlcdm]+|\d+)?\s*Pedoman Akademik Program Sarjana Fakultas Teknik Universitas Udayana\s+20(?:22|24)\s*(?:[ivxlcdm]+|\d+)?\b",
            " ",
            line,
            flags=re.IGNORECASE,
        )
        return re.sub(r"\s+", " ", line).strip()

    def _is_empty_extraction_line(self, line: str) -> bool:
        return re.match(r"^_?Tidak ada teks (yang )?berhasil diekstrak.*_?$", line, re.IGNORECASE) is not None

    def _parse_pages_to_blocks(self, pages: list[ExtractedPage], fallback_source_file: str) -> list[TextBlock]:
        blocks: list[TextBlock] = []
        current_chapter = ""
        current_section = ""
        current_subsection = ""
        paragraph_buffer: list[str] = []
        table_buffer: list[str] = []

        for page in pages:
            source_file = page.metadata.get("source_file") or fallback_source_file
            doc_type = self._infer_doc_type(source_file)

            def should_skip(line: str = "") -> bool:
                return self._is_excluded_line(line, doc_type, page.page_number, current_chapter)

            def make_block(text: str, block_type: str) -> None:
                text = text.strip()
                if not text or should_skip(text):
                    return
                blocks.append(
                    TextBlock(
                        text=text,
                        source_file=source_file,
                        doc_type=doc_type,
                        page=page.page_number,
                        chapter=current_chapter,
                        section=current_section,
                        subsection=current_subsection,
                        block_type=block_type,
                        metadata=page.metadata,
                    )
                )

            def flush_paragraph() -> None:
                nonlocal paragraph_buffer
                if paragraph_buffer:
                    make_block(self._normalize_paragraph_lines(paragraph_buffer), "paragraph")
                    paragraph_buffer = []

            def flush_table() -> None:
                nonlocal table_buffer
                if not table_buffer:
                    return
                table_text = "\n".join(table_buffer)
                if doc_type == "kalender_akademik":
                    for calendar_block in self._calendar_table_to_blocks(
                        table_text, source_file, page.page_number, current_chapter, current_section, page.metadata
                    ):
                        blocks.append(calendar_block)
                else:
                    make_block(table_text, "table")
                table_buffer = []

            for raw_line in page.content.splitlines():
                line = raw_line.strip()
                if not line:
                    flush_table()
                    flush_paragraph()
                    continue

                if self._is_metadata_comment(line) or self._is_page_heading(line):
                    flush_table()
                    flush_paragraph()
                    continue

                if self._is_markdown_table_line(line):
                    flush_paragraph()
                    table_buffer.append(line)
                    continue

                if table_buffer:
                    flush_table()

                heading_type = self._classify_heading(line, doc_type)
                if heading_type:
                    flush_paragraph()
                    heading = self._normalize_heading(line, doc_type)
                    if should_skip(heading):
                        continue
                    if heading_type == "chapter":
                        current_chapter = heading
                        current_section = ""
                        current_subsection = ""
                    elif heading_type == "section":
                        current_section = heading
                        current_subsection = ""
                    elif heading_type == "subsection":
                        current_subsection = heading
                    make_block(heading, "heading")
                    continue

                if not should_skip(line):
                    paragraph_buffer.append(line)

            flush_table()
            flush_paragraph()

        return blocks

    def _chunk_blocks(self, blocks: list[TextBlock]) -> list[TextChunk]:
        expanded_blocks = self._expand_oversized_blocks(blocks)
        chunks: list[TextChunk] = []
        buffer: list[TextBlock] = []
        buffer_chars = 0
        chunk_index = 0
        target_chars = max(settings.chunk_target_words * TARGET_CHARS_PER_WORD, 600)
        overlap_chars = max(settings.chunk_overlap_words * TARGET_CHARS_PER_WORD, 0)

        def flush_buffer() -> None:
            nonlocal buffer, buffer_chars, chunk_index
            if not buffer:
                return
            chunk = self._build_chunk_from_blocks(buffer, chunk_index)
            if chunk:
                chunks.append(chunk)
                chunk_index += 1
            buffer = []
            buffer_chars = 0

        for block in expanded_blocks:
            if block.doc_type == "kalender_akademik" and block.block_type == "calendar_row":
                flush_buffer()
                chunk = self._build_chunk_from_blocks([block], chunk_index, allow_short=True)
                if chunk:
                    chunks.append(chunk)
                    chunk_index += 1
                continue

            block_len = len(block.text)
            if buffer and block.source_file != buffer[0].source_file:
                flush_buffer()

            if buffer and buffer_chars + block_len > target_chars:
                chunk = self._build_chunk_from_blocks(buffer, chunk_index)
                if chunk:
                    chunks.append(chunk)
                    chunk_index += 1
                buffer = self._overlap_tail_blocks(buffer, overlap_chars)
                buffer_chars = sum(len(item.text) for item in buffer)

            buffer.append(block)
            buffer_chars += block_len

        flush_buffer()
        return chunks

    def _build_chunk_from_blocks(self, blocks: list[TextBlock], chunk_index: int, allow_short: bool = False) -> TextChunk | None:
        if not blocks:
            return None

        text_parts = [f"## {block.text}" if block.block_type == "heading" else block.text for block in blocks]
        text = "\n\n".join(text_parts).strip()
        if len(text) < MIN_CHUNK_CHARS and not allow_short and not any(block.block_type.startswith("table") for block in blocks):
            return None

        pages = [block.page for block in blocks if block.page is not None]
        source_file = blocks[0].source_file
        chapter = self._last_non_empty(block.chapter for block in blocks)
        section = self._last_non_empty(block.section for block in blocks)
        subsection = self._last_non_empty(block.subsection for block in blocks)
        section_title = subsection or section or chapter or self._infer_heading(text)
        source_chunk_id = self._create_chunk_id(source_file, chunk_index, text)

        metadata = {
            "source_file": source_file,
            "doc_type": blocks[0].doc_type,
            "page_start": min(pages) if pages else None,
            "page_end": max(pages) if pages else None,
            "pages": self._format_pages(pages),
            "chapter": chapter,
            "section": section,
            "subsection": subsection,
            "current_heading": section_title,
            "section_path": " > ".join(part for part in [chapter, section, subsection] if part),
            "chunk_index": chunk_index,
            "char_count": len(text),
            "block_types": sorted({block.block_type for block in blocks}),
            "generated_by": "pdf_upload_semantic_chunker",
            **blocks[0].metadata,
        }

        return TextChunk(
            content=text,
            page_number=min(pages) if pages else None,
            section_title=section_title,
            metadata=metadata,
            source_chunk_id=source_chunk_id,
        )

    def _expand_oversized_blocks(self, blocks: list[TextBlock]) -> list[TextBlock]:
        target_chars = max(settings.chunk_target_words * TARGET_CHARS_PER_WORD, 600)
        overlap_chars = max(settings.chunk_overlap_words * TARGET_CHARS_PER_WORD, 0)
        expanded: list[TextBlock] = []
        for block in blocks:
            if len(block.text) <= target_chars:
                expanded.append(block)
                continue
            for index, part in enumerate(self._split_long_text(block.text, target_chars, overlap_chars), start=1):
                expanded.append(
                    TextBlock(
                        text=part,
                        source_file=block.source_file,
                        doc_type=block.doc_type,
                        page=block.page,
                        chapter=block.chapter,
                        section=block.section,
                        subsection=block.subsection,
                        block_type=f"{block.block_type}_part_{index}",
                        metadata=block.metadata,
                    )
                )
        return expanded

    def _split_long_text(self, text: str, target_chars: int, overlap_chars: int) -> list[str]:
        if len(text) <= target_chars:
            return [text]
        if "\n|" in text or text.startswith("|"):
            return self._split_table_text(text, target_chars)

        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: list[str] = []
        current = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(current) + len(sentence) + 1 <= target_chars:
                current = f"{current} {sentence}".strip()
            else:
                if current:
                    chunks.append(current)
                if len(sentence) > target_chars:
                    step = max(target_chars - overlap_chars, 1)
                    chunks.extend(sentence[start : start + target_chars].strip() for start in range(0, len(sentence), step))
                    current = ""
                else:
                    current = sentence
        if current:
            chunks.append(current)
        return [chunk for chunk in chunks if chunk]

    def _split_table_text(self, text: str, target_chars: int) -> list[str]:
        chunks = []
        current_lines = []
        current_len = 0
        for line in text.splitlines():
            line_len = len(line) + 1
            if current_lines and current_len + line_len > target_chars:
                chunks.append("\n".join(current_lines).strip())
                current_lines = []
                current_len = 0
            current_lines.append(line)
            current_len += line_len
        if current_lines:
            chunks.append("\n".join(current_lines).strip())
        return chunks

    def _overlap_tail_blocks(self, blocks: list[TextBlock], overlap_chars: int) -> list[TextBlock]:
        if overlap_chars <= 0 or not blocks:
            return []
        tail = blocks[-1].text[-overlap_chars:].strip()
        if not tail:
            return []
        last = blocks[-1]
        return [
            TextBlock(
                text=tail,
                source_file=last.source_file,
                doc_type=last.doc_type,
                page=last.page,
                chapter=last.chapter,
                section=last.section,
                subsection=last.subsection,
                block_type="overlap",
                metadata=last.metadata,
            )
        ]

    def _calendar_table_to_blocks(
        self,
        table_text: str,
        source_file: str,
        fallback_page: int | None,
        chapter: str,
        section: str,
        page_metadata: dict[str, Any],
    ) -> list[TextBlock]:
        rows = [row.strip() for row in table_text.splitlines() if row.strip()]
        if len(rows) < 3:
            return []

        header = [cell.lower() for cell in self._split_markdown_table_row(rows[0])]
        required_columns = ["halaman", "bagian", "kegiatan", "waktu"]
        if not all(column in header for column in required_columns):
            return []

        index_map = {column: header.index(column) for column in required_columns}
        blocks: list[TextBlock] = []
        for row in rows[2:]:
            if self._is_table_separator_row(row):
                continue
            cells = self._split_markdown_table_row(row)
            if len(cells) < len(header):
                cells = cells + [""] * (len(header) - len(cells))

            page_text = cells[index_map["halaman"]].strip()
            row_section = self._normalize_calendar_section(cells[index_map["bagian"]].strip() or section)
            activity = cells[index_map["kegiatan"]].strip()
            date_text = cells[index_map["waktu"]].strip()
            if not activity and not date_text:
                continue

            page = int(page_text) if page_text.isdigit() else fallback_page
            text = f"Bagian: {row_section}\nKegiatan: {activity}\nWaktu: {date_text}".strip()
            blocks.append(
                TextBlock(
                    text=text,
                    source_file=source_file,
                    doc_type="kalender_akademik",
                    page=page,
                    chapter=chapter or "Kalender Akademik",
                    section=row_section,
                    subsection="",
                    block_type="calendar_row",
                    metadata=page_metadata,
                )
            )
        return blocks

    def _split_markdown_table_row(self, row: str) -> list[str]:
        return [cell.strip() for cell in row.strip().strip("|").split("|")]

    def _is_table_separator_row(self, row: str) -> bool:
        cells = self._split_markdown_table_row(row)
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)

    def _classify_heading(self, line: str, doc_type: str) -> str | None:
        text = self._normalize_heading(line, doc_type)
        if not text:
            return None
        if doc_type == "kalender_akademik":
            if text.lower().startswith(("kalender akademik", "tabel kalender akademik")):
                return "chapter"
            if re.match(r"^(SEMESTER\s+.+|[IVXLC]+\.\s+.+|KEGIATAN AKADEMIK LAINNYA.+)$", text, re.IGNORECASE):
                return "section"
            return None
        if re.match(r"^(BAGIAN\s+\d+\.?\s+.+|LAMPIRAN\s+[A-Z]\.?\s+.+)$", text, re.IGNORECASE):
            return "chapter"
        if re.match(r"^\d+\.\d+\.\d+(?:\.\d+)*\.?\s+.+$", text, re.IGNORECASE):
            return "subsection"
        if re.match(r"^\d+\.\d+\.?\s+.+$", text, re.IGNORECASE):
            return "section"
        return None

    def _normalize_heading(self, line: str, doc_type: str) -> str:
        text = re.sub(r"^#+\s*", "", line).strip()
        text = re.sub(r"\.{5,}\s*\d+\s*$", "", text).strip()
        if doc_type == "kalender_akademik":
            text = self._normalize_calendar_section(text)
        return text

    def _normalize_calendar_section(self, section: str) -> str:
        replacements = {"ll.": "II.", "lll.": "III.", "Il.": "II.", "Nopember": "November"}
        for wrong, correct in replacements.items():
            section = section.replace(wrong, correct)
        return re.sub(r"\s+", " ", section).strip()

    def _is_excluded_line(self, line: str, doc_type: str, page: int | None, current_chapter: str) -> bool:
        if doc_type != "pedoman_akademik":
            return False
        text = re.sub(r"^#+\s*", "", line).strip()
        if page is not None and page < PEDOMAN_BODY_START_PAGE:
            return True
        if re.match(r"^(DAFTAR ISI|DAFTAR TABEL|DAFTAR GAMBAR)\b", text, re.IGNORECASE):
            return True
        if re.match(r"^(DAFTAR ISI|DAFTAR TABEL|DAFTAR GAMBAR)\b", current_chapter, re.IGNORECASE):
            return True
        return False

    def _infer_doc_type(self, filename: str) -> str:
        name = filename.lower()
        if "kalender" in name:
            return "kalender_akademik"
        if "pedoman" in name:
            return "pedoman_akademik"
        return "dokumen_akademik"

    def _normalize_paragraph_lines(self, lines: list[str]) -> str:
        return re.sub(r"\s+", " ", " ".join(line.strip() for line in lines if line.strip())).strip()

    def _is_metadata_comment(self, line: str) -> bool:
        return line.startswith("<!--") and line.endswith("-->")

    def _is_page_heading(self, line: str) -> bool:
        return re.match(r"^#{1,3}\s*Halaman\s+\d+", line, re.IGNORECASE) is not None

    def _is_markdown_table_line(self, line: str) -> bool:
        return re.match(r"^\|.*\|$", line) is not None

    def _create_chunk_id(self, source_file: str, chunk_index: int, text: str) -> str:
        source_stem = re.sub(r"[^a-z0-9]+", "_", Path(source_file).stem.lower()).strip("_")
        digest = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
        return f"{source_stem}_{chunk_index:04d}_{digest}"

    def _format_pages(self, pages: list[int]) -> str:
        unique_pages = sorted(set(pages))
        if not unique_pages:
            return ""
        if len(unique_pages) == 1:
            return str(unique_pages[0])
        return f"{unique_pages[0]}-{unique_pages[-1]}"

    def _last_non_empty(self, values) -> str:
        found = ""
        for value in values:
            if value:
                found = value
        return found

    def _infer_heading(self, content: str) -> str | None:
        words = content.split()
        if not words:
            return None
        return " ".join(words[:16])[:240]
