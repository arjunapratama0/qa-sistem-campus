from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.application.services.qa_service import QAService
from app.domain.retrieval import RetrievedChunk


class FakeEmbeddingClient:
    async def embed_query(self, text):
        return [0.1] * 1024


class FakeLLMClient:
    async def generate_answer(self, question, chunks):
        return "Jawaban dari LLM gratis berdasarkan sumber."


class FakeChunkRepository:
    def search_by_embedding(self, embedding, limit):
        return [
            RetrievedChunk(
                id=uuid4(),
                document_id=uuid4(),
                document_title="Pedoman Akademik",
                content="Mahasiswa dengan IPS lebih dari 3,50 dapat mengambil maksimal 24 SKS.",
                page_number=10,
                section_title="Beban Studi",
                similarity_score=0.82,
            )
        ]


@dataclass
class FakeHistory:
    id: object
    created_at: datetime


class FakeHistoryRepository:
    def create_with_citations(self, **kwargs):
        return FakeHistory(id=uuid4(), created_at=datetime.now(UTC))


class FakeDB:
    def commit(self):
        pass

    def refresh(self, item):
        pass


@dataclass
class FakeUser:
    id: object


@pytest.mark.asyncio
async def test_qa_service_returns_llm_answer_and_citations():
    service = QAService(FakeDB(), embedding_client=FakeEmbeddingClient(), llm_client=FakeLLMClient())
    service.chunks = FakeChunkRepository()
    service.histories = FakeHistoryRepository()

    response = await service.ask("Berapa maksimal SKS?", FakeUser(id=uuid4()))

    assert response.answer == "Jawaban dari LLM gratis berdasarkan sumber."
    assert response.citations
    assert response.confidence_score > 0
