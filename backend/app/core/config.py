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
    access_token_expire_minutes: int = Field(default=15, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")

    frontend_origin: str | AnyHttpUrl = Field(
        default="http://localhost:5173",
        validation_alias="FRONTEND_ORIGIN",
    )
    trusted_hosts: str = Field(default="localhost,127.0.0.1,testserver", validation_alias="TRUSTED_HOSTS")

    jina_api_key: str | None = Field(default=None, validation_alias="JINA_API_KEY")
    jina_embedding_url: str = "https://api.jina.ai/v1/embeddings"
    jina_embedding_model: str = "jina-embeddings-v3"
    jina_embedding_dimensions: int = 1024

    llm_provider: str = Field(default="groq", validation_alias="LLM_PROVIDER")
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", validation_alias="GROQ_BASE_URL")
    groq_model: str = Field(default="llama-3.1-8b-instant", validation_alias="GROQ_MODEL")

    retrieval_top_k: int = 5
    retrieval_min_similarity: float = 0.2
    chunk_target_words: int = Field(default=450, validation_alias="CHUNK_TARGET_WORDS")
    chunk_overlap_words: int = Field(default=80, validation_alias="CHUNK_OVERLAP_WORDS")
    pdf_max_upload_mb: int = Field(default=20, validation_alias="PDF_MAX_UPLOAD_MB")
    pdf_enable_ocr: bool = Field(default=False, validation_alias="PDF_ENABLE_OCR")
    rate_limit_auth_per_minute: int = Field(default=10, validation_alias="RATE_LIMIT_AUTH_PER_MINUTE")
    rate_limit_qa_per_minute: int = Field(default=30, validation_alias="RATE_LIMIT_QA_PER_MINUTE")
    qa_dataset_path: str = Field(default="data/qa_dataset_rag.json", validation_alias="QA_DATASET_PATH")
    chunks_dataset_path: str = Field(default="data/chunks.json", validation_alias="CHUNKS_DATASET_PATH")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8-sig", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_frontend_origins() -> list[str]:
    return [origin.strip() for origin in str(get_settings().frontend_origin).split(",") if origin.strip()]


def get_trusted_hosts() -> list[str]:
    return [host.strip() for host in get_settings().trusted_hosts.split(",") if host.strip()]
