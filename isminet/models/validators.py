"""Common validators and fields for UniFi Network API models."""

from typing import Optional, Callable, Any
from ipaddress import IPv4Address, IPv6Address
import re
from pydantic import Field

MAC_PATTERN = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def validate_mac(v: Optional[str]) -> Optional[str]:
    """Validate MAC address format."""
    if v is None:
        return None
    if not MAC_PATTERN.match(v):
        raise ValueError("Invalid MAC address format")
    return v.lower()


def create_list_validator(
    validator_func: Callable[[str], Any],
    error_type: str,
    error_msg: str,
    transform_func: Callable[[str], str] = lambda x: x,
) -> Callable[[Optional[list[str]]], Optional[list[str]]]:
    """Create a validator for a list of values."""

    def validator(v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return None
        validated = []
        invalid = []
        for value in v:
            try:
                if not validator_func(transform_func(value)):
                    invalid.append(value)
                else:
                    validated.append(transform_func(value))
            except (ValueError, TypeError):
                invalid.append(value)
        if invalid:
            raise ValueError(error_msg)
        return validated

    return validator


# Create validators using the factory
validate_ip_list = create_list_validator(
    IPv4Address,
    "invalid_ip",
    "Invalid IPv4 address",
)

validate_ipv6_list = create_list_validator(
    IPv6Address,
    "invalid_ipv6",
    "Invalid IPv6 address",
)

validate_mac_list = create_list_validator(
    lambda x: bool(MAC_PATTERN.match(x)),
    "invalid_mac",
    "Invalid MAC address list",
    transform_func=str.lower,
)


def validate_ip(v: Optional[str]) -> Optional[str]:
    """Validate IP address format (IPv4 or IPv6)."""
    if v is None:
        return None
    try:
        # Try IPv4 first
        IPv4Address(v)
        return v
    except ValueError:
        try:
            # Try IPv6 if IPv4 fails
            IPv6Address(v)
            return v
        except ValueError:
            raise ValueError("Invalid IPv4 address")


def validate_version(v: Optional[str]) -> Optional[str]:
    """
    Validate firmware version string.

    Parameters:
        v: The version string to validate (e.g. '1.2.3')

    Returns:
        str: The validated version string

    Raises:
        ValueError: If version format is invalid (must be in format X.Y.Z where X,Y,Z are integers)
    """
    if v is None:
        return None
    if not VERSION_PATTERN.match(v):
        raise ValueError("Version must be in format x.y.z")
    return v


# Common field definitions
bytes_r_field = Field(None, description="Current bytes rate", ge=0)
tx_bytes_r_field = Field(None, description="Current transmit bytes rate", ge=0)
rx_bytes_r_field = Field(None, description="Current receive bytes rate", ge=0)
satisfaction_field = Field(None, description="Satisfaction score (0-100)", ge=0, le=100)
mac_field = Field(description="MAC address")
ip_field = Field(None, description="IP address")
site_id_field = Field(description="Site identifier")
version_field = Field(None, description="Version string")
