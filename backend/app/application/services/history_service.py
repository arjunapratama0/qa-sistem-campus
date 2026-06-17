from sqlalchemy.orm import Session

from app.application.schemas.history import HistoryItem
from app.application.schemas.qa import CitationRead
from app.infrastructure.db.models import User
from app.infrastructure.repositories.history import QuestionHistoryRepository


class HistoryService:
    def __init__(self, db: Session):
        self.histories = QuestionHistoryRepository(db)

    def list_my_history(self, current_user: User) -> list[HistoryItem]:
        histories = self.histories.list_by_user(current_user.id)
        items: list[HistoryItem] = []
        for history in histories:
            citations = []
            for citation in sorted(history.citations, key=lambda item: item.rank):
                chunk = citation.document_chunk
                citations.append(
                    CitationRead(
                        id=citation.id,
                        document_chunk_id=chunk.id,
                        document_title=chunk.document.title,
                        page_number=chunk.page_number,
                        section_title=chunk.section_title,
                        rank=citation.rank,
                        similarity_score=float(citation.similarity_score),
                        quote=citation.quote,
                    )
                )
            items.append(
                HistoryItem(
                    id=history.id,
                    question=history.question,
                    answer=history.answer,
                    confidence_score=float(history.confidence_score),
                    created_at=history.created_at,
                    citations=citations,
                )
            )
        return items

