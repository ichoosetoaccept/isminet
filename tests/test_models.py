"""Tests for UniFi Network API models."""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from isminet.models.base import BaseResponse
from isminet.models import Site
from isminet.models.devices import (
    Device,
    Client,
    RadioType,
    RadioProto,
    DeviceType,
    PortStats,
    WifiStats,
)
from isminet.models.version import VersionInfo

# Load test data from API response examples
DOCS_DIR = Path(__file__).parent.parent / "docs" / "api_responses"
with open(DOCS_DIR / "sites_response.json") as f:
    SITES_RESPONSE = json.load(f)

# Sample valid data for testing
VALID_MAC = "00:11:22:33:44:55"
VALID_IPV4 = "192.168.1.100"
VALID_IPV6 = "2001:db8::1"
VALID_NETMASK = "255.255.255.0"


def test_site_model_valid():
    """Test that the Site model can parse a valid site response."""
    site_data = SITES_RESPONSE["data"][0]
    site = Site(**site_data)

    # Test that all fields are correctly parsed
    assert site.name == "default"
    assert site.desc == "Default"
    assert site.id == "66450709e650bd21e774c55c"
    assert site.device_count == 3
    assert site.anonymous_id == "22263757-6495-476b-b62c-8e7b46cc2c73"
    assert site.external_id == "88f7af54-98f8-306a-a1c7-c9349722b1f6"
    assert site.attr_no_delete is True
    assert site.attr_hidden_id == "default"
    assert site.role == "admin"
    assert site.role_hotspot is False


def test_site_model_minimal():
    """Test that the Site model works with minimal data."""
    site_data = {
        "name": "test-site",
        "desc": "Test Site",
        "_id": "123456789",
        "device_count": 0,
    }
    site = Site(**site_data)

    assert site.name == "test-site"
    assert site.desc == "Test Site"
    assert site.id == "123456789"
    assert site.device_count == 0
    assert site.anonymous_id is None
    assert site.external_id is None
    assert site.attr_no_delete is None
    assert site.attr_hidden_id is None
    assert site.role is None
    assert site.role_hotspot is None


def test_site_model_invalid():
    """Test that the Site model properly validates input data."""
    invalid_sites = [
        # Missing required field
        {"name": "test-site", "desc": "Test Site"},
        # Invalid device count
        {
            "name": "test-site",
            "desc": "Test Site",
            "_id": "123456789",
            "device_count": -1,
        },
        # Empty string for required field
        {"name": "", "desc": "Test Site", "_id": "123456789", "device_count": 0},
    ]

    for data in invalid_sites:
        with pytest.raises(ValidationError):
            Site(**data)


def test_base_response_with_sites():
    """Test that the BaseResponse model can parse a response with sites."""
    response = BaseResponse[Site](**SITES_RESPONSE)

    assert response.meta.rc == "ok"
    assert len(response.data) == 1
    assert isinstance(response.data[0], Site)
    assert response.data[0].name == "default"


def test_port_stats_validation():
    """Test PortStats model validation."""
    valid_data = {
        "port_idx": 1,
        "name": "Port 1",
        "media": "GE",
        "port_poe": True,
        "speed": 1000,
        "up": True,
        "is_uplink": False,
        "mac": VALID_MAC,
        "rx_bytes": 1000000,
        "tx_bytes": 2000000,
        "rx_packets": 1000,
        "tx_packets": 2000,
        "rx_errors": 0,
        "tx_errors": 0,
        "type": "copper",
    }
    port = PortStats(**valid_data)
    assert port.mac == VALID_MAC.lower()
    assert port.speed == 1000

    # Test invalid port index
    with pytest.raises(ValidationError):
        PortStats(**{**valid_data, "port_idx": 0})

    # Test invalid MAC address
    with pytest.raises(ValidationError):
        PortStats(**{**valid_data, "mac": "invalid"})

    # Test invalid IP address
    with pytest.raises(ValidationError):
        PortStats(**{**valid_data, "ip": "invalid"})


def test_wifi_stats_validation():
    """Test WifiStats model validation."""
    valid_data = {
        "ap_mac": VALID_MAC,
        "channel": 36,
        "radio": RadioType.NA,
        "radio_proto": RadioProto.AX,
        "essid": "Test Network",
        "bssid": VALID_MAC,
        "signal": -65,
        "noise": -95,
        "tx_rate": 866000,
        "rx_rate": 866000,
        "tx_power": 20,
        "tx_retries": 10,
    }
    wifi = WifiStats(**valid_data)
    assert wifi.radio == RadioType.NA
    assert wifi.radio_proto == RadioProto.AX

    # Test invalid channel for radio type
    with pytest.raises(ValidationError):
        WifiStats(**{**valid_data, "channel": 1})  # 2.4 GHz channel for 5 GHz radio

    # Test invalid signal value
    with pytest.raises(ValidationError):
        WifiStats(**{**valid_data, "signal": 10})  # Positive dBm value

    # Test invalid channel width
    with pytest.raises(ValidationError):
        WifiStats(**{**valid_data, "channel_width": 30})  # Invalid channel width


def test_client_validation():
    """Test Client model validation."""
    valid_data = {
        "site_id": "default",
        "mac": VALID_MAC,
        "hostname": "test-device",
        "ip": VALID_IPV4,
        "last_ip": VALID_IPV4,
        "is_guest": False,
        "is_wired": True,
        "network": "Default",
        "network_id": "default",
        "uptime": 3600,
        "last_seen": 1600000000,
        "first_seen": 1500000000,
        "tx_bytes": 1000000,
        "rx_bytes": 2000000,
        "tx_packets": 1000,
        "rx_packets": 2000,
        "gw_mac": VALID_MAC,
        "sw_mac": VALID_MAC,
    }
    client = Client(**valid_data)
    assert client.mac == VALID_MAC.lower()
    assert client.ip == VALID_IPV4

    # Test invalid MAC address
    with pytest.raises(ValidationError):
        Client(**{**valid_data, "mac": "invalid"})

    # Test invalid IP address
    with pytest.raises(ValidationError):
        Client(**{**valid_data, "ip": "invalid"})

    # Test invalid first_seen/last_seen combination
    with pytest.raises(ValidationError):
        Client(**{**valid_data, "first_seen": 1700000000})  # After last_seen


def test_device_validation():
    """Test Device model validation."""
    valid_data = {
        "mac": VALID_MAC,
        "type": DeviceType.UAP,
        "model": "U6-Pro",
        "version": "7.0.0",
        "site_id": "default",
        "port_table": [],
    }
    device = Device(**valid_data)
    assert device.mac == VALID_MAC.lower()
    assert device.type == DeviceType.UAP

    # Test invalid MAC address
    with pytest.raises(ValidationError):
        Device(**{**valid_data, "mac": "invalid"})

    # Test invalid version format
    with pytest.raises(ValidationError):
        Device(**{**valid_data, "version": "invalid"})

    # Test invalid device type
    with pytest.raises(ValidationError):
        Device(**{**valid_data, "type": "invalid"})


def test_version_info_validation():
    """Test VersionInfo model validation."""
    valid_data = {
        "version": "7.0.0",
        "build": "1234",
        "site_id": "default",
    }
    version = VersionInfo(**valid_data)
    assert version.version == "7.0.0"

    # Test invalid version format
    with pytest.raises(ValidationError, match="Invalid version format"):
        invalid_data = valid_data.copy()
        invalid_data["version"] = "invalid.version"
        VersionInfo(**invalid_data)
