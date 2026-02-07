import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config import CORSConfig

from src.config import LOG_LEVEL


def setup_logging():
    """
    Set up logging configuration
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

    # Create console handler and set level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


def log_cors_configuration(config: "CORSConfig"):
    """
    Log CORS configuration at application startup

    Args:
        config: CORSConfig instance with CORS settings
    """
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("CORS Configuration")
    logger.info("=" * 60)

    if config.allow_origins:
        logger.info(f"Allowed Origins ({len(config.allow_origins)}):")
        for origin in config.allow_origins:
            logger.info(f"  - {origin}")
    else:
        logger.warning("No origins configured - cross-origin requests will be blocked!")

    logger.info(f"Allow Credentials: {config.allow_credentials}")
    logger.info(f"Allowed Methods: {', '.join(config.allow_methods)}")
    logger.info(f"Allowed Headers: {', '.join(config.allow_headers)}")
    logger.info(f"Preflight Cache: {config.max_age} seconds")
    logger.info("=" * 60)
