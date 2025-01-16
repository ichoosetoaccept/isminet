"""Tests for UniFi Network API client."""

import pytest
from unittest.mock import Mock, patch

from isminet.clients.unifi import UnifiClient
from isminet.config import APIConfig
from isminet.models.devices import Device, Client
from isminet.models.network import (
    NetworkConfiguration,
)
from isminet.models.system import SystemHealth
from isminet.models.enums import DeviceType, DHCPMode


@pytest.fixture
def unifi_client():
    """Create UnifiClient instance for testing."""
    config = APIConfig(
        api_key="test-key",
        host="unifi.local",
        port=8443,
        site="default",
        verify_ssl=False,
    )
    return UnifiClient(config)


@pytest.fixture
def mock_device_response():
    """Mock device response data."""
    return {
        "data": [
            {
                "mac": "00:11:22:33:44:55",
                "type": DeviceType.UGW,
                "version": "7.3.83",
                "model": "UDM-Pro",
                "name": "Gateway",
                "ip": "192.168.1.1",
                "uptime": 123456,
                "status": "connected",
            }
        ]
    }


@pytest.fixture
def mock_client_response():
    """Mock client response data."""
    return {
        "data": [
            {
                "mac": "aa:bb:cc:dd:ee:ff",
                "hostname": "client1",
                "ip": "192.168.1.100",
                "network_id": "default",
                "is_guest": False,
                "last_seen": 1234567890,
                "uptime": 3600,
                "first_seen": 1234567000,
            }
        ]
    }


@pytest.fixture
def mock_network_response():
    """Mock network response data."""
    return {
        "data": [
            {
                "id": "default",
                "name": "Default",
                "purpose": "corporate",
                "subnet": "192.168.1.0",
                "enabled": True,
                "vlan_enabled": True,
                "vlans": [
                    {
                        "vlan_id": 1,
                        "name": "Default VLAN",
                        "enabled": True,
                        "subnet": "192.168.1.0",
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
                ],
            }
        ]
    }


@pytest.fixture
def mock_system_response():
    """Mock system response data."""
    return {
        "data": [
            {
                "subsystem": "network",
                "status": "ok",
                "cpu_usage": 25.5,
                "mem_usage": 60.2,
                "temperature": 45.3,
                "loadavg_1": 1.2,
                "loadavg_5": 1.0,
                "loadavg_15": 0.8,
            }
        ]
    }


def test_site_path_construction(unifi_client):
    """Test site path property."""
    assert unifi_client.site_path == "/api/s/default"


@patch("requests.Session.request")
def test_device_management(mock_request, unifi_client, mock_device_response):
    """Test device management methods."""
    mock_response = Mock()
    mock_response.json.return_value = mock_device_response
    mock_response.status_code = 200
    mock_response.ok = True
    mock_request.return_value = mock_response

    # Test get_devices()
    devices = unifi_client.get_devices()
    assert len(devices) == 1
    assert isinstance(devices[0], Device)
    assert devices[0].mac == "00:11:22:33:44:55"

    # Test get_device()
    device = unifi_client.get_device("00:11:22:33:44:55")
    assert isinstance(device, Device)
    assert device.mac == "00:11:22:33:44:55"


@patch("requests.Session.request")
def test_client_management(mock_request, unifi_client, mock_client_response):
    """Test client management methods."""
    mock_response = Mock()
    mock_response.json.return_value = mock_client_response
    mock_response.status_code = 200
    mock_response.ok = True
    mock_request.return_value = mock_response

    # Test get_clients()
    clients = unifi_client.get_clients()
    assert len(clients) == 1
    assert isinstance(clients[0], Client)
    assert clients[0].mac == "aa:bb:cc:dd:ee:ff"

    # Test get_client()
    client = unifi_client.get_client("aa:bb:cc:dd:ee:ff")
    assert isinstance(client, Client)
    assert client.mac == "aa:bb:cc:dd:ee:ff"


@patch("requests.Session.request")
def test_network_settings(mock_request, unifi_client, mock_network_response):
    """Test network settings methods."""
    mock_response = Mock()
    mock_response.json.return_value = mock_network_response
    mock_response.status_code = 200
    mock_response.ok = True
    mock_request.return_value = mock_response

    # Test get_network_config()
    config = unifi_client.get_network_config("default")
    assert isinstance(config, NetworkConfiguration)
    assert config.name == "Default"
    assert config.purpose == "corporate"
    assert config.enabled is True
    assert config.subnet == "192.168.1.0"


@patch("requests.Session.request")
def test_system_status(mock_request, unifi_client, mock_system_response):
    """Test system status methods."""
    mock_response = Mock()
    mock_response.json.return_value = mock_system_response
    mock_response.status_code = 200
    mock_response.ok = True
    mock_request.return_value = mock_response

    # Test get_system_health()
    health = unifi_client.get_system_health()
    assert isinstance(health, SystemHealth)
    assert health.status == "ok"
    assert health.cpu_usage == 25.5
    assert health.mem_usage == 60.2
    assert health.temperature == 45.3
