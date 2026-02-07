import logging
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()


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