import logging
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()


@dataclass
class CORSConfig:
    """CORS configuration for FastAPI application"""

    # Origins allowed to make cross-origin requests
    allow_origins: List[str]

    # Whether to allow credentials (cookies, Authorization header)
    allow_credentials: bool = True

    # HTTP methods allowed for cross-origin requests
    allow_methods: List[str] = None

    # Request headers allowed in cross-origin requests
    allow_headers: List[str] = None

    # Response headers exposed to browser JavaScript
    expose_headers: List[str] = None

    # Preflight cache duration in seconds
    max_age: int = 600

    def __post_init__(self):
        """Set default values for list fields"""
        if self.allow_methods is None:
            self.allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        if self.allow_headers is None:
            self.allow_headers = ["Authorization", "Content-Type"]

        if self.expose_headers is None:
            self.expose_headers = []


def validate_origin(origin: str) -> tuple[bool, str]:
    """
    Validate a CORS origin URL.

    Args:
        origin: The origin URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    from urllib.parse import urlparse

    # Check for empty/whitespace
    if not origin or origin.isspace():
        return False, "Origin is empty or whitespace-only"

    # Check for wildcard (not allowed per spec)
    if origin == "*":
        return False, "Wildcard origin (*) not allowed per security policy"

    # Check for protocol
    if not origin.startswith(("http://", "https://")):
        return False, f"Origin must start with http:// or https://, got: {origin}"

    # Check for trailing slash
    if origin.endswith("/"):
        return False, f"Origin must not end with trailing slash: {origin}"

    # Validate URL structure
    try:
        parsed = urlparse(origin)
        if not parsed.netloc:
            return False, f"Invalid origin URL structure: {origin}"
    except Exception as e:
        return False, f"Failed to parse origin URL: {e}"

    return True, ""


def parse_cors_origins(origins_str: str) -> List[str]:
    """
    Parse and validate CORS origins from environment variable.

    Args:
        origins_str: Comma-separated list of origin URLs

    Returns:
        List of valid origin URLs
    """
    logger = logging.getLogger(__name__)

    if not origins_str:
        logger.warning("CORS_ORIGINS environment variable not set. No origins will be allowed.")
        return []

    # Split and strip
    raw_origins = [origin.strip() for origin in origins_str.split(",")]

    # Validate each origin
    valid_origins = []
    for origin in raw_origins:
        if not origin:
            continue

        is_valid, error_msg = validate_origin(origin)
        if is_valid:
            valid_origins.append(origin)
            logger.info(f"CORS: Allowed origin: {origin}")
        else:
            logger.warning(f"CORS: Invalid origin skipped: {origin} - {error_msg}")

    if not valid_origins:
        logger.warning("CORS: No valid origins configured. Cross-origin requests will be blocked.")

    return valid_origins


def get_cors_origins() -> List[str]:
    """
    Load and parse CORS origins from environment variable.

    Returns:
        List of valid origin URLs
    """
    origins_str = os.getenv("CORS_ORIGINS", "")
    return parse_cors_origins(origins_str)


def get_cors_config() -> CORSConfig:
    """
    Get complete CORS configuration.

    Returns:
        CORSConfig instance with all settings
    """
    return CORSConfig(
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=[],
        max_age=600,
    )


def get_env_variable(var_name: str, default_value: str = None) -> str:
    """
    Get environment variable or return default value
    """
    value = os.getenv(var_name, default_value)
    if value is None:
        raise ValueError(f"Environment variable {var_name} not set")
    return value


# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# JWT Authentication configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


class Settings(BaseModel):
    """Application settings"""
    DATABASE_URL: str
    LOG_LEVEL: str
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str

    class Config:
        frozen = True


def get_settings() -> Settings:
    """
    Get application settings with validation

    Raises:
        ValueError: If required settings are missing
    """
    # Validate JWT secret is set
    if not BETTER_AUTH_SECRET:
        raise ValueError(
            "BETTER_AUTH_SECRET environment variable must be set for JWT authentication. "
            "Please add it to your .env file."
        )

    # Validate secret length (minimum 32 bytes recommended for HS256)
    if len(BETTER_AUTH_SECRET) < 32:
        raise ValueError(
            "BETTER_AUTH_SECRET must be at least 32 characters long for security. "
            "Current length: {}".format(len(BETTER_AUTH_SECRET))
        )

    return Settings(
        DATABASE_URL=DATABASE_URL,
        LOG_LEVEL=LOG_LEVEL,
        BETTER_AUTH_SECRET=BETTER_AUTH_SECRET,
        JWT_ALGORITHM=JWT_ALGORITHM
    )