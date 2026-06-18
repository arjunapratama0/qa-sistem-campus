from dataclasses import dataclass
from io import BytesIO
import re

from fastapi import HTTPException, UploadFile, status
import pdfplumber
from pypdf import PdfReader

from app.core.config import get_settings

settings = get_settings()


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    content: str
    metadata: dict


class PDFTextExtractor:
    async def extract_pages(self, file: UploadFile) -> list[ExtractedPage]:
        contents = await self._read_validated_pdf(file)
        source_file = file.filename or "uploaded.pdf"

        try:
            reader = PdfReader(BytesIO(contents))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PDF file") from exc

        text_pages, table_pages = self._extract_with_pdfplumber(contents, source_file)
        pages: list[ExtractedPage] = []

        for index, page in enumerate(reader.pages, start=1):
            text = text_pages.get(index, "")
            tables = table_pages.get(index, [])
            image_count = len(page.images or [])

            ocr_text = ""
            ocr_status = "not_needed"
            if not text.strip() and not tables and image_count > 0:
                ocr_text, ocr_status = self._try_ocr_page(contents, index)

            parts = [
                f"# Halaman {index}",
                f"<!-- source: {source_file} | page: {index} | type: text -->",
            ]
            if text.strip():
                parts.append(text.strip())
            if ocr_text.strip():
                parts.append("<!-- type: ocr -->")
                parts.append(ocr_text.strip())
            for table_index, table in enumerate(tables, start=1):
                parts.append(f"<!-- source: {source_file} | page: {index} | type: table | table_index: {table_index} -->")
                parts.append(table)

            combined = "\n\n".join(part for part in parts if part and part.strip())
            metadata = {
                "source_file": source_file,
                "has_text": bool(text.strip()),
                "table_count": len(tables),
                "image_count": image_count,
                "needs_ocr": not text.strip() and not tables and image_count > 0,
                "ocr_status": ocr_status,
            }
            if text.strip() or tables or ocr_text.strip():
                pages.append(ExtractedPage(page_number=index, content=combined, metadata=metadata))

        if not pages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No extractable text found in PDF. OCR may be required for scanned documents.",
            )
        return pages

    async def _read_validated_pdf(self, file: UploadFile) -> bytes:
        if file.content_type not in {"application/pdf", "application/octet-stream"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF uploads are supported")
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be a PDF")

        contents = await file.read()
        if len(contents) > settings.pdf_max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="PDF is too large")
        return contents

    def _extract_with_pdfplumber(self, contents: bytes, source_file: str) -> tuple[dict[int, str], dict[int, list[str]]]:
        text_by_page: dict[int, str] = {}
        tables_by_page: dict[int, list[str]] = {}
        try:
            with pdfplumber.open(BytesIO(contents)) as pdf:
                for page_index, page in enumerate(pdf.pages, start=1):
                    raw_text = page.extract_text() or ""
                    text_by_page[page_index] = self._normalize_pdf_text(raw_text)

                    tables = []
                    for table in page.extract_tables() or []:
                        markdown_table = self._table_to_markdown(table)
                        if markdown_table:
                            tables.append(markdown_table)
                    if tables:
                        tables_by_page[page_index] = tables
        except Exception:
            return self._extract_text_with_pypdf(contents), {}
        return text_by_page, tables_by_page

    def _extract_text_with_pypdf(self, contents: bytes) -> dict[int, str]:
        reader = PdfReader(BytesIO(contents))
        return {
            index: self._normalize_pdf_text(page.extract_text() or "")
            for index, page in enumerate(reader.pages, start=1)
        }

    def _try_ocr_page(self, contents: bytes, page_number: int) -> tuple[str, str]:
        if not settings.pdf_enable_ocr:
            return "", "disabled"

        try:
            import fitz
            import pytesseract
            from PIL import Image
        except Exception:
            return "", "unavailable"

        try:
            doc = fitz.open(stream=contents, filetype="pdf")
            page = doc.load_page(page_number - 1)
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            try:
                raw_text = pytesseract.image_to_string(image, lang="ind+eng")
            except Exception:
                raw_text = pytesseract.image_to_string(image, lang="eng")
            doc.close()
        except Exception:
            return "", "failed"

        text = self._normalize_pdf_text(raw_text)
        return text, "success" if text else "empty"

    def _normalize_pdf_text(self, text: str) -> str:
        if not text:
            return ""

        text = text.replace("\x00", " ").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n[ \t]+", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _clean_markdown_cell(self, cell) -> str:
        if cell is None:
            return ""
        value = str(cell).replace("\n", " ").replace("|", "\\|")
        return re.sub(r"\s+", " ", value).strip()

    def _table_to_markdown(self, table) -> str:
        if not table:
            return ""

        rows = []
        for row in table:
            cleaned_row = [self._clean_markdown_cell(cell) for cell in row or []]
            if any(cleaned_row):
                rows.append(cleaned_row)

        if not rows:
            return ""

        max_cols = max(len(row) for row in rows)
        normalized_rows = [row + [""] * (max_cols - len(row)) for row in rows]
        header = normalized_rows[0] if any(normalized_rows[0]) else [f"Kolom {index + 1}" for index in range(max_cols)]
        body = normalized_rows[1:]

        markdown = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(["---"] * max_cols) + " |",
        ]
        markdown.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(markdown)
