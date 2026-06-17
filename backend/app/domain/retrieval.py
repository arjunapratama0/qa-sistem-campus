from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RetrievedChunk:
    id: UUID
    document_id: UUID
    document_title: str
    content: str
    page_number: int | None
    section_title: str | None
    similarity_score: float

