import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from isminet.models import Site, BaseResponse

# Load test data from API response examples
DOCS_DIR = Path(__file__).parent.parent / "docs" / "api_responses"
with open(DOCS_DIR / "sites_response.json") as f:
    SITES_RESPONSE = json.load(f)


def test_site_model_valid():
    """Test that the Site model can parse a valid site response."""
    site_data = SITES_RESPONSE["data"][0]
    site = Site(**site_data)

    # Test that all fields are correctly parsed
    assert site.name == "default"
    assert site.desc == "Default"
    assert site.id == "66450709e650bd21e774c55c"
    assert site.device_count == 3
    assert site.anonymous_id == "22263757-6495-476b-b62c-8e7b46cc2c73"
    assert site.external_id == "88f7af54-98f8-306a-a1c7-c9349722b1f6"
    assert site.attr_no_delete is True
    assert site.attr_hidden_id == "default"
    assert site.role == "admin"
    assert site.role_hotspot is False


def test_site_model_minimal():
    """Test that the Site model works with only required fields."""
    minimal_site = {
        "name": "test-site",
        "desc": "Test Site",
        "_id": "test123",
        "device_count": 0,
    }
    site = Site(**minimal_site)

    # Test required fields
    assert site.name == "test-site"
    assert site.desc == "Test Site"
    assert site.id == "test123"
    assert site.device_count == 0

    # Test optional fields are None
    assert site.anonymous_id is None
    assert site.external_id is None
    assert site.attr_no_delete is None
    assert site.attr_hidden_id is None
    assert site.role is None
    assert site.role_hotspot is None


def test_site_model_invalid():
    """Test that the Site model properly validates input data."""
    invalid_sites = [
        # Missing required field
        {
            "name": "test-site",
            "desc": "Test Site",
            "_id": "test123",
            # missing device_count
        },
        # Wrong type for device_count
        {
            "name": "test-site",
            "desc": "Test Site",
            "_id": "test123",
            "device_count": "not-a-number",
        },
        # Empty string for required field
        {"name": "", "desc": "Test Site", "_id": "test123", "device_count": 0},
    ]

    for invalid_site in invalid_sites:
        with pytest.raises(ValidationError):
            Site(**invalid_site)


def test_base_response_with_sites():
    """Test that the BaseResponse model works with Site data."""
    response = BaseResponse[Site](**SITES_RESPONSE)

    assert response.meta.rc == "ok"
    assert len(response.data) == 1

    site = response.data[0]
    assert isinstance(site, Site)
    assert site.name == "default"
    assert site.device_count == 3
