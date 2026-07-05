"""SynapseHR Backend - Main Application Entry Point."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.constants import APP_DESCRIPTION, APP_TITLE, APP_VERSION
from app.core.error_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.database.database import close_db, init_db
from app.middleware.logging import LoggingMiddleware
from app.middleware.performance import PerformanceMiddleware
from app.middleware.rate_limit import AIRateLimitMiddleware, RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.schemas.response import HealthResponse

settings = get_settings()

setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("application_startup", env=settings.APP_ENV)

    # Import all models to ensure they are registered with Base metadata
    import app.models.candidate  # noqa: F401

    # Initialize database
    await init_db()
    logger.info("database_initialized")

    # Initialize workflow engine
    from app.workflows.engine import initialize_workflows
    initialize_workflows()
    logger.info("workflows_initialized")

    yield

    # Cleanup
    await close_db()
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        lifespan=lifespan,
        docs_url="/api/docs" if settings.is_development else None,
        redoc_url="/api/redoc" if settings.is_development else None,
        openapi_url="/api/openapi.json" if settings.is_development else None,
    )

    # Register middleware (order matters - last registered = first executed)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(AIRateLimitMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Register routes
    app.include_router(api_router)

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        return HealthResponse(
            status="healthy",
            version=APP_VERSION,
            database="connected",
        )

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": APP_TITLE,
            "version": APP_VERSION,
            "status": "running",
            "docs": "/api/docs" if settings.is_development else None,
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.is_development,
    )
