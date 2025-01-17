"""Common test fixtures and constants for isminet tests."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Generator, cast

import pytest
import structlog
from _pytest.logging import LogCaptureFixture

from isminet.logging import setup_logging

# Constants for testing
VALID_MAC = "00:11:22:33:44:55"
VALID_IPV4 = "192.168.1.1"
VALID_IPV6 = "2001:db8::1"
VALID_NETMASK = "255.255.255.0"

# Load test data from API response examples
DOCS_DIR = Path(__file__).parent.parent / "docs" / "api_responses"
with open(DOCS_DIR / "sites_response.json") as f:
    SITES_RESPONSE = cast(Dict[str, Any], json.load(f))


@pytest.fixture(autouse=True)
def cleanup_handlers() -> Generator[None, None, None]:
    """Clean up logging handlers after each test."""
    yield
    root_logger = logging.getLogger()
    # Only remove non-file handlers to keep our log files intact
    for handler in root_logger.handlers[:]:
        if not isinstance(handler, logging.FileHandler):
            handler.close()
            root_logger.removeHandler(handler)
    structlog.reset_defaults()


@pytest.fixture
def valid_mac() -> str:
    """Return a valid MAC address for testing."""
    return VALID_MAC


@pytest.fixture
def valid_ipv4() -> str:
    """Return a valid IPv4 address for testing."""
    return VALID_IPV4


@pytest.fixture
def valid_ipv6() -> str:
    """Return a valid IPv6 address for testing."""
    return VALID_IPV6


@pytest.fixture
def valid_netmask() -> str:
    """Return a valid netmask for testing."""
    return VALID_NETMASK


@pytest.fixture
def log_output(caplog: LogCaptureFixture) -> LogCaptureFixture:
    """Fixture to capture log output."""
    caplog.set_level("DEBUG")
    return caplog


# Set up logging using centralized settings
setup_logging()
