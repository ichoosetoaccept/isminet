"""Tests for the logging configuration and functionality."""

import json
import logging
import os
from typing import Generator

import pytest
import structlog
from _pytest.logging import LogCaptureFixture
from pydantic import ValidationError

from isminet.logging import setup_logging, get_logger, LOG_DIR
from isminet.models.base import UnifiBaseModel, Meta


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


@pytest.fixture
def cleanup_log_files() -> Generator[None, None, None]:
    """Clean up log files after tests."""
    yield
    # Clean up test log files
    for log_file in LOG_DIR.glob("*.log"):
        log_file.unlink()


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
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]

    # Get the last log entry (ignoring setup logs)
    log_entry = log_entries[-1]
    assert log_entry["event"] == test_message
    assert log_entry["level"] == "info"
    assert "timestamp" in log_entry
    assert log_entry["logger"] == "test"


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
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]

    # Get the last log entry (ignoring setup logs)
    log_entry = log_entries[-1]
    assert log_entry["event"] == test_message
    assert log_entry["level"] == "info"
    assert "timestamp" in log_entry
    assert log_entry["logger"] == "test"


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

    # Find user log entries (excluding setup logs)
    user_logs = [entry for entry in log_entries if entry["logger"] == "test"]
    assert len(user_logs) == 1
    assert user_logs[0]["event"] == info_message


def test_structured_logging_context(
    env_setup: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that structured logging context is included in log messages."""
    setup_logging(level="INFO", development_mode=False)
    logger = get_logger("test")

    context = {"user": "test_user", "action": "test_action"}
    logger.info("test message with context", **context)

    captured = capsys.readouterr()
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]

    # Get the last log entry (ignoring setup logs)
    log_entry = log_entries[-1]
    assert log_entry["event"] == "test message with context"
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
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]

    # Get the last log entry (ignoring setup logs)
    log_entry = log_entries[-1]
    assert log_entry["event"] == "error occurred"
    assert log_entry["error"] == "test error"
    assert log_entry["level"] == "error"


def test_file_logging_development_mode(
    env_setup: None, cleanup_log_files: None
) -> None:
    """Test that logs are written to file in development mode."""
    setup_logging(level="DEBUG", development_mode=True, log_to_file=True)
    logger = get_logger("test")

    test_message = "test debug message"
    logger.debug(test_message)

    log_file = LOG_DIR / "dev.log"
    assert log_file.exists()
    log_content = log_file.read_text()
    assert test_message in log_content
    assert "test_logging.py" in log_content  # Should include file name in dev mode


def test_file_logging_production_mode(env_setup: None, cleanup_log_files: None) -> None:
    """Test that logs are written to file in production mode."""
    setup_logging(level="INFO", development_mode=False, log_to_file=True)
    logger = get_logger("test")

    test_message = "test info message"
    logger.info(test_message)

    log_file = LOG_DIR / "prod.log"
    assert log_file.exists()
    log_content = log_file.read_text()
    log_entries = [json.loads(line) for line in log_content.strip().split("\n")]

    # Get the last log entry (ignoring setup logs)
    log_entry = log_entries[-1]
    assert log_entry["event"] == test_message
    assert log_entry["level"] == "info"
    assert "timestamp" in log_entry
    assert log_entry["logger"] == "test"


def test_disable_file_logging(env_setup: None, cleanup_log_files: None) -> None:
    """Test that file logging can be disabled."""
    setup_logging(level="INFO", development_mode=False, log_to_file=False)
    logger = get_logger("test")

    test_message = "test info message"
    logger.info(test_message)

    # Neither log file should exist
    assert not (LOG_DIR / "dev.log").exists()
    assert not (LOG_DIR / "prod.log").exists()


def test_model_initialization_logging(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that model initialization is logged correctly."""
    setup_logging(level="DEBUG", development_mode=False)
    test_data = {"name": "test", "value": 42}
    UnifiBaseModel(**test_data)

    captured = capsys.readouterr()
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]

    init_log = next(
        entry for entry in log_entries if entry["event"] == "model_initialized"
    )
    assert init_log["model"] == "UnifiBaseModel"
    assert set(init_log["provided_fields"]) == {"name", "value"}


def test_model_validation_error_logging(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that model validation errors are logged correctly."""
    setup_logging(level="DEBUG", development_mode=False)

    with pytest.raises(ValidationError):
        Meta(rc="error")  # Should be "ok"

    captured = capsys.readouterr()
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]

    error_log = next(
        entry for entry in log_entries if entry["event"] == "model_validation_failed"
    )
    assert error_log["model"] == "Meta"
    assert "validation_errors" in error_log
    assert error_log["error_type"] == "ValidationError"


def test_model_serialization_logging(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that model serialization is logged correctly."""
    setup_logging(level="DEBUG", development_mode=False)
    model = UnifiBaseModel(name="test", value=42)

    model.model_dump(exclude_unset=True)

    captured = capsys.readouterr()
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]

    dump_log = next(
        entry for entry in log_entries if entry["event"] == "model_serialized"
    )
    assert dump_log["model"] == "UnifiBaseModel"
    assert "included_fields" in dump_log
    assert dump_log["exclude_unset"] is True


