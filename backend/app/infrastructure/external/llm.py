import httpx

from app.core.config import get_settings
from app.domain.retrieval import RetrievedChunk

settings = get_settings()


class FreeLLMClient:
    async def generate_answer(self, question: str, chunks: list[RetrievedChunk]) -> str | None:
        if settings.llm_provider.lower() != "groq" or not chunks or not settings.groq_api_key:
            return None

        context = "\n\n".join(
            f"[Sumber {index}] {chunk.content[:1200]}" for index, chunk in enumerate(chunks[:5], start=1)
        )
        payload = {
            "model": settings.groq_model,
            "temperature": 0.2,
            "max_tokens": 700,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah asisten akademik kampus. Jawab hanya berdasarkan konteks sumber. "
                        "Jika konteks tidak cukup, katakan sumber belum cukup. "
                        "Jangan mengarang. Gunakan bahasa Indonesia yang jelas dan ringkas."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Konteks:\n{context}\n\nPertanyaan: {question}",
                },
            ],
        }
        headers = {"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{settings.groq_base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    headers=headers,
                )
            response.raise_for_status()
        except Exception:
            return None

        answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return answer or None
