"""Logging configuration."""

import logging
import sys
from typing import Optional
from rich.logging import RichHandler
from app.core.config import settings


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Setup structured logging for the application."""
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Only configure once
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    if settings.DEBUG:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
            datefmt="[%Y-%m-%d %H:%M:%S]",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    
    # Create console handler
    if sys.stderr.isatty():
        # Use Rich handler for terminal with colors
        handler = RichHandler(
            rich_tracebacks=True,
            show_path=False,
            show_time=False,
        )
        handler.setFormatter(formatter)
    else:
        # Use basic handler for non-TTY environments
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger