from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Informant Campus"
    api_prefix: str = "/api/v1"
    environment: str = "development"

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/smart_informant",
        validation_alias="DATABASE_URL",
    )

    jwt_secret_key: str = Field(
        default="change-me-in-production",
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    frontend_origin: str | AnyHttpUrl = Field(
        default="http://localhost:5173",
        validation_alias="FRONTEND_ORIGIN",
    )

    jina_api_key: str | None = Field(default=None, validation_alias="JINA_API_KEY")
    jina_embedding_url: str = "https://api.jina.ai/v1/embeddings"
    jina_embedding_model: str = "jina-embeddings-v3"
    jina_embedding_dimensions: int = 1024

    retrieval_top_k: int = 5
    retrieval_min_similarity: float = 0.2
    qa_dataset_path: str = Field(default="data/qa_dataset_rag.json", validation_alias="QA_DATASET_PATH")
    chunks_dataset_path: str = Field(default="data/chunks.json", validation_alias="CHUNKS_DATASET_PATH")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
