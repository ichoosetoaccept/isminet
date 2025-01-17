"""Structured logging configuration for isminet."""

import logging
import sys
from pathlib import Path
from typing import Any, Callable, List, MutableMapping

import structlog
from rich.console import Console

from .settings import Settings

console = Console()


def setup_logging() -> None:
    """Configure structured logging for the application.

    Uses settings from the central configuration:
    - settings.log_level: The logging level to use
    - settings.development_mode: Whether to use pretty printing
    - settings.log_to_file: Whether to log to file
    """
    # Reload settings to pick up environment variable changes
    settings = Settings()

    # Convert string level to logging level
    log_level = getattr(logging, settings.log_level.upper())

    # Create handlers
    handlers: List[logging.Handler] = []

    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    handlers.append(console_handler)

    # Configure file handler if enabled
    if settings.log_to_file:
        log_file = settings.get_log_file_path()
        # Create logs directory if it doesn't exist
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        handlers.append(file_handler)

    # Set up standard logging
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add our handlers
    for handler in handlers:
        root_logger.addHandler(handler)

    # Configure processors for structlog
    shared_processors: list[Callable[[Any, str, MutableMapping[str, Any]], Any]] = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.filter_by_level,  # Add level filtering
        structlog.stdlib.add_logger_name,  # Add logger name
        structlog.contextvars.merge_contextvars,
    ]

    if settings.development_mode:
        # Use a more readable format for development
        processors = shared_processors + [
            # Add colors and format for better readability
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
                # More readable format for development
                pad_event=50,
                repr_native_str=False,
            ),
        ]
    else:
        # Use JSON formatting for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,  # Use stdlib logger
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),  # Use stdlib logger factory
        cache_logger_on_first_use=True,
    )

    # Log initial configuration
    logger = get_logger(__name__)
    logger.info(
        "logging_configured",
        level=settings.log_level,
        development_mode=settings.development_mode,
        log_to_file=settings.log_to_file,
        log_file=settings.get_log_file_path() if settings.log_to_file else None,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance for the given name.

    Args:
        name: The name of the logger (usually __name__)

    Returns:
        A structured logger instance
    """
    return structlog.get_logger(name)
