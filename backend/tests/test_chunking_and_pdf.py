from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.application.services.chunking_service import ChunkingService
from app.application.services.pdf_service import PDFTextExtractor


def test_chunking_preserves_source_metadata():
    service = ChunkingService()
    pages = [(30, "kata " * 700, {"table_count": 1, "image_count": 0, "needs_ocr": False})]

    chunks = service.chunk_pages(pages, source_file="pedoman.pdf")

    assert len(chunks) >= 2
    assert chunks[0].page_number == 30
    assert chunks[0].metadata["source_file"] == "pedoman.pdf"
    assert chunks[0].metadata["table_count"] == 1
    assert chunks[0].metadata["generated_by"] == "pdf_upload_semantic_chunker"
    assert chunks[0].source_chunk_id.startswith("pedoman_")


def test_calendar_table_chunks_one_activity_per_chunk():
    service = ChunkingService()
    pages = [
        (
            1,
            """
            # Kalender Akademik
            | Halaman | Bagian | Kegiatan | Waktu |
            |---|---|---|---|
            | 1 | I. REGISTRASI | Pembayaran UKT | 1-10 Agustus 2025 |
            | 1 | I. REGISTRASI | Pengisian KRS | 11-15 Agustus 2025 |
            """,
            {"table_count": 1, "image_count": 0, "needs_ocr": False},
        )
    ]

    chunks = service.chunk_pages(pages, source_file="Kalender Akademik 2025-2026.pdf")

    assert len(chunks) == 2
    assert "Pembayaran UKT" in chunks[0].content
    assert chunks[0].metadata["block_types"] == ["calendar_row"]
    assert chunks[1].metadata["section"] == "I. REGISTRASI"


@pytest.mark.asyncio
async def test_pdf_extractor_rejects_non_pdf():
    extractor = PDFTextExtractor()
    upload = UploadFile(filename="notes.txt", file=BytesIO(b"not a pdf"))

    with pytest.raises(HTTPException):
        await extractor.extract_pages(upload)
