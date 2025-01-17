"""Tests for system models."""

import pytest
from typing import Dict, Any, cast
from pydantic import ValidationError

from isminet.models.system import (
    SystemHealth,
    ProcessInfo,
    ServiceStatus,
    SystemStatus,
)
from isminet.models.enums import DeviceType

# Test data
VALID_SYSTEM_HEALTH: Dict[str, Any] = {
    "device_type": DeviceType.UGW,
    "subsystem": "network",
    "status": "ok",
    "status_code": 0,
    "status_message": "System healthy",
    "last_check": 1000,
    "next_check": 2000,
}

VALID_PROCESS_INFO: Dict[str, Any] = {
    "pid": 1234,
    "name": "test_process",
    "cpu_usage": 25.5,
    "mem_usage": 60.2,
    "mem_rss": 1024,
    "mem_vsz": 2048,
    "threads": 4,
    "uptime": 3600,
}

VALID_SERVICE_STATUS: Dict[str, Any] = {
    "name": "test_service",
    "status": "running",
    "enabled": True,
    "last_start": 1000,
    "last_stop": None,
    "restart_count": 0,
    "pid": 1234,
}

VALID_SYSTEM_STATUS: Dict[str, Any] = {
    "device_type": DeviceType.UGW,
    "version": "1.0.0",
    "uptime": 3600,
    "health": [VALID_SYSTEM_HEALTH],
    "processes": [VALID_PROCESS_INFO],
    "services": [VALID_SERVICE_STATUS],
    "alerts": None,
    "upgradable": False,
    "update_available": False,
    "update_version": None,
    "storage_usage": 75,
    "storage_available": 1024,
}


def test_system_health_model() -> None:
    """Test SystemHealth model initialization and validation."""
    health = SystemHealth(**VALID_SYSTEM_HEALTH)
    assert health.subsystem == "network"
    assert health.status == "ok"
    assert health.status_code == 0
    assert health.status_message == "System healthy"
    assert health.last_check == 1000
    assert health.next_check == 2000


@pytest.mark.parametrize(
    "invalid_data,expected_error",
    [
        ({"status": "invalid"}, "Status must be one of: ok, warning, error"),
        (
            {"last_check": 2000, "next_check": 1000},
            "next_check must be after last_check",
        ),
        ({"subsystem": ""}, "String should have at least 1 character"),
        ({"status_code": -1}, "Input should be greater than or equal to 0"),
    ],
)
def test_system_health_validation_errors(
    invalid_data: Dict[str, Any], expected_error: str
) -> None:
    """Test SystemHealth validation errors with parameterized test cases."""
    test_data = cast(Dict[str, Any], {**VALID_SYSTEM_HEALTH, **invalid_data})
    with pytest.raises(ValidationError, match=expected_error):
        SystemHealth(**test_data)


def test_process_info_model() -> None:
    """Test ProcessInfo model initialization and validation."""
    process = ProcessInfo(**VALID_PROCESS_INFO)
    assert process.pid == 1234
    assert process.name == "test_process"
    assert process.cpu_usage == 25.5
    assert process.mem_usage == 60.2
    assert process.mem_rss == 1024
    assert process.mem_vsz == 2048
    assert process.threads == 4
    assert process.uptime == 3600


@pytest.mark.parametrize(
    "invalid_data,expected_error",
    [
        ({"pid": 0}, "Input should be greater than or equal to 1"),
        ({"name": ""}, "String should have at least 1 character"),
        ({"cpu_usage": -1}, "Input should be greater than or equal to 0"),
        ({"cpu_usage": 101}, "Input should be less than or equal to 100"),
        ({"mem_usage": -1}, "Input should be greater than or equal to 0"),
        ({"mem_usage": 101}, "Input should be less than or equal to 100"),
        ({"mem_rss": -1}, "Input should be greater than or equal to 0"),
        ({"mem_vsz": -1}, "Input should be greater than or equal to 0"),
        ({"threads": 0}, "Input should be greater than or equal to 1"),
        ({"uptime": -1}, "Input should be greater than or equal to 0"),
    ],
)
def test_process_info_validation_errors(
    invalid_data: Dict[str, Any], expected_error: str
) -> None:
    """Test ProcessInfo validation errors with parameterized test cases."""
    test_data = cast(Dict[str, Any], {**VALID_PROCESS_INFO, **invalid_data})
    with pytest.raises(ValidationError, match=expected_error):
        ProcessInfo(**test_data)


def test_service_status_model() -> None:
    """Test ServiceStatus model initialization and validation."""
    service = ServiceStatus(**VALID_SERVICE_STATUS)
    assert service.name == "test_service"
    assert service.status == "running"
    assert service.enabled is True
    assert service.last_start == 1000
    assert service.last_stop is None
    assert service.restart_count == 0
    assert service.pid == 1234


@pytest.mark.parametrize(
    "invalid_data,expected_error",
    [
        ({"name": ""}, "String should have at least 1 character"),
        ({"status": "invalid"}, "Status must be one of: running, stopped, error"),
        ({"restart_count": -1}, "Input should be greater than or equal to 0"),
        ({"pid": 0}, "Input should be greater than or equal to 1"),
    ],
)
def test_service_status_validation_errors(
    invalid_data: Dict[str, Any], expected_error: str
) -> None:
    """Test ServiceStatus validation errors with parameterized test cases."""
    test_data = cast(Dict[str, Any], {**VALID_SERVICE_STATUS, **invalid_data})
    with pytest.raises(ValidationError, match=expected_error):
        ServiceStatus(**test_data)


def test_system_status_model() -> None:
    """Test SystemStatus model initialization and validation."""
    status = SystemStatus(**VALID_SYSTEM_STATUS)
    assert status.device_type == DeviceType.UGW
    assert status.version == "1.0.0"
    assert status.uptime == 3600
    assert len(status.health) == 1
    assert len(status.processes or []) == 1  # Handle optional lists
    assert len(status.services or []) == 1  # Handle optional lists
    assert status.alerts is None
    assert status.upgradable is False
    assert status.update_available is False
    assert status.update_version is None
    assert status.storage_usage == 75
    assert status.storage_available == 1024


@pytest.mark.parametrize(
    "invalid_data,expected_error",
    [
        ({"version": "invalid"}, "Version must be in format x.y.z"),
        ({"uptime": -1}, "Input should be greater than or equal to 0"),
        ({"health": []}, "List should have at least 1 item"),
        ({"storage_usage": -1}, "Input should be greater than or equal to 0"),
        ({"storage_usage": 101}, "Input should be less than or equal to 100"),
        ({"storage_available": -1}, "Input should be greater than or equal to 0"),
        ({"update_version": "invalid"}, "Version must be in format x.y.z"),
    ],
)
def test_system_status_validation_errors(
    invalid_data: Dict[str, Any], expected_error: str
) -> None:
    """Test SystemStatus validation errors with parameterized test cases."""
    test_data = cast(Dict[str, Any], {**VALID_SYSTEM_STATUS, **invalid_data})
    with pytest.raises(ValidationError, match=expected_error):
        SystemStatus(**test_data)
