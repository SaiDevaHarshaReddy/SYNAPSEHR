"""SynapseHR Backend - Main Application Entry Point."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

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
    print("STARTUP: Starting lifespan...", flush=True)
    logger.info("application_startup", env=settings.APP_ENV)

    # Import all models to ensure they are registered with Base metadata
    import app.models.candidate  # noqa: F401
    import app.models.hr_ticket  # noqa: F401
    print("STARTUP: Models imported.", flush=True)

    # Initialize database
    print("STARTUP: Initializing DB...", flush=True)
    try:
        await init_db()
        print("STARTUP: DB Initialized successfully.", flush=True)
        logger.info("database_initialized")
    except Exception as e:
        print(f"STARTUP DB ERROR: {e}", flush=True)
        raise

    # Initialize workflow engine
    print("STARTUP: Initializing workflows...", flush=True)
    try:
        from app.workflows.engine import initialize_workflows
        initialize_workflows()
        print("STARTUP: Workflows Initialized successfully.", flush=True)
        logger.info("workflows_initialized")
    except Exception as e:
        print(f"STARTUP WORKFLOW ERROR: {e}", flush=True)
        raise

    print("STARTUP: Lifespan setup complete.", flush=True)
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

     #Register middleware (order matters - last registered = first executed)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
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
