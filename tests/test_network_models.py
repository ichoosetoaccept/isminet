"""Tests for network models."""

import pytest
from typing import Dict, Any, List
from pydantic import ValidationError

from isminet.models.network import NetworkConfiguration
from isminet.models.enums import DHCPMode

# Test data
VALID_NETWORK_CONFIG: Dict[str, Any] = {
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
            "untagged_ports": [1, 2, 3],
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


@pytest.mark.parametrize(
    "ipv6_config,expected_addresses",
    [
        (
            {
                "ipv6_ra_enabled": True,
                "ipv6_interface_type": "upstream",
                "ipv6_pd_prefixid": 0,
                "ipv6_addresses": ["2001:0db8:85a3:0000:0000:8a2e:0370:7334"],
            },
            ["2001:0db8:85a3:0000:0000:8a2e:0370:7334"],
        ),
        (
            {
                "ipv6_ra_enabled": True,
                "ipv6_interface_type": "upstream",
                "ipv6_pd_prefixid": 1,
                "ipv6_addresses": [
                    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                    "2001:0db8:85a3:0000:0000:8a2e:0370:7335",
                ],
            },
            [
                "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                "2001:0db8:85a3:0000:0000:8a2e:0370:7335",
            ],
        ),
    ],
)
def test_ipv6_configuration(
    ipv6_config: Dict[str, Any], expected_addresses: List[str]
) -> None:
    """Test IPv6 configuration with various valid configurations."""
    config = NetworkConfiguration(**{**VALID_NETWORK_CONFIG, **ipv6_config})
    assert (config.ipv6_addresses or []) == expected_addresses


@pytest.mark.parametrize(
    "invalid_ipv6_config,error_pattern",
    [
        (
            {"ipv6_addresses": ["not_an_ipv6_address", "also_invalid"]},
            "Invalid IPv6 address format",
        ),
        (
            {
                "ipv6_addresses": [
                    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                    "not_an_ipv6_address",
                ],
            },
            "Invalid IPv6 address format",
        ),
        (
            {
                "ipv6_ra_enabled": True,
                "ipv6_interface_type": "upstream",
                "ipv6_pd_prefixid": -1,
            },
            "Input should be greater than or equal to 0",
        ),
        (
            {
                "ipv6_ra_enabled": True,
                "ipv6_interface_type": "invalid",
                "ipv6_pd_prefixid": 0,
            },
            "IPv6 interface type must be 'upstream' or 'downstream'",
        ),
    ],
)
def test_invalid_ipv6_configuration(
    invalid_ipv6_config: Dict[str, Any], error_pattern: str
) -> None:
    """Test IPv6 configuration validation with invalid inputs."""
    with pytest.raises(ValidationError, match=error_pattern):
        NetworkConfiguration(**{**VALID_NETWORK_CONFIG, **invalid_ipv6_config})
