"""Structured logging configuration for isminet."""

import logging
import sys
from pathlib import Path
from typing import Any, Callable, List, MutableMapping

import structlog
from rich.console import Console

console = Console()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)


def get_log_file_path(development_mode: bool) -> str:
    """Get the appropriate log file path based on mode."""
    return str(LOG_DIR / ("dev.log" if development_mode else "prod.log"))


def setup_logging(
    level: str = "INFO",
    development_mode: bool = False,
    log_to_file: bool = True,
) -> None:
    """Configure structured logging for the application.

    Args:
        level: The logging level to use (default: INFO)
        development_mode: Whether to use pretty printing for development (default: False)
        log_to_file: Whether to log to a file in addition to stdout (default: True)
    """
    # Convert string level to logging level
    log_level = getattr(logging, level.upper())

    # Create handlers
    handlers: List[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_to_file:
        log_file = get_log_file_path(development_mode)
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)

    # Set up standard logging
    logging.basicConfig(
        format="%(message)s",
        handlers=handlers,
        level=log_level,
        force=True,  # Reset any existing configuration
    )

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

    if development_mode:
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
        level=level,
        development_mode=development_mode,
        log_to_file=log_to_file,
        log_file=get_log_file_path(development_mode) if log_to_file else None,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance for the given name.

    Args:
        name: The name of the logger (usually __name__)

    Returns:
        A structured logger instance
    """
    return structlog.get_logger(name)
