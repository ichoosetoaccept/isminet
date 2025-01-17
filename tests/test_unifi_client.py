"""Tests for UniFi Network API client."""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch

from isminet.clients.unifi import UnifiClient
from isminet.config import APIConfig
from isminet.models.devices import Device, Client
from isminet.models.network import (
    NetworkConfiguration,
)
from isminet.models.system import (
    SystemStatus,
)
from isminet.models.enums import DeviceType, DHCPMode


@pytest.fixture
def unifi_client() -> UnifiClient:
    """
    Pytest fixture that creates and returns a configured UnifiClient instance for testing purposes.

    The fixture initializes a UnifiClient with predefined test configuration parameters, allowing consistent and controlled API client setup across test scenarios.

    Returns:
        UnifiClient: A configured UnifiClient instance with test credentials and settings
    """
    config = APIConfig(
        api_key="test-key",
        host="unifi.local",
        port=8443,
        site="default",
        verify_ssl=False,
    )
    return UnifiClient(config)


@pytest.fixture
def mock_device_response() -> Dict[str, List[Dict[str, Any]]]:
    """
    Provides a mock response simulating a UniFi network device for testing purposes.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of device data
    """
    return {
        "data": [
            {
                "mac": "00:00:00:00:00:00",
                "type": DeviceType.UGW,
                "version": "4.0.66",
                "model": "UGW3",
                "name": "Gateway",
                "site_id": "default",
                "ip": "192.168.1.1",
                "hostname": "gateway",
                "uptime": 3600,
                "last_seen": 1234567890,
                "adopted": True,
                "status": "connected",
                "upgradable": False,
                "update_available": False,
                "health": [
                    {
                        "device_type": DeviceType.UGW,
                        "subsystem": "network",
                        "status": "ok",
                        "status_code": 0,
                        "status_message": "System healthy",
                        "last_check": 1000,
                        "next_check": 2000,
                    }
                ],
            }
        ]
    }


@pytest.fixture
def mock_client_response() -> Dict[str, List[Dict[str, Any]]]:
    """
    Provides a mock response simulating a UniFi network client for testing purposes.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of client data
    """
    return {
        "data": [
            {
                "mac": "00:00:00:00:00:00",
                "ip": "192.168.1.100",
                "hostname": "client1",
                "site_id": "default",
                "is_guest": False,
                "is_wired": True,
                "first_seen": 1234567890,
                "last_seen": 1234567890,
            }
        ]
    }


@pytest.fixture
def mock_network_response() -> Dict[str, List[Dict[str, Any]]]:
    """
    Provides a mock response simulating network configuration data for testing purposes.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing network configuration data
    """
    return {
        "data": [
            {
                "name": "Default",
                "purpose": "corporate",
                "enabled": True,
                "subnet": "192.168.1.0/24",
                "vlan_enabled": True,
                "vlans": [
                    {
                        "id": 10,
                        "name": "IoT",
                        "enabled": True,
                        "subnet": "192.168.10.0/24",
                        "gateway_ip": "192.168.10.1",
                        "tagged_ports": [],
                        "untagged_ports": [],
                        "dhcp": {
                            "mode": DHCPMode.SERVER,
                            "enabled": True,
                            "start": "192.168.10.100",
                            "end": "192.168.10.200",
                            "lease_time": 86400,
                            "dns": ["8.8.8.8", "8.8.4.4"],
                            "gateway_ip": "192.168.10.1",
                        },
                    }
                ],
                "dhcp": {
                    "mode": DHCPMode.SERVER,
                    "enabled": True,
                    "start": "192.168.1.100",
                    "end": "192.168.1.200",
                    "lease_time": 86400,
                    "dns": ["8.8.8.8", "8.8.4.4"],
                    "gateway_ip": "192.168.1.1",
                },
            }
        ]
    }


