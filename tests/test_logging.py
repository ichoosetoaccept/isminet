"""Tests for the logging configuration and functionality."""

import json
import logging
import os
from typing import Generator

import pytest
import structlog
from _pytest.logging import LogCaptureFixture

from isminet.logging import setup_logging, get_logger


@pytest.fixture(autouse=True)
def configure_logging() -> None:
    """Configure logging before each test."""
    # Reset structlog's configuration before each test
    structlog.reset_defaults()


@pytest.fixture
def env_setup() -> Generator[None, None, None]:
    """Set up and tear down environment variables for testing."""
    old_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def log_output(caplog: LogCaptureFixture) -> LogCaptureFixture:
    """Fixture to capture log output."""
    caplog.set_level(logging.DEBUG)
    return caplog


def test_logger_initialization(
    env_setup: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test basic logger initialization."""
    setup_logging(level="INFO", development_mode=False)
    logger = get_logger("test")

    # Verify the logger works by making a log call
    test_message = "test initialization"
    logger.info(test_message)

    # Check that the log message was formatted correctly
    captured = capsys.readouterr()
    log_entry = json.loads(captured.out)

    assert log_entry["event"] == test_message
    assert log_entry["level"] == "info"
    assert "timestamp" in log_entry
    assert log_entry["logger"] == "test"  # Verify logger name is set correctly


def test_development_mode_logging(
    env_setup: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test logging in development mode with pretty printing."""
    setup_logging(level="DEBUG", development_mode=True)
    logger = get_logger("test")

    test_message = "test debug message"
    logger.debug(test_message)

    captured = capsys.readouterr()
    assert test_message in captured.out
    assert "\x1b[" in captured.out  # ANSI color codes should be present


def test_production_mode_logging(
    env_setup: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test logging in production mode with JSON output."""
    setup_logging(level="INFO", development_mode=False)
    logger = get_logger("test")

    test_message = "test info message"
    logger.info(test_message)

    captured = capsys.readouterr()
    log_entry = json.loads(captured.out)
    assert log_entry["event"] == test_message
    assert log_entry["level"] == "info"
    assert "timestamp" in log_entry


def test_log_level_filtering(
    env_setup: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that log level filtering works correctly."""
    setup_logging(level="INFO", development_mode=False)
    logger = get_logger("test")

    debug_message = "debug message"
    info_message = "info message"

    logger.debug(debug_message)
    logger.info(info_message)

    captured = capsys.readouterr()
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]

    # Debug message should be filtered out
    assert len(log_entries) == 1
    assert log_entries[0]["event"] == info_message


def test_structured_logging_context(
    env_setup: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that structured logging context is included in log messages."""
    setup_logging(level="INFO", development_mode=False)
    logger = get_logger("test")

    context = {"user": "test_user", "action": "test_action"}
    logger.info("test message with context", **context)

    captured = capsys.readouterr()
    log_entry = json.loads(captured.out)

    assert log_entry["user"] == "test_user"
    assert log_entry["action"] == "test_action"


def test_environment_variable_integration(
    env_setup: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that environment variables properly configure logging."""
    os.environ["ISMINET_LOG_LEVEL"] = "DEBUG"
    os.environ["ISMINET_DEV_MODE"] = "1"

    # Re-initialize logging with environment variables
    setup_logging(
        level=os.getenv("ISMINET_LOG_LEVEL", "INFO"),
        development_mode=os.getenv("ISMINET_DEV_MODE", "0").lower() in ("1", "true"),
    )

    logger = get_logger("test")
    test_message = "test debug message"
    logger.debug(test_message)

    captured = capsys.readouterr()
    assert test_message in captured.out
    assert "\x1b[" in captured.out  # ANSI color codes should be present


def test_error_logging_with_exception(
    env_setup: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that exceptions are properly logged with context."""
    setup_logging(level="INFO", development_mode=False)
    logger = get_logger("test")

    try:
        raise ValueError("test error")
    except ValueError as e:
        logger.error("error occurred", error=str(e))

    captured = capsys.readouterr()
    log_entry = json.loads(captured.out)

    assert log_entry["event"] == "error occurred"
    assert log_entry["error"] == "test error"
    assert log_entry["level"] == "error"
