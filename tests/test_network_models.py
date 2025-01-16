"""Tests for network configuration models."""

import pytest
from pydantic import ValidationError

from isminet.models.network import (
    DHCPConfiguration,
    VLANConfiguration,
    NetworkConfiguration,
)
from isminet.models.enums import DHCPMode, IGMPMode

# Test data
VALID_DHCP_CONFIG = {
    "mode": DHCPMode.SERVER,
    "enabled": True,
    "start": "192.168.1.100",
    "end": "192.168.1.200",
    "lease_time": 86400,
    "dns": ["8.8.8.8", "8.8.4.4"],
    "gateway_ip": "192.168.1.1",
}

VALID_VLAN_CONFIG = {
    "vlan_id": 100,
    "name": "IoT VLAN",
    "enabled": True,
    "subnet": "192.168.100.0",
    "dhcp": VALID_DHCP_CONFIG,
    "igmp_snooping": True,
    "igmp_mode": IGMPMode.SNOOPING,
    "tagged_ports": [1, 2, 3],
    "untagged_ports": [4, 5, 6],
}

VALID_NETWORK_CONFIG = {
    "name": "Main Network",
    "purpose": "corporate",
    "enabled": True,
    "subnet": "192.168.1.0",
    "vlan_enabled": True,
    "vlans": [VALID_VLAN_CONFIG],
    "dhcp": VALID_DHCP_CONFIG,
    "igmp_snooping": True,
    "igmp_mode": IGMPMode.SNOOPING,
}


def test_dhcp_configuration():
    """
    Test the validation and configuration of DHCPConfiguration instances.
    
    This test function verifies the behavior of DHCPConfiguration by:
    - Validating a complete, valid DHCP server configuration
    - Checking the handling of disabled DHCP mode
    - Ensuring required fields are present when DHCP is enabled
    - Confirming that invalid IP addresses raise validation errors
    
    Parameters:
        None
    
    Raises:
        ValidationError: When configuration is invalid due to missing fields or incorrect IP addresses
    """
    # Test valid configuration
    config = DHCPConfiguration(**VALID_DHCP_CONFIG)
    assert config.mode == DHCPMode.SERVER
    assert config.enabled is True
    assert config.start == "192.168.1.100"
    assert config.dns == ["8.8.8.8", "8.8.4.4"]

    # Test disabled DHCP
    config = DHCPConfiguration(mode=DHCPMode.DISABLED, enabled=False)
    assert config.mode == DHCPMode.DISABLED
    assert config.enabled is False

    # Test missing required fields in server mode
    with pytest.raises(ValidationError):
        DHCPConfiguration(mode=DHCPMode.SERVER, enabled=True)

    # Test invalid IP addresses
    with pytest.raises(ValidationError):
        DHCPConfiguration(**{**VALID_DHCP_CONFIG, "start": "invalid.ip"})
    with pytest.raises(ValidationError):
        DHCPConfiguration(**{**VALID_DHCP_CONFIG, "dns": ["invalid.ip"]})


def test_vlan_configuration():
    """
    Test the validation rules for VLAN (Virtual Local Area Network) configurations.
    
    This test function validates the VLANConfiguration model by:
    - Verifying successful creation with a valid configuration
    - Checking boundary conditions for VLAN ID (must be between 1 and 4094)
    - Ensuring that tagged and untagged ports do not overlap
    
    Parameters:
        None
    
    Raises:
        ValidationError: If VLAN configuration violates validation rules
            - VLAN ID is less than 1 or greater than 4094
            - Tagged and untagged ports have common interfaces
    """
    # Test valid configuration
    config = VLANConfiguration(**VALID_VLAN_CONFIG)
    assert config.vlan_id == 100
    assert config.name == "IoT VLAN"
    assert config.subnet == "192.168.100.0"
    assert isinstance(config.dhcp, DHCPConfiguration)

    # Test VLAN ID boundaries
    with pytest.raises(ValidationError):
        VLANConfiguration(**{**VALID_VLAN_CONFIG, "vlan_id": 0})
    with pytest.raises(ValidationError):
        VLANConfiguration(**{**VALID_VLAN_CONFIG, "vlan_id": 4095})

    # Test port validation
    with pytest.raises(ValidationError):
        VLANConfiguration(
            **{
                **VALID_VLAN_CONFIG,
                "tagged_ports": [1, 2],
                "untagged_ports": [2, 3],
            }
        )


def test_network_configuration():
    """
    Test the validation and configuration of network settings.
    
    This test function validates the NetworkConfiguration model by:
    - Verifying correct initialization with valid network configuration
    - Checking validation for invalid purpose
    - Ensuring VLAN configuration constraints are enforced
    - Validating duplicate VLAN ID detection
    - Testing IPv6-specific configuration parameters
    
    Parameters:
        None
    
    Raises:
        ValidationError: If network configuration fails validation checks
    """
    # Test valid configuration
    config = NetworkConfiguration(**VALID_NETWORK_CONFIG)
    assert config.name == "Main Network"
    assert config.purpose == "corporate"
    assert config.subnet == "192.168.1.0"
    assert isinstance(config.vlans[0], VLANConfiguration)
    assert isinstance(config.dhcp, DHCPConfiguration)

    # Test invalid purpose
    with pytest.raises(ValidationError):
        NetworkConfiguration(**{**VALID_NETWORK_CONFIG, "purpose": "invalid"})

    # Test VLAN validation
    with pytest.raises(ValidationError):
        NetworkConfiguration(
            **{**VALID_NETWORK_CONFIG, "vlan_enabled": True, "vlans": None}
        )

    # Test duplicate VLAN IDs
    duplicate_vlan = VALID_VLAN_CONFIG.copy()
    with pytest.raises(ValidationError):
        NetworkConfiguration(
            **{
                **VALID_NETWORK_CONFIG,
                "vlans": [VALID_VLAN_CONFIG, duplicate_vlan],
            }
        )

    # Test IPv6 configuration
    config = NetworkConfiguration(
        **{
            **VALID_NETWORK_CONFIG,
            "ipv6_ra_enabled": True,
            "ipv6_interface_type": "upstream",
            "ipv6_pd_prefixid": 0,
        }
    )
    assert config.ipv6_ra_enabled is True
    assert config.ipv6_interface_type == "upstream"
    assert config.ipv6_pd_prefixid == 0
