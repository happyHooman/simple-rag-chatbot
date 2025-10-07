"""Custom exceptions and error handling for the application."""
from typing import Any


class BaseAPIException(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Raised when validation fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, status_code=422, details=details)


class NotFoundError(BaseAPIException):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None):
        super().__init__(message, status_code=404, details=details)


class UnauthorizedError(BaseAPIException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized", details: dict[str, Any] | None = None):
        super().__init__(message, status_code=401, details=details)


class ForbiddenError(BaseAPIException):
    """Raised when access is forbidden."""

    def __init__(self, message: str = "Forbidden", details: dict[str, Any] | None = None):
        super().__init__(message, status_code=403, details=details)


class InternalServerError(BaseAPIException):
    """Raised for internal server errors."""

    def __init__(self, message: str = "Internal server error", details: dict[str, Any] | None = None):
        super().__init__(message, status_code=500, details=details)
