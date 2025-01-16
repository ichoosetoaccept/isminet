"""Common validators and fields for UniFi Network API models."""

from typing import Optional, List, Callable, Any
from ipaddress import IPv4Address, IPv6Address
import re
from pydantic import Field
from pydantic_core import PydanticCustomError

MAC_PATTERN = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")


def validate_mac(v: Optional[str]) -> Optional[str]:
    """Validate MAC address format."""
    if v is None:
        return None
    if not MAC_PATTERN.match(v):
        raise PydanticCustomError(
            "invalid_mac",
            "Invalid MAC address format",
            {},
        )
    return v.lower()


def create_list_validator(
    validator_func: Callable[[str], Any],
    error_type: str,
    error_msg: str,
    transform_func: Optional[Callable[[str], str]] = None,
) -> Callable[[Optional[List[str]]], Optional[List[str]]]:
    """
    Create a validator for lists of values.

    Args:
        validator_func: Function to validate each item
        error_type: Type of error to raise on validation failure
        error_msg: Error message template
        transform_func: Optional function to transform valid values

    Returns:
        A validator function for lists of values
    """

    def validate_list(v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return None

        validated = []
        errors = []

        for item in v:
            try:
                validator_func(item)
                validated.append(transform_func(item) if transform_func else item)
            except ValueError:
                errors.append(item)

        if errors:
            raise PydanticCustomError(
                error_type,
                error_msg,
                {"values": ", ".join(errors)},
            )

        return validated

    return validate_list


# Create validators using the factory
validate_ip_list = create_list_validator(
    IPv4Address, "invalid_ip", "Invalid IPv4 addresses: {values}"
)

validate_ipv6_list = create_list_validator(
    IPv6Address, "invalid_ipv6", "Invalid IPv6 addresses: {values}"
)

validate_mac_list = create_list_validator(
    lambda x: bool(MAC_PATTERN.match(x)),
    "invalid_mac",
    "Invalid MAC addresses: {values}",
    transform_func=str.lower,
)


def validate_ip(v: Optional[str]) -> Optional[str]:
    """Validate IPv4 address format."""
    if v is None:
        return None
    try:
        IPv4Address(v)
        return v
    except ValueError:
        raise PydanticCustomError(
            "invalid_ip",
            "Invalid IPv4 address",
            {},
        )


def validate_ip_list(v: Optional[List[str]]) -> Optional[List[str]]:
    """
    Validate a list of IPv4 addresses.
    
    Validates each IPv4 address in the input list using the IPv4Address class. 
    Ensures all addresses are valid IPv4 format.
    
    Parameters:
        v (Optional[List[str]]): A list of IP address strings to validate
    
    Returns:
        Optional[List[str]]: The original list of IP addresses if all are valid, 
        or None if the input is None
    
    Raises:
        PydanticCustomError: If any IP address in the list is invalid, 
        with error details specifying the problematic address
    """
    if v is None:
        return None
    validated = []
    for addr in v:
        try:
            IPv4Address(addr)
            validated.append(addr)
        except ValueError:
            raise PydanticCustomError(
                "invalid_ip",
                "Invalid IPv4 address: {addr}",
                {"addr": addr},
            )
    return validated


def validate_ipv6_list(v: Optional[List[str]]) -> Optional[List[str]]:
    """
    Validate a list of IPv6 addresses.
    
    Parameters:
        v (Optional[List[str]]): A list of IPv6 address strings to validate
    
    Returns:
        Optional[List[str]]: A list of validated IPv6 addresses, or None if input is None
    
    Raises:
        PydanticCustomError: If any IPv6 address in the list is invalid, with error type "invalid_ipv6"
    
    Examples:
        >>> validate_ipv6_list(["2001:0db8:85a3:0000:0000:8a2e:0370:7334"])
        ['2001:0db8:85a3:0000:0000:8a2e:0370:7334']
        >>> validate_ipv6_list(None) is None
        True
    """
    if v is None:
        return None
    validated = []
    for addr in v:
        try:
            IPv6Address(addr)
            validated.append(addr)
        except ValueError:
            raise PydanticCustomError(
                "invalid_ipv6",
                "Invalid IPv6 address: {addr}",
                {"addr": addr},
            )
    return validated


def validate_version(v: Optional[str]) -> Optional[str]:
    """Validate version format."""
    if v is None:
        return None
    if not re.match(r"^\d+\.\d+\.\d+$", v):
        raise PydanticCustomError(
            "invalid_version",
            "Invalid version format",
            {},
        )
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
