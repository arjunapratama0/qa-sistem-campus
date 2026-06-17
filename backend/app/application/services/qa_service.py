from sqlalchemy.orm import Session

from app.application.schemas.qa import AskQuestionResponse, CitationRead
from app.core.config import get_settings
from app.domain.retrieval import RetrievedChunk
from app.infrastructure.db.models import User
from app.infrastructure.external.jina import JinaEmbeddingClient
from app.infrastructure.repositories.chunks import ChunkRepository
from app.infrastructure.repositories.history import QuestionHistoryRepository

settings = get_settings()


class QAService:
    def __init__(self, db: Session, embedding_client: JinaEmbeddingClient | None = None):
        self.db = db
        self.embedding_client = embedding_client or JinaEmbeddingClient()
        self.chunks = ChunkRepository(db)
        self.histories = QuestionHistoryRepository(db)

    async def ask(self, question: str, current_user: User) -> AskQuestionResponse:
        embedding = await self.embedding_client.embed_query(question)
        retrieved = self.chunks.search_by_embedding(embedding, limit=settings.retrieval_top_k)
        usable_chunks = [
            chunk for chunk in retrieved if chunk.similarity_score >= settings.retrieval_min_similarity
        ]

        answer = self._build_answer(usable_chunks)
        confidence_score = self._calculate_confidence(usable_chunks)

        history = self.histories.create_with_citations(
            user_id=current_user.id,
            question=question,
            answer=answer,
            confidence_score=confidence_score,
            chunks=usable_chunks,
        )
        self.db.commit()
        self.db.refresh(history)

        citations = [
            CitationRead(
                document_chunk_id=chunk.id,
                document_title=chunk.document_title,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                rank=rank,
                similarity_score=round(chunk.similarity_score, 5),
                quote=chunk.content[:600],
            )
            for rank, chunk in enumerate(usable_chunks, start=1)
        ]

        return AskQuestionResponse(
            history_id=history.id,
            question=question,
            answer=answer,
            confidence_score=confidence_score,
            citations=citations,
            created_at=history.created_at,
        )

    def _build_answer(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return (
                "Saya belum menemukan sumber kampus yang cukup relevan untuk menjawab pertanyaan ini. "
                "Silakan coba gunakan kata kunci yang lebih spesifik atau hubungi bagian akademik."
            )

        selected = chunks[:2]
        evidence = " ".join(self._trim_sentence(chunk.content, 420) for chunk in selected)
        return (
            "Berdasarkan dokumen kampus yang tersedia, "
            f"{evidence} "
            "Silakan periksa kutipan sumber di bawah untuk memastikan konteks dan detail resminya."
        )

    def _trim_sentence(self, text: str, max_length: int) -> str:
        cleaned = " ".join(text.split())
        if len(cleaned) <= max_length:
            return cleaned
        return cleaned[:max_length].rsplit(" ", 1)[0] + "..."

    def _calculate_confidence(self, chunks: list[RetrievedChunk]) -> float:
        if not chunks:
            return 0.0

        similarities = [max(0.0, min(1.0, chunk.similarity_score)) for chunk in chunks]
        top_similarity = similarities[0]
        average_similarity = sum(similarities) / len(similarities)
        coverage = min(len(chunks) / settings.retrieval_top_k, 1.0)
        confidence = (top_similarity * 0.7) + (average_similarity * 0.2) + (coverage * 0.1)
        return round(max(0.0, min(confidence, 1.0)), 4)

