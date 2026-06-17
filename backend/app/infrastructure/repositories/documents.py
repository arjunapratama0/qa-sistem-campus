from uuid import UUID

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.infrastructure.db.models import Document, DocumentChunk
from app.infrastructure.db.vector import vector_literal


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self,
        created_by: UUID,
        title: str,
        source_type: str,
        source_url: str | None,
        file_name: str | None,
    ) -> Document:
        document = Document(
            created_by=created_by,
            title=title,
            source_type=source_type,
            source_url=source_url,
            file_name=file_name,
        )
        self.db.add(document)
        self.db.flush()
        return document

    def add_chunk(
        self,
        document_id: UUID,
        chunk_index: int,
        content: str,
        page_number: int | None,
        section_title: str | None,
        embedding: list[float],
    ) -> None:
        statement = text(
            """
            insert into document_chunks (
              document_id, chunk_index, content, page_number, section_title, token_count, embedding
            )
            values (
              :document_id, :chunk_index, :content, :page_number, :section_title, :token_count, cast(:embedding as vector)
            )
            """
        )
        self.db.execute(
            statement,
            {
                "document_id": document_id,
                "chunk_index": chunk_index,
                "content": content,
                "page_number": page_number,
                "section_title": section_title,
                "token_count": len(content.split()),
                "embedding": vector_literal(embedding),
            },
        )

    def list_documents(self) -> list[tuple[Document, int]]:
        return (
            self.db.query(Document, func.count(DocumentChunk.id).label("chunk_count"))
            .outerjoin(DocumentChunk, DocumentChunk.document_id == Document.id)
            .group_by(Document.id)
            .order_by(Document.created_at.desc())
            .all()
        )

