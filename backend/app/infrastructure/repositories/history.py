from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.domain.retrieval import RetrievedChunk
from app.infrastructure.db.models import Citation, DocumentChunk, QuestionHistory


class QuestionHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_with_citations(
        self,
        user_id: UUID,
        question: str,
        answer: str,
        confidence_score: float,
        chunks: list[RetrievedChunk],
    ) -> QuestionHistory:
        history = QuestionHistory(
            user_id=user_id,
            question=question,
            answer=answer,
            confidence_score=confidence_score,
        )
        self.db.add(history)
        self.db.flush()

        for rank, chunk in enumerate(chunks, start=1):
            self.db.add(
                Citation(
                    question_history_id=history.id,
                    document_chunk_id=chunk.id,
                    rank=rank,
                    similarity_score=chunk.similarity_score,
                    quote=chunk.content[:600],
                )
            )

        self.db.flush()
        self.db.refresh(history)
        return history

    def list_by_user(self, user_id: UUID, limit: int = 50) -> list[QuestionHistory]:
        return (
            self.db.query(QuestionHistory)
            .options(
                joinedload(QuestionHistory.citations)
                .joinedload(Citation.document_chunk)
                .joinedload(DocumentChunk.document)
            )
            .filter(QuestionHistory.user_id == user_id)
            .order_by(QuestionHistory.created_at.desc())
            .limit(limit)
            .all()
        )