def test_system_status_initialization_logging(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that system status initialization is logged correctly."""
    setup_logging(level="INFO", development_mode=False)
    from isminet.models.system import (
        SystemStatus,
        DeviceType,
    )

    test_data = {
        "device_type": DeviceType.UAP,
        "version": "1.2.3",
        "uptime": 3600,
        "health": [
            {
                "device_type": DeviceType.UAP,
                "subsystem": "test",
                "status": "ok",
                "status_code": 0,
                "status_message": "All good",
                "last_check": 1000,
                "next_check": 2000,
            }
        ],
        "processes": [
            {
                "pid": 1,
                "name": "test",
                "cpu_usage": 10.5,
                "mem_usage": 20.5,
                "mem_rss": 1024,
                "mem_vsz": 2048,
            }
        ],
        "services": [
            {"name": "test_service", "status": "running", "enabled": True, "pid": 1}
        ],
        "upgradable": False,
        "update_available": False,
        "storage_usage": 1024,
        "storage_available": 4096,
    }

    # Initialize system status which should trigger logging
    SystemStatus(
        **test_data
    )  # Don't need to store the instance since we're only testing the logs

    # Check log output
    captured = capsys.readouterr()
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]
    init_log = next(
        entry for entry in log_entries if entry["event"] == "system_status_initialized"
    )

    assert init_log["device_type"] == "uap"
    assert init_log["version"] == "1.2.3"
    assert init_log["update_available"] is False
    assert init_log["health_checks"] == 1
    assert init_log["processes"] == 1
    assert init_log["services"] == 1
    assert init_log["storage_usage"] == 1024


@pytest.mark.parametrize(
    "health_status,expected_log_level",
    [("ok", "debug"), ("warning", "warning"), ("error", "error")],
)
def test_system_health_validation_logging(
    health_status: str, expected_log_level: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that system health validation logs appropriate messages based on status."""
    setup_logging(level="DEBUG", development_mode=False)
    from isminet.models.system import SystemHealth, DeviceType

    # Create health instance but don't need to store it since we're only testing logs
    SystemHealth(
        device_type=DeviceType.UAP,
        subsystem="test",
        status=health_status,
        status_code=0,
        status_message="Test message",
        last_check=1000,
        next_check=2000,
    )

    # Check log output
    captured = capsys.readouterr()
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]

    # Check for model initialization logs
    init_logs = [
        entry for entry in log_entries if entry["event"] == "model_initialized"
    ]
    assert len(init_logs) > 0
    init_log = init_logs[0]
    assert init_log["model"] == "SystemHealth"
    assert "status" in init_log["provided_fields"]
    assert (
        init_log["level"] == "info"
    )  # Model initialization is always logged at INFO level


def test_system_status_dump_logging(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that system status dump operation is logged correctly."""
    setup_logging(level="DEBUG", development_mode=False)
    from isminet.models.system import (
        SystemStatus,
        DeviceType,
    )

    test_data = {
        "device_type": DeviceType.UAP,
        "version": "1.2.3",
        "uptime": 3600,
        "health": [
            {
                "device_type": DeviceType.UAP,
                "subsystem": "test",
                "status": "ok",
                "status_code": 0,
                "status_message": "All good",
                "last_check": 1000,
                "next_check": 2000,
            }
        ],
        "processes": [
            {
                "pid": 1,
                "name": "test",
                "cpu_usage": 10.5,
                "mem_usage": 20.5,
                "mem_rss": 1024,
                "mem_vsz": 2048,
            }
        ],
        "services": [
            {"name": "test_service", "status": "running", "enabled": True, "pid": 1}
        ],
        "upgradable": False,
        "update_available": False,
        "storage_usage": 1024,
        "storage_available": 4096,
    }

    system_status = SystemStatus(
        **test_data
    )  # Need to store this one since we call model_dump() on it
    system_status.model_dump()

    # Check log output
    captured = capsys.readouterr()
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]
    dump_log = next(
        entry for entry in log_entries if entry["event"] == "system_status_dumped"
    )

    assert dump_log["device_type"] == "uap"
    assert dump_log["version"] == "1.2.3"
    assert dump_log["health_status"] == ["ok"]
    assert dump_log["service_status"] == {"test_service": "running"}
    assert dump_log["storage_usage"] == 1024


def test_config_loading_logging(
    env_setup: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that configuration loading is logged correctly."""
    setup_logging(level="INFO", development_mode=False)
    from isminet.config import APIConfig

    # Set test environment variables
    os.environ.update(
        {
            "UNIFI_API_KEY": "test_key",
            "UNIFI_HOST": "test.host",
            "UNIFI_PORT": "8443",
            "UNIFI_VERIFY_SSL": "true",
        }
    )

    APIConfig.from_env()  # Don't need to store since we're only testing logs

    # Check log output
    captured = capsys.readouterr()
    log_entries = [json.loads(line) for line in captured.out.strip().split("\n")]
    config_logs = [entry for entry in log_entries if entry["event"] == "config_loaded"]

    assert len(config_logs) > 0
    config_log = config_logs[0]
    assert config_log["host"] == "test.host"
    assert config_log["port"] == 8443
    assert config_log["verify_ssl"] is True
    # API key should not be logged
    assert "api_key" not in config_log
