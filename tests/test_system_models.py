"""Tests for system status models."""

import pytest
from pydantic import ValidationError

from isminet.models.system import (
    SystemHealth,
    ProcessInfo,
    ServiceStatus,
    SystemStatus,
)
from isminet.models.enums import DeviceType

# Test data
VALID_SYSTEM_HEALTH = {
    "subsystem": "network",
    "status": "ok",
    "status_code": 0,
    "status_message": "All systems operational",
    "last_check": 1000,
    "next_check": 2000,
    "cpu_usage": 50.0,
    "mem_usage": 75.0,
    "temperature": 45.5,
    "loadavg_1": 0.5,
    "loadavg_5": 1.0,
    "loadavg_15": 1.5,
}

VALID_PROCESS_INFO = {
    "pid": 1234,
    "name": "unifi-core",
    "cpu_usage": 25.5,
    "mem_usage": 15.5,
    "mem_rss": 1024 * 1024 * 100,  # 100MB
    "mem_vsz": 1024 * 1024 * 500,  # 500MB
    "threads": 4,
    "uptime": 3600,
}

VALID_SERVICE_STATUS = {
    "name": "unifi",
    "status": "running",
    "enabled": True,
    "last_start": 1000,
    "last_stop": None,
    "restart_count": 0,
    "pid": 1234,
}

VALID_SYSTEM_STATUS = {
    "device_type": DeviceType.UDM,
    "version": "7.5.187",
    "uptime": 86400,
    "health": [VALID_SYSTEM_HEALTH],
    "processes": [VALID_PROCESS_INFO],
    "services": [VALID_SERVICE_STATUS],
    "cpu_usage": 45.5,
    "mem_usage": 65.5,
    "temperature": 50.0,
    "loadavg_1": 0.8,
    "loadavg_5": 1.2,
    "loadavg_15": 1.0,
    "tx_bytes": 1000000,
    "rx_bytes": 2000000,
    "storage_usage": 75.5,
    "storage_available": 1024 * 1024 * 1024 * 50,  # 50GB
}


def test_system_health():
    """Test SystemHealth validation."""
    # Test valid configuration
    health = SystemHealth(**VALID_SYSTEM_HEALTH)
    assert health.subsystem == "network"
    assert health.status == "ok"
    assert health.cpu_usage == 50.0

    # Test invalid status
    with pytest.raises(ValidationError):
        SystemHealth(**{**VALID_SYSTEM_HEALTH, "status": "invalid"})

    # Test invalid timestamp order
    with pytest.raises(ValidationError):
        SystemHealth(**{**VALID_SYSTEM_HEALTH, "last_check": 2000, "next_check": 1000})

    # Test invalid CPU usage
    with pytest.raises(ValidationError):
        SystemHealth(**{**VALID_SYSTEM_HEALTH, "cpu_usage": 101})

    # Test invalid memory usage
    with pytest.raises(ValidationError):
        SystemHealth(**{**VALID_SYSTEM_HEALTH, "mem_usage": -1})


def test_process_info():
    """Test ProcessInfo validation."""
    # Test valid configuration
    process = ProcessInfo(**VALID_PROCESS_INFO)
    assert process.pid == 1234
    assert process.name == "unifi-core"
    assert process.cpu_usage == 25.5

    # Test invalid PID
    with pytest.raises(ValidationError):
        ProcessInfo(**{**VALID_PROCESS_INFO, "pid": 0})

    # Test invalid CPU usage
    with pytest.raises(ValidationError):
        ProcessInfo(**{**VALID_PROCESS_INFO, "cpu_usage": 101})

    # Test invalid memory usage
    with pytest.raises(ValidationError):
        ProcessInfo(**{**VALID_PROCESS_INFO, "mem_usage": -1})

    # Test invalid thread count
    with pytest.raises(ValidationError):
        ProcessInfo(**{**VALID_PROCESS_INFO, "threads": 0})

    # Test invalid memory values
    with pytest.raises(ValidationError):
        ProcessInfo(**{**VALID_PROCESS_INFO, "mem_rss": -1})
    with pytest.raises(ValidationError):
        ProcessInfo(**{**VALID_PROCESS_INFO, "mem_vsz": -1})


def test_service_status():
    """Test ServiceStatus validation."""
    # Test valid configuration
    service = ServiceStatus(**VALID_SERVICE_STATUS)
    assert service.name == "unifi"
    assert service.status == "running"
    assert service.enabled is True

    # Test invalid status
    with pytest.raises(ValidationError):
        ServiceStatus(**{**VALID_SERVICE_STATUS, "status": "invalid"})

    # Test invalid PID
    with pytest.raises(ValidationError):
        ServiceStatus(**{**VALID_SERVICE_STATUS, "pid": 0})

    # Test invalid restart count
    with pytest.raises(ValidationError):
        ServiceStatus(**{**VALID_SERVICE_STATUS, "restart_count": -1})

    # Test stopped service
    service = ServiceStatus(
        **{
            **VALID_SERVICE_STATUS,
            "status": "stopped",
            "pid": None,
            "last_stop": 2000,
        }
    )
    assert service.status == "stopped"
    assert service.pid is None


def test_system_status():
    """Test SystemStatus validation."""
    # Test valid configuration
    status = SystemStatus(**VALID_SYSTEM_STATUS)
    assert status.device_type == DeviceType.UDM
    assert status.version == "7.5.187"
    assert len(status.health) == 1
    assert len(status.processes) == 1
    assert len(status.services) == 1

    # Test invalid version
    with pytest.raises(ValidationError):
        SystemStatus(**{**VALID_SYSTEM_STATUS, "version": "invalid"})

    # Test invalid update version
    with pytest.raises(ValidationError):
        SystemStatus(**{**VALID_SYSTEM_STATUS, "update_version": "invalid"})

    # Test invalid storage values
    with pytest.raises(ValidationError):
        SystemStatus(**{**VALID_SYSTEM_STATUS, "storage_usage": 101})
    with pytest.raises(ValidationError):
        SystemStatus(**{**VALID_SYSTEM_STATUS, "storage_available": -1})

    # Test without optional components
    minimal_status = {
        "device_type": DeviceType.UDM,
        "version": "7.5.187",
        "uptime": 86400,
        "health": [VALID_SYSTEM_HEALTH],
    }
    status = SystemStatus(**minimal_status)
    assert status.processes is None
    assert status.services is None
    assert status.alerts is None
