from dataclasses import dataclass

from app.core.config import get_settings

settings = get_settings()


@dataclass(frozen=True)
class TextChunk:
    content: str
    page_number: int | None
    section_title: str | None
    metadata: dict


class ChunkingService:
    def chunk_pages(self, pages: list[tuple[int, str, dict]], source_file: str) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        for page_number, text, page_metadata in pages:
            normalized = self._normalize(text)
            if not normalized:
                continue

            words = normalized.split()
            start = 0
            page_chunk_index = 0
            while start < len(words):
                end = min(start + settings.chunk_target_words, len(words))
                content = " ".join(words[start:end])
                chunks.append(
                    TextChunk(
                        content=content,
                        page_number=page_number,
                        section_title=self._infer_heading(content),
                        metadata={
                            "source_file": source_file,
                            "page_start": page_number,
                            "page_end": page_number,
                            "chunk_index_on_page": page_chunk_index,
                            "word_start": start,
                            "word_end": end,
                            "generated_by": "pdf_upload",
                            **page_metadata,
                        },
                    )
                )
                if end >= len(words):
                    break
                start = max(0, end - settings.chunk_overlap_words)
                page_chunk_index += 1
        return chunks

    def _normalize(self, text: str) -> str:
        return " ".join(text.replace("\x00", " ").split())

    def _infer_heading(self, content: str) -> str | None:
        words = content.split()
        if not words:
            return None
        return " ".join(words[:16])[:240]
