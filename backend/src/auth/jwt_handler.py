"""
JWT Handler for token verification and user identity extraction
"""
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from typing import Dict, Optional


class JWTHandler:
    """
    Handles JWT token verification and user identity extraction
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize JWT handler with secret key and algorithm

        Args:
            secret_key: Secret key for JWT signature verification
            algorithm: Algorithm used for JWT signing (default: HS256)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(self, user_id: int, email: str) -> str:
        """
        Generate a JWT access token for a user.

        Args:
            user_id: User's unique identifier
            email: User's email address

        Returns:
            Encoded JWT token string

        Example:
            >>> handler = JWTHandler(secret_key="secret", algorithm="HS256")
            >>> token = handler.create_access_token(user_id=1, email="user@example.com")
            >>> print(token)
            eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
        """
        # Create token payload with required claims
        payload = {
            "sub": str(user_id),  # Subject claim (user ID as string)
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=24)  # Expiration (24 hours)
        }

        # Encode and return the token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Dict:
        """
        Verify JWT token signature and expiration

        Args:
            token: JWT token string

        Returns:
            Dict containing decoded token payload

        Raises:
            HTTPException: 401 if token is invalid or expired
        """
        try:
            # T049: Add clock skew tolerance (leeway) for time synchronization issues
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "require": ["exp", "sub"]
                },
                leeway=10  # Allow 10 seconds clock skew tolerance
            )
            return payload
        except jwt.ExpiredSignatureError:
            # T048: Proper error handling for ExpiredSignatureError
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"}
            )

    def extract_user_id(self, payload: Dict) -> int:
        """
        Extract user ID from token payload

        Args:
            payload: Decoded JWT token payload

        Returns:
            User ID as integer

        Raises:
            HTTPException: 401 if user ID cannot be extracted
        """
        # Try standard 'sub' claim first
        user_id = payload.get("sub")

        # Try nested format if standard format not found
        if not user_id and "user" in payload:
            user_id = payload["user"].get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user identifier"
            )

        # Convert to integer if it's a string
        try:
            return int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user identifier format"
            )
