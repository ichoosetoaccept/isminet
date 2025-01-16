"""Tests for device models."""

import pytest
from pydantic import ValidationError
from isminet.models.devices import Device, Client
from isminet.models.enums import DeviceType, LedOverride
from isminet.models.version import VersionInfo


def test_device_model_valid():
    """Test that the Device model can parse a valid device response."""
    device_data = {
        "mac": "00:00:00:00:00:00",
        "model": "U7PG2",
        "type": DeviceType.UAP,
        "version": "4.0.66",
        "site_id": "default",
    }
    device = Device(**device_data)

    assert device.mac == "00:00:00:00:00:00"
    assert device.model == "U7PG2"
    assert device.type == DeviceType.UAP
    assert device.version == "4.0.66"
    assert device.name is None
    assert device.led_override is None


def test_device_model_with_optional_fields():
    """Test that the Device model works with optional fields."""
    device_data = {
        "mac": "00:00:00:00:00:00",
        "model": "U7PG2",
        "type": DeviceType.UAP,
        "version": "4.0.66",
        "site_id": "default",
        "name": "My Access Point",
        "led_override": LedOverride.ON,
    }
    device = Device(**device_data)

    assert device.mac == "00:00:00:00:00:00"
    assert device.name == "My Access Point"
    assert device.led_override == LedOverride.ON


def test_device_model_invalid():
    """Test that the Device model properly validates input data."""
    invalid_devices = [
        # Missing required field
        {
            "model": "U7PG2",
            "type": DeviceType.UAP,
            "version": "4.0.66",
        },
        # Invalid MAC address
        {
            "mac": "invalid",
            "model": "U7PG2",
            "type": DeviceType.UAP,
            "version": "4.0.66",
            "site_id": "default",
        },
        # Invalid version format
        {
            "mac": "00:00:00:00:00:00",
            "model": "U7PG2",
            "type": DeviceType.UAP,
            "version": "invalid",
            "site_id": "default",
        },
    ]

    for data in invalid_devices:
        with pytest.raises(ValidationError):
            Device(**data)


def test_client_model_valid():
    """Test that the Client model can parse a valid client response."""
    client_data = {
        "mac": "00:00:00:00:00:00",
        "hostname": "client-device",
        "ip": "192.168.1.100",
        "site_id": "default",
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
        "gw_mac": "00:00:00:00:00:01",
        "sw_mac": "00:00:00:00:00:02",
    }
    client = Client(**client_data)
    assert client.mac == "00:00:00:00:00:00"
    assert client.hostname == "client-device"
    assert client.ip == "192.168.1.100"


def test_client_model_invalid():
    """Test that the Client model properly validates input data."""
    invalid_clients = [
        # Missing required field
        {
            "hostname": "client-device",
            "ip": "192.168.1.100",
        },
        # Invalid MAC address
        {
            "mac": "invalid",
            "hostname": "client-device",
            "ip": "192.168.1.100",
            "site_id": "default",
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
            "gw_mac": "00:00:00:00:00:01",
            "sw_mac": "00:00:00:00:00:02",
        },
        # Invalid IP address
        {
            "mac": "00:00:00:00:00:00",
            "hostname": "client-device",
            "ip": "invalid",
            "site_id": "default",
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
            "gw_mac": "00:00:00:00:00:01",
            "sw_mac": "00:00:00:00:00:02",
        },
    ]

    for data in invalid_clients:
        with pytest.raises(ValidationError):
            Client(**data)


def test_version_info_model_valid():
    """Test that the VersionInfo model can parse a valid version response."""
    version_data = {
        "version": "7.3.83",
        "site_id": "default",
    }
    version_info = VersionInfo(**version_data)
    assert version_info.version == "7.3.83"


def test_version_info_model_invalid():
    """Test that the VersionInfo model properly validates input data."""
    invalid_versions = [
        # Missing required field
        {"site_id": "default"},
        # Invalid version format
        {"version": "invalid", "site_id": "default"},
    ]

    for data in invalid_versions:
        with pytest.raises(ValidationError):
            VersionInfo(**data)
