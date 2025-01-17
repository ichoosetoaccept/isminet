"""Tests for common validation patterns."""

from typing import Any, List, Optional, TypedDict

import pytest
from pydantic import Field, ValidationError

from isminet.models.base import UnifiBaseModel
from isminet.models.mixins import ValidationMixin


class TestModelDict(TypedDict, total=False):
    """Type for TestModel input data."""

    mac: str
    ip: Optional[str]
    netmask: Optional[str]
    mac_list: Optional[List[str]]
    version: Optional[str]
    percentage: Optional[float]
    non_negative: Optional[int]
    negative: Optional[int]
    range_value: Optional[int]


class TestModel(ValidationMixin, UnifiBaseModel):
    """Test model with common validation patterns."""

    mac: str = Field(description="MAC address")
    ip: Optional[str] = Field(None, description="IP address")
    netmask: Optional[str] = Field(None, description="Network mask")
    mac_list: Optional[List[str]] = Field(None, description="MAC address list")
    version: Optional[str] = Field(None, description="Version string")
    percentage: Optional[float] = Field(None, description="Percentage value")
    non_negative: Optional[int] = Field(None, description="Non-negative integer")
    negative: Optional[int] = Field(None, description="Negative integer")
    range_value: Optional[int] = Field(None, description="Value within range")


@pytest.mark.parametrize(
    "field,value,expected_value,description",
    [
        ("mac", "00:11:22:33:44:55", "00:11:22:33:44:55", "Valid MAC address"),
        ("ip", "192.168.1.1", "192.168.1.1", "Valid IPv4 address"),
        ("ip", "2001:db8::1", "2001:db8::1", "Valid IPv6 address"),
        ("netmask", "255.255.255.0", "255.255.255.0", "Valid netmask"),
        ("mac_list", ["00:11:22:33:44:55"], ["00:11:22:33:44:55"], "Valid MAC list"),
        ("version", "1.2.3", "1.2.3", "Valid version string"),
        ("percentage", 50.0, 50.0, "Valid percentage"),
        ("non_negative", 0, 0, "Valid non-negative integer"),
        ("negative", -1, -1, "Valid negative integer"),
        ("range_value", 5, 5, "Valid range value"),
    ],
)
def test_validation_valid_inputs(
    field: str, value: Any, expected_value: Any, description: str
) -> None:
    """Test validation with valid inputs."""
    data: TestModelDict = {"mac": "00:11:22:33:44:55"}  # Base required field
    data[field] = value  # type: ignore
    model = TestModel(**data)
    assert getattr(model, field) == expected_value, description


@pytest.mark.parametrize(
    "field,invalid_value,error_pattern",
    [
        ("mac", "invalid", "Invalid MAC address format"),
        ("ip", "invalid", "Invalid IPv4 address"),
        ("netmask", "invalid", "Invalid network mask"),
        ("mac_list", ["invalid"], "Invalid MAC address list"),
        ("version", "1.0", "Version must be in format x.y.z"),
        ("percentage", 101.0, "Percentage must be between 0 and 100"),
        ("percentage", -1.0, "Percentage must be between 0 and 100"),
        ("non_negative", -1, "Value must be non-negative"),
        ("negative", 0, "Value must be negative"),
        ("range_value", 11, "range_value must be between 0 and 10"),
    ],
)
def test_validation_invalid_inputs(
    field: str, invalid_value: Any, error_pattern: str
) -> None:
    """Test validation with invalid inputs."""
    data: TestModelDict = {"mac": "00:11:22:33:44:55"}  # Base required field
    data[field] = invalid_value  # type: ignore
    with pytest.raises(ValidationError, match=error_pattern):
        TestModel(**data)
