from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handler import register_exception_handlers
from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as document_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import AppContextMiddleware

setup_logging(log_level="INFO" if settings.ENVIRONMENT == "production" else "DEBUG")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="A RAG-powered API for assisting students with course queries.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(AppContextMiddleware)

    register_exception_handlers(app)

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok", "environment": settings.ENVIRONMENT}

    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(document_router, prefix=settings.API_V1_STR)
    app.include_router(chat_router, prefix=settings.API_V1_STR)

    return app


app = create_app()