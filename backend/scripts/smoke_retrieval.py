import argparse
import asyncio
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.external.jina import JinaEmbeddingClient
from app.infrastructure.repositories.chunks import ChunkRepository


async def run(question: str, top_k: int) -> None:
    db = SessionLocal()
    try:
        embedding = await JinaEmbeddingClient().embed_query(question)
        chunks = ChunkRepository(db).search_by_embedding(embedding, top_k)
        print(f"Retrieved {len(chunks)} chunks")
        for index, chunk in enumerate(chunks, start=1):
            section = (chunk.section_title or "").replace("\n", " ")[:90]
            print(f"{index}. score={chunk.similarity_score:.4f} page={chunk.page_number} section={section}")
            print(f"   source={chunk.document_title}")
    finally:
        db.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Smoke test Jina embedding and pgvector retrieval")
    parser.add_argument("--question", default="Berapa maksimal SKS jika IPS 3.6?")
    parser.add_argument("--top-k", type=int, default=3)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run(args.question, args.top_k))
