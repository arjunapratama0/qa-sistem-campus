import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings

settings = get_settings()


class JinaEmbeddingClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.jina_api_key

    async def embed_query(self, text: str) -> list[float]:
        return await self._embed([text], task="retrieval.query")

    async def embed_passage(self, text: str) -> list[float]:
        return await self._embed([text], task="retrieval.passage")

    async def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return await self._embed_many(texts, task="retrieval.passage")

    async def _embed(self, texts: list[str], task: str) -> list[float]:
        embeddings = await self._embed_many(texts, task=task)
        return embeddings[0]

    async def _embed_many(self, texts: list[str], task: str) -> list[list[float]]:
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="JINA_API_KEY is not configured",
            )

        payload = {
            "model": settings.jina_embedding_model,
            "task": task,
            "dimensions": settings.jina_embedding_dimensions,
            "input": texts,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(settings.jina_embedding_url, json=payload, headers=headers)

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Embedding provider request failed",
            )

        data = response.json()
        return [item["embedding"] for item in data["data"]]

