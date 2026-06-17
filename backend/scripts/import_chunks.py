import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import get_settings
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.vector import vector_literal
from app.infrastructure.external.jina import JinaEmbeddingClient

settings = get_settings()


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return Path.cwd() / path


def batched(items: list[Any], batch_size: int):
    for index in range(0, len(items), batch_size):
        yield items[index : index + batch_size]


def apply_schema_if_requested(db, schema_path: Path) -> None:
    statements = [
        statement.strip()
        for statement in schema_path.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]
    for statement in statements:
        db.execute(text(statement))
    db.commit()


def delete_imported_documents(db) -> None:
    db.execute(
        text(
            """
            delete from documents
            where source_type = 'imported_json'
            """
        )
    )
    db.commit()


def create_document(db, title: str, metadata: dict[str, Any]):
    existing = db.execute(
        text(
            """
            select id
            from documents
            where title = :title and source_type = 'imported_json'
            limit 1
            """
        ),
        {"title": title},
    ).scalar_one_or_none()

    if existing:
        return existing, False

    document_id = db.execute(
        text(
            """
            insert into documents (title, source_type, file_name, metadata)
            values (:title, 'imported_json', :file_name, cast(:metadata as jsonb))
            returning id
            """
        ),
        {
            "title": title,
            "file_name": metadata.get("source_file"),
            "metadata": json.dumps(metadata, ensure_ascii=False),
        },
    ).scalar_one()
    db.commit()
    return document_id, True


def insert_chunk(db, document_id, chunk: dict[str, Any], chunk_index: int, embedding: list[float]) -> None:
    metadata = chunk.get("metadata", {})
    db.execute(
        text(
            """
            insert into document_chunks (
              document_id, chunk_index, content, page_number, section_title, source_chunk_id, metadata, token_count, embedding
            )
            values (
              :document_id, :chunk_index, :content, :page_number, :section_title, :source_chunk_id, cast(:metadata as jsonb), :token_count, cast(:embedding as vector)
            )
            on conflict (document_id, chunk_index) do nothing
            """
        ),
        {
            "document_id": document_id,
            "chunk_index": int(metadata.get("chunk_index") or chunk_index),
            "content": chunk["text"],
            "page_number": metadata.get("page_start"),
            "section_title": metadata.get("current_heading") or metadata.get("section"),
            "source_chunk_id": chunk.get("id"),
            "metadata": json.dumps(metadata, ensure_ascii=False),
            "token_count": len(chunk["text"].split()),
            "embedding": vector_literal(embedding),
        },
    )


async def import_chunks(args) -> None:
    chunks_path = resolve_path(args.chunks)
    chunks = json.loads(chunks_path.read_text(encoding="utf-8-sig"))
    if args.limit:
        chunks = chunks[: args.limit]

    db = SessionLocal()
    try:
        if args.apply_schema:
            apply_schema_if_requested(db, Path("app/infrastructure/db/schema.sql"))

        if args.replace:
            delete_imported_documents(db)

        by_source: dict[str, list[dict[str, Any]]] = {}
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            source = metadata.get("source_file") or "Imported Campus Document"
            by_source.setdefault(source, []).append(chunk)

        embedding_client = JinaEmbeddingClient()
        total_chunks = 0

        for source_title, source_chunks in by_source.items():
            first_metadata = source_chunks[0].get("metadata", {})
            document_id, created = create_document(db, source_title, first_metadata)
            if not created and not args.replace:
                print(f"Skipping existing document: {source_title}")
                continue

            for batch in batched(source_chunks, args.batch_size):
                embeddings = await embedding_client.embed_passages([item["text"] for item in batch])
                for offset, (chunk, embedding) in enumerate(zip(batch, embeddings), start=1):
                    insert_chunk(db, document_id, chunk, total_chunks + offset, embedding)
                total_chunks += len(batch)
                db.commit()
                print(f"Imported {total_chunks}/{len(chunks)} chunks")

        print(f"Done. Imported {total_chunks} chunks from {chunks_path}")
    finally:
        db.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Import campus chunks into Supabase pgvector")
    parser.add_argument("--chunks", default=settings.chunks_dataset_path, help="Path to chunks.json")
    parser.add_argument("--batch-size", type=int, default=32, help="Jina embedding batch size")
    parser.add_argument("--limit", type=int, default=0, help="Import only the first N chunks")
    parser.add_argument("--replace", action="store_true", help="Delete previous imported_json documents first")
    parser.add_argument("--apply-schema", action="store_true", help="Apply schema.sql before import")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(import_chunks(parse_args()))
