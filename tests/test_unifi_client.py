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
    """
    Pytest fixture that creates and returns a configured UnifiClient instance for testing purposes.
    
    The fixture initializes a UnifiClient with predefined test configuration parameters, allowing consistent and controlled API client setup across test scenarios.
    
    Parameters:
        None
    
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
def mock_device_response():
    """
    Provides a mock response simulating a UniFi network device for testing purposes.
    
    Returns:
        dict: A dictionary containing a list of device data with predefined attributes, including:
            - mac (str): Device MAC address
            - type (DeviceType): Device type (UniFi Gateway)
            - version (str): Firmware version
            - model (str): Device model
            - name (str): Device name
            - ip (str): IP address
            - uptime (int): Device uptime in seconds
            - status (str): Connection status
    """
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
    """
    Provides a mock response simulating a client device's network data for testing purposes.
    
    Returns:
        dict: A dictionary containing a list of client data with predefined attributes, including:
            - mac (str): Client's MAC address
            - hostname (str): Client's hostname
            - ip (str): Client's IP address
            - network_id (str): Network identifier
            - is_guest (bool): Guest network status
            - last_seen (int): Timestamp of last device detection
            - uptime (int): Duration the client has been connected
            - first_seen (int): Timestamp of first device detection
    """
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
    """
    Provides a mock response simulating a network configuration for testing UniFi Network API client interactions.
    
    Returns:
        dict: A dictionary containing a list of network configuration data with the following structure:
        - 'data': A list with a single network configuration dictionary
        - Network configuration includes:
            * 'id': Network identifier (str)
            * 'name': Network name (str)
            * 'purpose': Network purpose (str)
            * 'subnet': Network subnet (str)
            * 'enabled': Network enabled status (bool)
            * 'vlan_enabled': VLAN configuration status (bool)
            * 'vlans': List of VLAN configurations with detailed DHCP settings
    """
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
    """
    Provides a mock response simulating system health data for UniFi network testing.
    
    Returns:
        dict: A dictionary containing system health metrics with the following keys:
            - data (list): A list with a single dictionary representing system health
            - subsystem (str): Name of the system subsystem (e.g., "network")
            - status (str): Overall system status ("ok")
            - cpu_usage (float): Current CPU utilization percentage
            - mem_usage (float): Current memory usage percentage
            - temperature (float): System temperature in degrees
            - loadavg_1 (float): 1-minute system load average
            - loadavg_5 (float): 5-minute system load average
            - loadavg_15 (float): 15-minute system load average
    """
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
    """
    Test the construction of the site path for the UniFi client.
    
    Verifies that the `site_path` property is correctly generated with the default site name.
    
    Args:
        unifi_client: A configured UniFi client instance to test.
    
    Asserts:
        The site path is constructed as "/api/s/default" for the default site.
    """
    assert unifi_client.site_path == "/api/s/default"


@patch("requests.Session.request")
def test_device_management(mock_request, unifi_client, mock_device_response):
    """
    Test the device management methods of the UniFi Network API client.
    
    This test function verifies the functionality of device retrieval methods:
    - Checks the `get_devices()` method returns a list of Device objects
    - Validates that the returned devices have the correct MAC address
    - Tests the `get_device()` method for retrieving a specific device by MAC address
    
    Args:
        mock_request (Mock): Mocked request method to simulate API responses
        unifi_client (UnifiClient): Configured UniFi client instance for testing
        mock_device_response (dict): Predefined mock response containing device data
    
    Assertions:
        - Verifies one device is returned from `get_devices()`
        - Confirms returned devices are of type Device
        - Checks the MAC address matches the expected value
        - Validates `get_device()` returns a Device with the correct MAC address
    """
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
    """
    Test the client management methods of the UniFi Network API client.
    
    This test function verifies the functionality of client retrieval methods:
    - Checks the `get_clients()` method returns a list of Client objects
    - Validates the `get_client()` method retrieves a specific client by MAC address
    
    Args:
        mock_request (Mock): Mocked request method to simulate API responses
        unifi_client (UnifiClient): Configured UniFi client instance for testing
        mock_client_response (dict): Predefined mock response containing client data
    
    Assertions:
        - Verifies exactly one client is returned by `get_clients()`
        - Confirms returned clients are instances of the Client class
        - Checks the MAC address of retrieved clients matches the expected value
    """
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
    """
    Test the retrieval and validation of network configuration from the UniFi Network API.
    
    This test function verifies the `get_network_config()` method of the UniFi client by:
    - Mocking the API request response with predefined network configuration data
    - Retrieving network configuration for the "default" network
    - Asserting that the returned object is a NetworkConfiguration instance
    - Validating key network configuration properties such as name, purpose, enabled status, and subnet
    
    Parameters:
        mock_request (MagicMock): Mocked request method to simulate API calls
        unifi_client (UnifiClient): Configured UniFi client instance for testing
        mock_network_response (dict): Predefined mock network configuration response data
    
    Raises:
        AssertionError: If the network configuration does not match expected values
    """
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
    """
    Test the retrieval and validation of system health information from the UniFi Network API.
    
    This test function verifies the `get_system_health()` method of the UniFi client by:
    - Mocking the API request response with predefined system health data
    - Ensuring the returned object is an instance of SystemHealth
    - Checking that system health metrics are correctly parsed and match expected values
    
    Parameters:
        mock_request (MagicMock): Mocked request method to simulate API calls
        unifi_client (UnifiClient): Configured UniFi client instance for testing
        mock_system_response (dict): Predefined mock system health response data
    
    Assertions:
        - Returned health object is of type SystemHealth
        - System status is "ok"
        - CPU usage is 25.5%
        - Memory usage is 60.2%
        - Temperature is 45.3 degrees
    """
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
