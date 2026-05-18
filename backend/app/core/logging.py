"""
Structured logging configuration.
"""

import logging
import sys

from app.core import get_settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
        if not settings.is_production
        else '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    )

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Quiet noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger for a module."""
    return logging.getLogger(f"parcelhub.{name}")
