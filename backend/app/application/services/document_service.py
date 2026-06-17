from sqlalchemy.orm import Session

from app.application.schemas.document import DocumentCreateRequest, DocumentRead
from app.infrastructure.db.models import User
from app.infrastructure.external.jina import JinaEmbeddingClient
from app.infrastructure.repositories.documents import DocumentRepository


class DocumentService:
    def __init__(self, db: Session, embedding_client: JinaEmbeddingClient | None = None):
        self.db = db
        self.documents = DocumentRepository(db)
        self.embedding_client = embedding_client or JinaEmbeddingClient()

    async def create_document(self, payload: DocumentCreateRequest, current_user: User) -> DocumentRead:
        document = self.documents.create_document(
            created_by=current_user.id,
            title=payload.title,
            source_type=payload.source_type,
            source_url=payload.source_url,
            file_name=payload.file_name,
        )
        embeddings = await self.embedding_client.embed_passages([chunk.content for chunk in payload.chunks])

        for index, (chunk, embedding) in enumerate(zip(payload.chunks, embeddings), start=0):
            self.documents.add_chunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk.content,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                embedding=embedding,
            )

        self.db.commit()
        return DocumentRead(
            id=document.id,
            title=document.title,
            source_type=document.source_type,
            source_url=document.source_url,
            file_name=document.file_name,
            status=document.status,
            chunk_count=len(payload.chunks),
        )

    def list_documents(self) -> list[DocumentRead]:
        rows = self.documents.list_documents()
        return [
            DocumentRead(
                id=document.id,
                title=document.title,
                source_type=document.source_type,
                source_url=document.source_url,
                file_name=document.file_name,
                status=document.status,
                chunk_count=chunk_count,
            )
            for document, chunk_count in rows
        ]

