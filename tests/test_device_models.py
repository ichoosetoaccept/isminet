"""Tests for device models."""

import pytest
from typing import Dict, Any
from pydantic import ValidationError
from isminet.models.devices import Device, Client
from isminet.models.enums import DeviceType

# Test data
VALID_DEVICE_DATA: Dict[str, Any] = {
    "mac": "00:00:00:00:00:00",
    "model": "U7PG2",
    "type": DeviceType.UAP,
    "version": "4.0.66",
    "site_id": "default",
    "name": "Test AP",
    "ip": "192.168.1.1",
    "hostname": "ap-1",
    "uptime": 3600,
    "last_seen": 1234567890,
    "adopted": True,
    "status": "connected",
    "upgradable": False,
    "update_available": False,
}

VALID_CLIENT_DATA: Dict[str, Any] = {
    "mac": "00:00:00:00:00:00",
    "ip": "192.168.1.100",
    "hostname": "client1",
    "site_id": "default",
    "is_guest": False,
    "is_wired": True,
    "first_seen": 1234567890,
    "last_seen": 1234567890,
}


@pytest.mark.parametrize(
    "field_group,values,expected_values",
    [
        (
            "required_fields",
            {
                "mac": "00:00:00:00:00:00",
                "model": "U7PG2",
                "type": DeviceType.UAP,
                "version": "4.0.66",
                "site_id": "default",
            },
            {
                "mac": "00:00:00:00:00:00",
                "model": "U7PG2",
                "type": DeviceType.UAP,
                "version": "4.0.66",
                "site_id": "default",
            },
        ),
        (
            "status_fields",
            {
                "adopted": True,
                "status": "connected",
                "upgradable": False,
                "update_available": False,
            },
            {
                "adopted": True,
                "status": "connected",
                "upgradable": False,
                "update_available": False,
            },
        ),
        (
            "network_fields",
            {"ip": "192.168.1.1", "hostname": "ap-1"},
            {"ip": "192.168.1.1", "hostname": "ap-1"},
        ),
        (
            "timing_fields",
            {"uptime": 3600, "last_seen": 1234567890},
            {"uptime": 3600, "last_seen": 1234567890},
        ),
    ],
)
def test_device_model_fields(
    field_group: str, values: Dict[str, Any], expected_values: Dict[str, Any]
) -> None:
    """Test device model field groups."""
    device = Device(**{**VALID_DEVICE_DATA, **values})
    for field, expected in expected_values.items():
        assert getattr(device, field) == expected


@pytest.mark.parametrize(
    "invalid_data,error_pattern",
    [
        (
            {k: v for k, v in VALID_DEVICE_DATA.items() if k != "mac"},
            "Field required",
        ),
        (
            {**VALID_DEVICE_DATA, "mac": "invalid"},
            "Invalid MAC address format",
        ),
        (
            {**VALID_DEVICE_DATA, "type": "invalid"},
            "Input should be 'uap', 'usw', 'ugw', 'udm' or 'udm-pro'",
        ),
        (
            {**VALID_DEVICE_DATA, "version": "invalid"},
            "Version must be in format x.y.z",
        ),
        (
            {**VALID_DEVICE_DATA, "uptime": -1},
            "Input should be greater than or equal to 0",
        ),
    ],
)
def test_device_model_validation(
    invalid_data: Dict[str, Any], error_pattern: str
) -> None:
    """Test device model validation."""
    with pytest.raises(ValidationError, match=error_pattern):
        Device(**invalid_data)


@pytest.mark.parametrize(
    "field_group,values,expected_values",
    [
        (
            "required_fields",
            {
                "mac": "00:00:00:00:00:00",
                "ip": "192.168.1.100",
                "hostname": "client1",
                "site_id": "default",
            },
            {
                "mac": "00:00:00:00:00:00",
                "ip": "192.168.1.100",
                "hostname": "client1",
                "site_id": "default",
            },
        ),
        (
            "status_fields",
            {"is_guest": False, "is_wired": True},
            {"is_guest": False, "is_wired": True},
        ),
        (
            "timing_fields",
            {"first_seen": 1234567890, "last_seen": 1234567890},
            {"first_seen": 1234567890, "last_seen": 1234567890},
        ),
    ],
)
def test_client_model_fields(
    field_group: str, values: Dict[str, Any], expected_values: Dict[str, Any]
) -> None:
    """Test client model field groups."""
    client = Client(**{**VALID_CLIENT_DATA, **values})
    for field, expected in expected_values.items():
        assert getattr(client, field) == expected


@pytest.mark.parametrize(
    "invalid_data,error_pattern",
    [
        (
            {k: v for k, v in VALID_CLIENT_DATA.items() if k != "mac"},
            "Field required",
        ),
        (
            {**VALID_CLIENT_DATA, "mac": "invalid"},
            "Invalid MAC address format",
        ),
        (
            {**VALID_CLIENT_DATA, "ip": "invalid"},
            "Invalid IPv4 address",
        ),
        (
            {**VALID_CLIENT_DATA, "hostname": ""},
            "String should have at least 1 character",
        ),
        (
            {**VALID_CLIENT_DATA, "first_seen": -1},
            "Input should be greater than or equal to 0",
        ),
    ],
)
def test_client_model_validation(
    invalid_data: Dict[str, Any], error_pattern: str
) -> None:
    """Test client model validation."""
    with pytest.raises(ValidationError, match=error_pattern):
        Client(**invalid_data)
