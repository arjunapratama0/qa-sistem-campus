from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.application.services.chunking_service import ChunkingService
from app.application.services.pdf_service import PDFTextExtractor


def test_chunking_preserves_source_metadata():
    service = ChunkingService()
    pages = [(3, "kata " * 700, {"table_count": 1, "image_count": 0, "needs_ocr": False})]

    chunks = service.chunk_pages(pages, source_file="pedoman.pdf")

    assert len(chunks) >= 2
    assert chunks[0].page_number == 3
    assert chunks[0].metadata["source_file"] == "pedoman.pdf"
    assert chunks[0].metadata["table_count"] == 1
    assert chunks[0].metadata["generated_by"] == "pdf_upload"


@pytest.mark.asyncio
async def test_pdf_extractor_rejects_non_pdf():
    extractor = PDFTextExtractor()
    upload = UploadFile(filename="notes.txt", file=BytesIO(b"not a pdf"))

    with pytest.raises(HTTPException):
        await extractor.extract_pages(upload)
