"""Exception handlers for the FastAPI application."""
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ...config import settings
from ...config.logging_config import get_logger
from .exceptions import BaseAPIException

logger = get_logger(__name__)


def build_error_context(request: Request, exc: Exception, **overrides: Any) -> dict[str, Any]:
    """Build error context with request info and exception details."""
    context = {
        "url": str(request.url),
        "method": request.method,
        "exception_type": type(exc).__name__,
    }

    # Extract common exception attributes if they exist
    if hasattr(exc, "status_code"):
        context["status_code"] = exc.status_code
    if hasattr(exc, "detail"):
        context["detail"] = exc.detail
    if hasattr(exc, "message"):
        context["message"] = exc.message
    if hasattr(exc, "details"):
        context["details"] = exc.details

    # Override with any explicitly provided values
    context.update(overrides)
    return context


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""

    @app.exception_handler(BaseAPIException)
    async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
        """Handle custom API exceptions."""
        logger.error("API exception occurred", **build_error_context(request, exc))

        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "details": exc.details, "type": type(exc).__name__}
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTP exceptions."""
        logger.warning("HTTP exception occurred", **build_error_context(request, exc))

        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle Starlette HTTP exceptions."""
        logger.warning("Starlette HTTP exception occurred", **build_error_context(request, exc))

        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle request validation errors."""
        logger.warning("Validation error occurred", **build_error_context(request, exc, errors=exc.errors()))

        return JSONResponse(status_code=422, content={"error": "Validation error", "details": exc.errors()})

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error("Unexpected exception occurred", **build_error_context(
            request, exc, message=str(exc), exc_info=True
        ))

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred" if not settings.DEBUG else str(exc),
            },
        )
