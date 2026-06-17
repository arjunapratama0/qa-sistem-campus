from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.retrieval import RetrievedChunk
from app.infrastructure.db.vector import vector_literal


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_by_embedding(self, embedding: list[float], limit: int) -> list[RetrievedChunk]:
        query = text(
            """
            select
              dc.id,
              dc.document_id,
              d.title as document_title,
              dc.content,
              dc.page_number,
              dc.section_title,
              1 - (dc.embedding <=> cast(:embedding as vector)) as similarity_score
            from document_chunks dc
            join documents d on d.id = dc.document_id
            where d.status = 'active'
            order by dc.embedding <=> cast(:embedding as vector)
            limit :limit
            """
        )
        rows = self.db.execute(query, {"embedding": vector_literal(embedding), "limit": limit}).mappings().all()
        return [
            RetrievedChunk(
                id=row["id"],
                document_id=row["document_id"],
                document_title=row["document_title"],
                content=row["content"],
                page_number=row["page_number"],
                section_title=row["section_title"],
                similarity_score=float(row["similarity_score"]),
            )
            for row in rows
        ]

