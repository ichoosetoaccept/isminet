"""Tests for UniFi Network API models."""

import json
from pathlib import Path
from typing import Any, Dict, cast

import pytest
from pydantic import ValidationError

from isminet.models.base import BaseResponse
from isminet.models import Site

# Load test data from API response examples
DOCS_DIR = Path(__file__).parent.parent / "docs" / "api_responses"
with open(DOCS_DIR / "sites_response.json") as f:
    SITES_RESPONSE = cast(Dict[str, Any], json.load(f))


@pytest.mark.parametrize(
    "field,expected_value",
    [
        ("name", "default"),
        ("desc", "Default"),
        ("id", "66450709e650bd21e774c55c"),
        ("device_count", 3),
        ("anonymous_id", "22263757-6495-476b-b62c-8e7b46cc2c73"),
        ("external_id", "88f7af54-98f8-306a-a1c7-c9349722b1f6"),
        ("attr_no_delete", True),
        ("attr_hidden_id", "default"),
        ("role", "admin"),
        ("role_hotspot", False),
    ],
)
def test_site_model_field_values(field: str, expected_value: Any) -> None:
    """Test that the Site model correctly parses each field."""
    site_data = cast(Dict[str, Any], SITES_RESPONSE["data"][0])
    site = Site(**site_data)
    assert getattr(site, field) == expected_value


@pytest.mark.parametrize(
    "field,expected_value",
    [
        ("name", "test-site"),
        ("desc", "Test Site"),
        ("id", "123456789"),
        ("device_count", 0),
        ("anonymous_id", None),
        ("external_id", None),
        ("attr_no_delete", None),
        ("attr_hidden_id", None),
        ("role", None),
        ("role_hotspot", None),
    ],
)
def test_site_model_minimal_field_values(field: str, expected_value: Any) -> None:
    """Test that the Site model correctly handles minimal data for each field."""
    site_data: Dict[str, Any] = {
        "name": "test-site",
        "desc": "Test Site",
        "_id": "123456789",
        "device_count": 0,
    }
    site = Site(**site_data)
    assert getattr(site, field) == expected_value


@pytest.mark.parametrize(
    "invalid_data,error_pattern",
    [
        (
            {"name": "test-site", "desc": "Test Site"},
            "Field required",
        ),
        (
            {
                "name": "test-site",
                "desc": "Test Site",
                "_id": "123456789",
                "device_count": -1,
            },
            "Input should be greater than or equal to 0",
        ),
        (
            {"name": "", "desc": "Test Site", "_id": "123456789", "device_count": 0},
            "String should have at least 1 character",
        ),
    ],
)
def test_site_model_invalid(invalid_data: Dict[str, Any], error_pattern: str) -> None:
    """Test that the Site model properly validates input data."""
    with pytest.raises(ValidationError, match=error_pattern):
        Site(**invalid_data)


@pytest.mark.parametrize(
    "field,expected_value,expected_type",
    [
        ("meta.rc", "ok", str),
        ("data", 1, len),  # Check length of data list
        ("data[0].name", "default", str),
        ("data[0]", Site, Site),  # Check type of first data item
    ],
)
def test_base_response_fields(
    field: str, expected_value: Any, expected_type: Any
) -> None:
    """Test that BaseResponse correctly parses all fields."""
    response = BaseResponse[Site](**SITES_RESPONSE)

    # Handle nested field access
    value: Any
    if field == "data" and expected_type == len:
        value = len(response.data)
    elif "." in field:
        obj = response
        for part in field.split("."):
            obj = getattr(obj, part)
        value = obj
    elif "[" in field:
        # Handle array access with type checking
        array_field = field.split("[")[0]
        data = getattr(response, array_field)
        index = int(field.split("[")[1].split("]")[0])

        if "." in field:
            attr = field.split(".")[1]
            value = getattr(data[index], attr)
        else:
            value = data[index]
    else:
        value = getattr(response, field)

    if expected_type == len:
        assert value == expected_value
    elif expected_type == Site:
        assert isinstance(value, Site)
    else:
        assert isinstance(value, expected_type)
        assert value == expected_value


@pytest.mark.parametrize(
    "invalid_data,error_pattern",
    [
        (
            {**SITES_RESPONSE, "meta": {"rc": "error"}},
            "Response code must be 'ok'",
        ),
        (
            {**SITES_RESPONSE, "data": []},
            "List should have at least 1 item",
        ),
    ],
)
def test_base_response_invalid(
    invalid_data: Dict[str, Any], error_pattern: str
) -> None:
    """Test that BaseResponse validation fails with invalid data."""
    with pytest.raises(ValidationError, match=error_pattern):
        BaseResponse[Site](**invalid_data)