@pytest.fixture
def mock_system_response() -> Dict[str, List[Dict[str, Any]]]:
    """
    Provides a mock response simulating system health data for testing purposes.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing system health data
    """
    return {
        "data": [
            {
                "device_type": DeviceType.UGW,
                "version": "4.0.66",
                "uptime": 3600,
                "health": [
                    {
                        "device_type": DeviceType.UGW,
                        "subsystem": "network",
                        "status": "ok",
                        "status_code": 0,
                        "status_message": "System healthy",
                        "last_check": 1000,
                        "next_check": 2000,
                    }
                ],
                "processes": [
                    {
                        "pid": 1234,
                        "name": "test_process",
                        "cpu_usage": 25.5,
                        "mem_usage": 60.2,
                        "mem_rss": 1024,
                        "mem_vsz": 2048,
                        "threads": 4,
                        "uptime": 3600,
                    }
                ],
                "services": [
                    {
                        "name": "test_service",
                        "status": "running",
                        "enabled": True,
                        "last_start": 1000,
                        "last_stop": None,
                        "restart_count": 0,
                        "pid": 1234,
                    }
                ],
                "alerts": None,
                "upgradable": False,
                "update_available": False,
                "update_version": None,
                "storage_usage": 75,
                "storage_available": 1024,
            }
        ]
    }


def test_site_path_construction(unifi_client: UnifiClient) -> None:
    """Test that site-specific API paths are constructed correctly."""
    assert unifi_client.site_path == "/api/s/default"


@patch("requests.Session.request")
def test_device_management(
    mock_request: Mock,
    unifi_client: UnifiClient,
    mock_device_response: Dict[str, List[Dict[str, Any]]],
) -> None:
    """Test device management API endpoints."""
    mock_request.return_value.json.return_value = mock_device_response
    mock_request.return_value.status_code = 200

    # Test get_devices
    devices = unifi_client.get_devices()
    assert len(devices) == 1
    assert isinstance(devices[0], Device)
    assert devices[0].mac == "00:00:00:00:00:00"
    assert devices[0].type == DeviceType.UGW
    assert devices[0].version == "4.0.66"
    assert devices[0].model == "UGW3"
    assert devices[0].name == "Gateway"
    assert devices[0].site_id == "default"
    assert devices[0].ip == "192.168.1.1"
    assert devices[0].hostname == "gateway"
    assert devices[0].uptime == 3600
    assert devices[0].last_seen == 1234567890
    assert devices[0].adopted is True
    assert devices[0].status == "connected"
    assert devices[0].upgradable is False
    assert devices[0].update_available is False
    assert devices[0].health is not None
    assert len(devices[0].health) == 1
    assert devices[0].health[0].subsystem == "network"
    assert devices[0].health[0].status == "ok"

    # Test get_device
    device = unifi_client.get_device("00:00:00:00:00:00")
    assert isinstance(device, Device)
    assert device.mac == "00:00:00:00:00:00"
    assert device.type == DeviceType.UGW
    assert device.version == "4.0.66"
    assert device.model == "UGW3"
    assert device.name == "Gateway"
    assert device.site_id == "default"
    assert device.ip == "192.168.1.1"
    assert device.hostname == "gateway"
    assert device.uptime == 3600
    assert device.last_seen == 1234567890
    assert device.adopted is True
    assert device.status == "connected"
    assert device.upgradable is False
    assert device.update_available is False
    assert device.health is not None
    assert len(device.health) == 1
    assert device.health[0].subsystem == "network"
    assert device.health[0].status == "ok"


@patch("requests.Session.request")
def test_client_management(
    mock_request: Mock,
    unifi_client: UnifiClient,
    mock_client_response: Dict[str, List[Dict[str, Any]]],
) -> None:
    """Test client management API endpoints."""
    mock_request.return_value.json.return_value = mock_client_response
    mock_request.return_value.status_code = 200

    # Test get_clients
    clients = unifi_client.get_clients()
    assert len(clients) == 1
    assert isinstance(clients[0], Client)
    assert clients[0].mac == "00:00:00:00:00:00"
    assert clients[0].ip == "192.168.1.100"
    assert clients[0].hostname == "client1"
    assert clients[0].site_id == "default"
    assert clients[0].is_guest is False
    assert clients[0].is_wired is True
    assert clients[0].first_seen == 1234567890
    assert clients[0].last_seen == 1234567890

    # Test get_client
    client = unifi_client.get_client("00:00:00:00:00:00")
    assert isinstance(client, Client)
    assert client.mac == "00:00:00:00:00:00"
    assert client.ip == "192.168.1.100"
    assert client.hostname == "client1"
    assert client.site_id == "default"
    assert client.is_guest is False
    assert client.is_wired is True
    assert client.first_seen == 1234567890
    assert client.last_seen == 1234567890


