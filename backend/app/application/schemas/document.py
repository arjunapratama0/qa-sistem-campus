from uuid import UUID

from pydantic import BaseModel, Field


class DocumentChunkInput(BaseModel):
    content: str = Field(min_length=10)
    page_number: int | None = None
    section_title: str | None = None


class DocumentCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    source_type: str = "manual"
    source_url: str | None = None
    file_name: str | None = None
    chunks: list[DocumentChunkInput] = Field(min_length=1)


class DocumentRead(BaseModel):
    id: UUID
    title: str
    source_type: str
    source_url: str | None = None
    file_name: str | None = None
    status: str
    chunk_count: int = 0


class DocumentUploadResponse(DocumentRead):
    message: str
