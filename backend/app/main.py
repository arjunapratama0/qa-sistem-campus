from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routers import auth, documents, history, qa
from app.core.config import get_frontend_origins, get_settings, get_trusted_hosts
from app.core.middleware import InMemoryRateLimitMiddleware, SecurityHeadersMiddleware

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="AI-powered campus question answering API",
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(InMemoryRateLimitMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=get_trusted_hosts())
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_frontend_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(qa.router, prefix=settings.api_prefix)
    app.include_router(history.router, prefix=settings.api_prefix)
    app.include_router(documents.router, prefix=settings.api_prefix)

    @app.get("/")
    def root():
        return {"message": "Smart Informant Campus API", "docs": "/docs"}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
