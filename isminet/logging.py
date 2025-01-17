"""Structured logging configuration for isminet."""

import logging
import sys
from typing import Any, Callable, MutableMapping

import structlog
from rich.console import Console

console = Console()


def setup_logging(
    level: str = "INFO",
    development_mode: bool = False,
) -> None:
    """Configure structured logging for the application.

    Args:
        level: The logging level to use (default: INFO)
        development_mode: Whether to use pretty printing for development (default: False)
    """
    # Convert string level to logging level
    log_level = getattr(logging, level.upper())

    # Set up standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
        force=True,  # Reset any existing configuration
    )

    # Configure processors for structlog
    shared_processors: list[Callable[[Any, str, MutableMapping[str, Any]], Any]] = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.filter_by_level,  # Add level filtering
        structlog.stdlib.add_logger_name,  # Add logger name
        structlog.contextvars.merge_contextvars,
    ]

    if development_mode:
        # Add pretty printing for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
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


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance for the given name.

    Args:
        name: The name of the logger (usually __name__)

    Returns:
        A structured logger instance
    """
    return structlog.get_logger(name)
