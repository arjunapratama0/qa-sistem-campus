import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("TRUSTED_HOSTS", "testserver,localhost,127.0.0.1")
os.environ.setdefault("JINA_API_KEY", "")
os.environ.setdefault("GROQ_API_KEY", "")

