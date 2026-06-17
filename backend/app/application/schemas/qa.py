from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AskQuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class CitationRead(BaseModel):
    id: UUID | None = None
    document_chunk_id: UUID
    document_title: str
    page_number: int | None = None
    section_title: str | None = None
    rank: int
    similarity_score: float
    quote: str


class AskQuestionResponse(BaseModel):
    history_id: UUID
    question: str
    answer: str
    confidence_score: float
    citations: list[CitationRead]
    created_at: datetime

