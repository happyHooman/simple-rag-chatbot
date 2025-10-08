"""Authentication module for FastAPI endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...config import settings
from ...config.logging_config import get_logger

logger = get_logger(__name__)

# OAuth2 scheme for token authentication
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (e.g., {"sub": "username"})
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    logger.debug(f"Created JWT token for subject: {data.get('sub', 'unknown')}")
    
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    """
    Validate JWT authentication token.

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

    # First, try simple token validation (for backward compatibility with tests)
    valid_tokens = settings.VALID_TOKENS.split(",")
    if token in valid_tokens:
        logger.info(f"Authentication successful with simple token: {token[:8]}...")
        return token

    # If not a simple token, try JWT validation
    payload = verify_token(token)
    
    # Log successful authentication
    subject = payload.get("sub", "unknown")
    logger.info(f"Authentication successful for JWT user: {subject}")
    
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
