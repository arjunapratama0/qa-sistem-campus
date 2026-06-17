from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.application.schemas.qa import CitationRead


class HistoryItem(BaseModel):
    id: UUID
    question: str
    answer: str
    confidence_score: float
    created_at: datetime
    citations: list[CitationRead] = []

