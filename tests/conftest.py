"""Common test fixtures and constants for isminet tests."""

import json
from pathlib import Path
from typing import Any, Dict, cast

import pytest
from _pytest.logging import LogCaptureFixture

# Constants for testing
VALID_MAC = "00:11:22:33:44:55"
VALID_IPV4 = "192.168.1.1"
VALID_IPV6 = "2001:db8::1"
VALID_NETMASK = "255.255.255.0"

# Load test data from API response examples
DOCS_DIR = Path(__file__).parent.parent / "docs" / "api_responses"
with open(DOCS_DIR / "sites_response.json") as f:
    SITES_RESPONSE = cast(Dict[str, Any], json.load(f))


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
