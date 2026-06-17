from io import BytesIO

from fastapi import HTTPException, UploadFile, status
import pdfplumber
from pypdf import PdfReader

from app.core.config import get_settings

settings = get_settings()


class PDFTextExtractor:
    async def extract_pages(self, file: UploadFile) -> list[tuple[int, str, dict]]:
        if file.content_type not in {"application/pdf", "application/octet-stream"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF uploads are supported")
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be a PDF")

        contents = await file.read()
        if len(contents) > settings.pdf_max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="PDF is too large")

        try:
            reader = PdfReader(BytesIO(contents))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PDF file") from exc

        page_tables = self._extract_tables(contents)
        pages: list[tuple[int, str, dict]] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            tables = page_tables.get(index, [])
            table_text = "\n".join(tables)
            combined = "\n\n".join(part for part in [text.strip(), table_text.strip()] if part)
            image_count = len(page.images or [])
            metadata = {
                "has_text": bool(text.strip()),
                "table_count": len(tables),
                "image_count": image_count,
                "needs_ocr": not combined.strip() and image_count > 0,
            }
            if combined.strip():
                pages.append((index, combined, metadata))

        if not pages:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No extractable text found in PDF")
        return pages

    def _extract_tables(self, contents: bytes) -> dict[int, list[str]]:
        tables_by_page: dict[int, list[str]] = {}
        try:
            with pdfplumber.open(BytesIO(contents)) as pdf:
                for page_index, page in enumerate(pdf.pages, start=1):
                    tables = []
                    for table in page.extract_tables() or []:
                        rows = []
                        for row in table:
                            values = [str(cell).strip() if cell is not None else "" for cell in row]
                            if any(values):
                                rows.append(" | ".join(values))
                        if rows:
                            tables.append("\n".join(rows))
                    if tables:
                        tables_by_page[page_index] = tables
        except Exception:
            return {}
        return tables_by_page
