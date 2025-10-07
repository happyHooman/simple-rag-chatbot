"""Authentication module for FastAPI endpoints."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...config import settings
from ...config.logging_config import get_logger

logger = get_logger(__name__)

# OAuth2 scheme for token authentication
security = HTTPBearer(auto_error=False)


def get_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    """
    Validate authentication token.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        str: Valid token

    Raises:
        HTTPException: If token is invalid or missing
    """
    # In development mode, skip authentication
    if settings.DEBUG:
        logger.info("Development mode: Skipping authentication")
        return "dev_token"

    # Check if credentials are provided
    if not credentials:
        logger.warning("Authentication failed: No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get token from credentials
    token = credentials.credentials

    # Simple token validation (in production, use proper JWT validation)
    valid_tokens = settings.VALID_TOKENS.split(",")

    if token not in valid_tokens:
        logger.warning("Authentication failed: Invalid token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Authentication successful for token: {token[:8]}...")
    return token


def get_optional_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str | None:
    """
    Get token if provided, but don't require authentication.
    Useful for endpoints that can work with or without authentication.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        Optional[str]: Token if valid, None if not provided or invalid
    """
    if not credentials:
        return None

    try:
        return get_token(credentials)
    except HTTPException:
        return None
