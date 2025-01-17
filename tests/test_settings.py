"""Tests for settings configuration."""

import os
from pathlib import Path
from typing import Any, Dict, Generator

import pytest
from pydantic import ValidationError

from isminet.settings import APIVersion, Settings


@pytest.fixture(autouse=True)  # Apply to all tests
def clean_env() -> Generator[None, None, None]:
    """Store and restore environment variables."""
    env_vars = [
        "UNIFI_API_KEY",
        "UNIFI_HOST",
        "UNIFI_PORT",
        "UNIFI_VERIFY_SSL",
        "UNIFI_TIMEOUT",
        "UNIFI_SITE",
        "UNIFI_API_VERSION",
        "ISMINET_LOG_LEVEL",
        "ISMINET_DEV_MODE",
        "ISMINET_LOG_TO_FILE",
    ]
    # Store original env vars
    original_vars = {key: os.environ.get(key) for key in env_vars}
    # Remove env vars to ensure .env values are used
    for key in env_vars:
        os.environ.pop(key, None)
    yield
    # Restore original env vars
    for key, value in original_vars.items():
        if value is not None:
            os.environ[key] = value
        else:
            os.environ.pop(key, None)


@pytest.fixture
def env_vars(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """Set up test environment variables that override .env values."""
    test_vars = request.param if hasattr(request, "param") else {}
    # Set test env vars
    for key, value in test_vars.items():
        os.environ[key] = str(value)
    yield
    # Clean up test env vars
    for key in test_vars:
        os.environ.pop(key, None)


def test_api_version_enum() -> None:
    """Test APIVersion enum."""
    assert APIVersion.V1.value == "v1"
    assert APIVersion.V2.value == "v2"
    assert APIVersion.V1.path == "/proxy/network/api"
    assert APIVersion.V2.path == "/proxy/network/api"


def test_current_env_file() -> None:
    """Test our actual .env file configuration."""
    settings = Settings()
    # Test values from our current .env file
    assert settings.log_level == "DEBUG"
    assert settings.development_mode is True
    assert settings.log_to_file is True
    assert settings.unifi_api_key == "TTYYGaprNuYRqheIyqdB8YOAD2QEVuBv"
    assert settings.unifi_host == "192.168.1.1"


@pytest.mark.parametrize(
    "env_vars,expected",
    [
        # Test production configuration
        (
            {
                "ISMINET_LOG_LEVEL": "INFO",
                "ISMINET_DEV_MODE": "0",
                "ISMINET_LOG_TO_FILE": "1",
                "UNIFI_API_KEY": "prod_key",
                "UNIFI_HOST": "prod.host",
                "UNIFI_VERIFY_SSL": "true",
            },
            {
                "log_level": "INFO",
                "development_mode": False,
                "log_to_file": True,
                "unifi_verify_ssl": True,
            },
        ),
        # Test minimal configuration
        (
            {
                "UNIFI_API_KEY": "min_key",
                "UNIFI_HOST": "min.host",
            },
            {
                "log_level": "DEBUG",  # From .env
                "development_mode": True,  # From .env
                "log_to_file": True,  # From .env
                "unifi_verify_ssl": False,  # Default
            },
        ),
        # Test development configuration with custom ports
        (
            {
                "ISMINET_LOG_LEVEL": "DEBUG",
                "ISMINET_DEV_MODE": "1",
                "UNIFI_API_KEY": "dev_key",
                "UNIFI_HOST": "dev.host",
                "UNIFI_PORT": "8443",
                "UNIFI_API_VERSION": "v2",
            },
            {
                "log_level": "DEBUG",
                "development_mode": True,
                "unifi_port": 8443,
                "unifi_api_version": APIVersion.V2,
            },
        ),
    ],
    indirect=["env_vars"],
)
def test_env_configurations(env_vars: None, expected: Dict[str, Any]) -> None:
    """Test different environment configurations."""
    settings = Settings()
    for key, value in expected.items():
        assert getattr(settings, key) == value


@pytest.mark.parametrize(
    "field,value,expected_error",
    [
        ("unifi_host", "", "Host cannot be empty"),
        ("unifi_api_key", "", "API key cannot be empty"),
        ("unifi_port", 0, "Port must be between 1 and 65535"),
        ("unifi_port", 65536, "Port must be between 1 and 65535"),
        ("test_port", 0, "Port must be between 1 and 65535"),
        ("test_port", 65536, "Port must be between 1 and 65535"),
        (
            "isminet_log_level",
            "INVALID",
            "Input should be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'",
        ),
    ],
)
def test_settings_validation(field: str, value: Any, expected_error: str) -> None:
    """Test settings validation."""
    # Base settings with required fields
    settings_dict: Dict[str, Any] = {
        "unifi_api_key": "test_key",
        "unifi_host": "test.host",
        field: value,  # Add the test value
    }

    print(f"\nTesting field: {field} with value: {value}")
    print(f"Settings dict: {settings_dict}")

    with pytest.raises(ValidationError) as exc_info:
        Settings.model_validate(settings_dict)

    error_str = str(exc_info.value)
    print(f"Validation error: {error_str}")
    assert expected_error in error_str, (
        f"Expected error '{expected_error}' not found in '{error_str}'"
    )


def test_project_paths() -> None:
    """Test project path settings."""
    settings = Settings(unifi_api_key="test", unifi_host="test.host")
    assert isinstance(settings.PROJECT_ROOT, Path)
    assert isinstance(settings.LOG_DIR, Path)
    assert settings.LOG_DIR == settings.PROJECT_ROOT / "logs"


@pytest.mark.parametrize("dev_mode", [True, False])
def test_get_log_file_path(dev_mode: bool, tmp_path: Path) -> None:
    """Test log file path generation."""
    os.environ["ISMINET_DEV_MODE"] = str(int(dev_mode))
    settings = Settings(
        unifi_api_key="test",
        unifi_host="test.host",
        LOG_DIR=tmp_path,  # Override log directory for testing
    )
    log_path = settings.get_log_file_path()
    assert isinstance(log_path, str)
    expected_file = "dev.log" if dev_mode else "prod.log"
    assert log_path == str(tmp_path / expected_file)
    assert tmp_path.exists()  # Directory should be created


def test_case_insensitive_env_vars() -> None:
    """Test case-insensitive environment variable loading."""
    # Test with mixed case
    os.environ["UNIFI_API_KEY"] = "test_key_mixed"
    os.environ["unifi_host"] = "test.host.mixed"
    settings = Settings()
    assert settings.unifi_api_key == "test_key_mixed"
    assert settings.unifi_host == "test.host.mixed"


def test_extra_env_vars() -> None:
    """Test handling of unknown environment variables."""
    os.environ["UNKNOWN_VAR"] = "test"
    # Should not raise an error
    settings = Settings(unifi_api_key="test", unifi_host="test.host")
    # Should not have the unknown variable as an attribute
    assert not hasattr(settings, "UNKNOWN_VAR")