@patch("requests.Session.request")
def test_network_settings(
    mock_request: Mock,
    unifi_client: UnifiClient,
    mock_network_response: Dict[str, List[Dict[str, Any]]],
) -> None:
    """Test network settings API endpoints."""
    mock_request.return_value.json.return_value = mock_network_response
    mock_request.return_value.status_code = 200

    # Test get_network_config
    config = unifi_client.get_network_config("default")
    assert isinstance(config, NetworkConfiguration)
    assert config.name == "Default"
    assert config.purpose == "corporate"
    assert config.enabled is True
    assert config.subnet == "192.168.1.0/24"
    assert config.vlan_enabled is True
    assert config.vlans is not None
    assert len(config.vlans) == 1
    vlan = config.vlans[0]
    assert vlan.id == 10
    assert vlan.name == "IoT"
    assert vlan.enabled is True
    assert vlan.subnet == "192.168.10.0/24"
    assert vlan.gateway_ip == "192.168.10.1"
    assert vlan.tagged_ports == []
    assert vlan.untagged_ports == []
    assert vlan.dhcp is not None
    assert vlan.dhcp.mode == DHCPMode.SERVER
    assert vlan.dhcp.enabled is True
    assert vlan.dhcp.start == "192.168.10.100"
    assert vlan.dhcp.end == "192.168.10.200"
    assert vlan.dhcp.lease_time == 86400
    assert vlan.dhcp.dns == ["8.8.8.8", "8.8.4.4"]
    assert vlan.dhcp.gateway_ip == "192.168.10.1"
    assert config.dhcp is not None
    assert config.dhcp.mode == DHCPMode.SERVER
    assert config.dhcp.enabled is True
    assert config.dhcp.start == "192.168.1.100"
    assert config.dhcp.end == "192.168.1.200"
    assert config.dhcp.lease_time == 86400
    assert config.dhcp.dns == ["8.8.8.8", "8.8.4.4"]
    assert config.dhcp.gateway_ip == "192.168.1.1"


@patch("requests.Session.request")
def test_system_status(
    mock_request: Mock,
    unifi_client: UnifiClient,
    mock_system_response: Dict[str, List[Dict[str, Any]]],
) -> None:
    """Test system status API endpoints."""
    mock_request.return_value.json.return_value = mock_system_response
    mock_request.return_value.status_code = 200

    # Test get_system_health
    status = unifi_client.get_system_health()
    assert isinstance(status, SystemStatus)
    assert status.device_type == DeviceType.UGW
    assert status.version == "4.0.66"
    assert status.uptime == 3600
    assert len(status.health) == 1
    assert status.health[0].subsystem == "network"
    assert status.health[0].status == "ok"
    assert status.health[0].status_code == 0
    assert status.health[0].status_message == "System healthy"
    assert status.health[0].last_check == 1000
    assert status.health[0].next_check == 2000
    assert len(status.processes) == 1
    assert status.processes[0].pid == 1234
    assert status.processes[0].name == "test_process"
    assert status.processes[0].cpu_usage == 25.5
    assert status.processes[0].mem_usage == 60.2
    assert status.processes[0].mem_rss == 1024
    assert status.processes[0].mem_vsz == 2048
    assert status.processes[0].threads == 4
    assert status.processes[0].uptime == 3600
    assert len(status.services) == 1
    assert status.services[0].name == "test_service"
    assert status.services[0].status == "running"
    assert status.services[0].enabled is True
    assert status.services[0].last_start == 1000
    assert status.services[0].last_stop is None
    assert status.services[0].restart_count == 0
    assert status.services[0].pid == 1234
    assert status.alerts is None
    assert status.upgradable is False
    assert status.update_available is False
    assert status.update_version is None
    assert status.storage_usage == 75
    assert status.storage_available == 1024
