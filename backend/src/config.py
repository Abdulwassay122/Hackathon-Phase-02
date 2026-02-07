import logging
import os
from dotenv import load_dotenv

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