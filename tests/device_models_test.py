"""Tests for device-related models."""

import pytest
from pydantic import ValidationError
from isminet.models.devices import Device, Client, VersionInfo


def test_device_model_valid():
    """Test that the Device model can parse a valid device response."""
    device_data = {
        "mac": "00:00:00:00:00:00",
        "model": "U7PG2",
        "type": "uap",
        "version": "4.0.66.10832",
    }
    device = Device(**device_data)

    assert device.mac == "00:00:00:00:00:00"
    assert device.model == "U7PG2"
    assert device.type == "uap"
    assert device.version == "4.0.66.10832"
    assert device.name is None
    assert device.led_override is None


def test_device_model_with_optional_fields():
    """Test that the Device model works with optional fields."""
    device_data = {
        "mac": "00:00:00:00:00:00",
        "model": "U7PG2",
        "type": "uap",
        "version": "4.0.66.10832",
        "name": "My Access Point",
        "led_override": "on",
    }
    device = Device(**device_data)

    assert device.mac == "00:00:00:00:00:00"
    assert device.name == "My Access Point"
    assert device.led_override == "on"


def test_device_model_invalid():
    """Test that the Device model properly validates input data."""
    invalid_devices = [
        # Missing required field
        {
            "model": "U7PG2",
            "type": "uap",
            "version": "4.0.66.10832",
            # missing mac
        },
        # Empty string for required field
        {"mac": "", "model": "U7PG2", "type": "uap", "version": "4.0.66.10832"},
    ]

    for invalid_device in invalid_devices:
        with pytest.raises(ValidationError):
            Device(**invalid_device)


def test_client_model_valid():
    """Test that the Client model can parse a valid client response."""
    client_data = {
        "mac": "00:00:00:00:00:00",
        "hostname": "client-device",
        "ip": "192.168.1.100",
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
            "mac": "00:00:00:00:00:00",
            "hostname": "client-device",
            # missing ip
        },
        # Empty string for required field
        {"mac": "00:00:00:00:00:00", "hostname": "", "ip": "192.168.1.100"},
    ]

    for invalid_client in invalid_clients:
        with pytest.raises(ValidationError):
            Client(**invalid_client)


def test_version_info_model_valid():
    """Test that the VersionInfo model can parse a valid version response."""
    version_data = {"version": "7.3.83"}
    version_info = VersionInfo(**version_data)

    assert version_info.version == "7.3.83"


def test_version_info_model_invalid():
    """Test that the VersionInfo model properly validates input data."""
    invalid_versions = [
        # Missing required field
        {},
        # Empty string for required field
        {"version": ""},
    ]

    for invalid_version in invalid_versions:
        with pytest.raises(ValidationError):
            VersionInfo(**invalid_version)
