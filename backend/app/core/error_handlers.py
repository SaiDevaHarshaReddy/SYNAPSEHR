"""Global exception handlers for the application."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import structlog

from app.core.exceptions import AppException

logger = structlog.get_logger()


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.error(
            "app_exception",
            exception_type=type(exc).__name__,
            message=exc.message,
            status_code=exc.status_code,
            detail=exc.detail,
            request_id=getattr(request.state, "request_id", None),
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": type(exc).__name__,
                    "message": exc.message,
                    "request_id": getattr(request.state, "request_id", None),
                    "detail": exc.detail,
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            exception_type=type(exc).__name__,
            message=str(exc),
            request_id=getattr(request.state, "request_id", None),
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "request_id": getattr(request.state, "request_id", None),
                },
            },
        )
