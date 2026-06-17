from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, documents, history, qa
from app.core.config import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="AI-powered campus question answering API",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(settings.frontend_origin)],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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

