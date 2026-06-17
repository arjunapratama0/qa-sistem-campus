from sqlalchemy.orm import Session

from fastapi import UploadFile

from app.application.schemas.document import DocumentCreateRequest, DocumentRead, DocumentUploadResponse
from app.application.services.chunking_service import ChunkingService
from app.application.services.pdf_service import PDFTextExtractor
from app.infrastructure.db.models import User
from app.infrastructure.external.jina import JinaEmbeddingClient
from app.infrastructure.repositories.documents import DocumentRepository


class DocumentService:
    def __init__(self, db: Session, embedding_client: JinaEmbeddingClient | None = None):
        self.db = db
        self.documents = DocumentRepository(db)
        self.embedding_client = embedding_client or JinaEmbeddingClient()
        self.chunking = ChunkingService()
        self.pdf_extractor = PDFTextExtractor()

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
                metadata={"source_type": "manual"},
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

    async def upload_pdf(self, file: UploadFile, current_user: User, title: str | None = None) -> DocumentUploadResponse:
        pages = await self.pdf_extractor.extract_pages(file)
        source_file = file.filename or "uploaded.pdf"
        chunks = self.chunking.chunk_pages(pages, source_file=source_file)

        document = self.documents.create_document(
            created_by=current_user.id,
            title=title or source_file,
            source_type="pdf_upload",
            source_url=None,
            file_name=source_file,
        )

        for batch_start in range(0, len(chunks), 32):
            batch = chunks[batch_start : batch_start + 32]
            embeddings = await self.embedding_client.embed_passages([chunk.content for chunk in batch])
            for offset, (chunk, embedding) in enumerate(zip(batch, embeddings), start=batch_start):
                self.documents.add_chunk(
                    document_id=document.id,
                    chunk_index=offset,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    embedding=embedding,
                    source_chunk_id=f"{document.id}_{offset:04d}",
                    metadata=chunk.metadata,
                )

        self.db.commit()
        return DocumentUploadResponse(
            id=document.id,
            title=document.title,
            source_type=document.source_type,
            source_url=document.source_url,
            file_name=document.file_name,
            status=document.status,
            chunk_count=len(chunks),
            message=f"Uploaded and embedded {len(chunks)} chunks",
        )
