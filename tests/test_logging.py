"""Tests for logging configuration."""

import os
from typing import Generator

import pytest

from isminet.logging import setup_logging, get_logger
from isminet.settings import Settings

# Get LOG_DIR from settings
settings = Settings(unifi_api_key="test", unifi_host="test.host")
LOG_DIR = settings.LOG_DIR


@pytest.fixture(autouse=True)
def clean_env() -> Generator[None, None, None]:
    """Store and restore environment variables."""
    env_vars = [
        "ISMINET_LOG_LEVEL",
        "ISMINET_DEV_MODE",
        "ISMINET_LOG_TO_FILE",
    ]
    # Store original env vars
    original_vars = {key: os.environ.get(key) for key in env_vars}
    # Remove env vars
    for key in env_vars:
        os.environ.pop(key, None)
    yield
    # Restore original env vars
    for key, value in original_vars.items():
        if value is not None:
            os.environ[key] = value
        else:
            os.environ.pop(key, None)


def test_logger_initialization(capsys: pytest.CaptureFixture[str]) -> None:
    """Test basic logger initialization."""
    os.environ["ISMINET_LOG_LEVEL"] = "INFO"
    os.environ["ISMINET_DEV_MODE"] = "0"
    setup_logging()
    logger = get_logger("test")
    logger.info("Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_development_mode_logging(capsys: pytest.CaptureFixture[str]) -> None:
    """Test logging in development mode with pretty printing."""
    os.environ["ISMINET_LOG_LEVEL"] = "DEBUG"
    os.environ["ISMINET_DEV_MODE"] = "1"
    setup_logging()
    logger = get_logger("test")
    logger.debug("Debug message")
    captured = capsys.readouterr()
    assert "Debug message" in captured.out


def test_production_mode_logging(capsys: pytest.CaptureFixture[str]) -> None:
    """Test logging in production mode with JSON output."""
    os.environ["ISMINET_LOG_LEVEL"] = "INFO"
    os.environ["ISMINET_DEV_MODE"] = "0"
    setup_logging()
    logger = get_logger("test")
    logger.info("Production message")
    captured = capsys.readouterr()
    assert "Production message" in captured.out


def test_log_level_filtering(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that log level filtering works correctly."""
    os.environ["ISMINET_LOG_LEVEL"] = "INFO"
    os.environ["ISMINET_DEV_MODE"] = "0"
    setup_logging()
    logger = get_logger("test")
    logger.debug("Debug message")  # Should not appear
    logger.info("Info message")  # Should appear
    captured = capsys.readouterr()
    assert "Debug message" not in captured.out
    assert "Info message" in captured.out


def test_structured_logging_context(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that structured logging context is included in log messages."""
    os.environ["ISMINET_LOG_LEVEL"] = "INFO"
    os.environ["ISMINET_DEV_MODE"] = "0"
    setup_logging()
    logger = get_logger("test")
    logger = logger.bind(user_id="123", action="test")
    logger.info("Structured message")
    captured = capsys.readouterr()
    assert "user_id" in captured.out
    assert "action" in captured.out
    assert "Structured message" in captured.out


def test_environment_variable_integration(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that environment variables properly configure logging."""
    os.environ["ISMINET_LOG_LEVEL"] = "DEBUG"
    os.environ["ISMINET_DEV_MODE"] = "1"
    setup_logging()
    logger = get_logger("test")
    logger.debug("Debug message")
    captured = capsys.readouterr()
    assert "Debug message" in captured.out


def test_error_logging_with_exception(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that exceptions are properly logged with context."""
    os.environ["ISMINET_LOG_LEVEL"] = "INFO"
    os.environ["ISMINET_DEV_MODE"] = "0"
    setup_logging()
    logger = get_logger("test")
    try:
        raise ValueError("Test error")
    except ValueError:
        logger.exception("Error occurred")
    captured = capsys.readouterr()
    assert "Error occurred" in captured.out
    assert "ValueError: Test error" in captured.out


@pytest.fixture
def cleanup_log_files() -> Generator[None, None, None]:
    """Clean up log files after tests."""
    yield
    for file in ["dev.log", "prod.log"]:
        path = LOG_DIR / file
        if path.exists():
            path.unlink()


def test_file_logging_development_mode(cleanup_log_files: None) -> None:
    """Test that logs are written to file in development mode."""
    os.environ["ISMINET_LOG_LEVEL"] = "DEBUG"
    os.environ["ISMINET_DEV_MODE"] = "1"
    os.environ["ISMINET_LOG_TO_FILE"] = "1"
    setup_logging()
    logger = get_logger("test")
    logger.debug("File test message")
    log_file = LOG_DIR / "dev.log"
    assert log_file.exists()
    assert "File test message" in log_file.read_text()


def test_file_logging_production_mode(cleanup_log_files: None) -> None:
    """Test that logs are written to file in production mode."""
    os.environ["ISMINET_LOG_LEVEL"] = "INFO"
    os.environ["ISMINET_DEV_MODE"] = "0"
    os.environ["ISMINET_LOG_TO_FILE"] = "1"
    setup_logging()
    logger = get_logger("test")
    logger.info("Production file message")
    log_file = LOG_DIR / "prod.log"
    assert log_file.exists()
    assert "Production file message" in log_file.read_text()


def test_disable_file_logging(cleanup_log_files: None) -> None:
    """Test that file logging can be disabled."""
    os.environ["ISMINET_LOG_LEVEL"] = "INFO"
    os.environ["ISMINET_DEV_MODE"] = "0"
    os.environ["ISMINET_LOG_TO_FILE"] = "0"
    setup_logging()
    logger = get_logger("test")
    logger.info("Console only message")
    dev_log = LOG_DIR / "dev.log"
    prod_log = LOG_DIR / "prod.log"
    assert not dev_log.exists()
    assert not prod_log.exists()


# ... rest of the test file ...
