"""
FastAPI authentication dependencies for JWT verification
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.auth.jwt_handler import JWTHandler
from src.config import get_settings


# Security scheme for Swagger UI
security = HTTPBearer()

# Get settings
settings = get_settings()

# Initialize JWT handler
jwt_handler = JWTHandler(
    secret_key=settings.BETTER_AUTH_SECRET,
    algorithm=settings.JWT_ALGORITHM
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Dependency to extract and verify current user from JWT token

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        User ID from verified token

    Raises:
        HTTPException: 401 if token is invalid or missing
    """
    token = credentials.credentials
    payload = jwt_handler.verify_token(token)
    user_id = jwt_handler.extract_user_id(payload)
    return user_id
