"""
Tests for UniFi Network API client.

This module contains unit tests for the BaseAPIClient class, covering:
- Client initialization and configuration
- Retry mechanism for failed requests
- HTTP error handling and custom exceptions
- Response validation using Pydantic models
- Context manager implementation

All tests use mocking to avoid actual API calls.
"""

from typing import List, Optional, Type, Dict, Any, Union
import pytest
from requests import ConnectionError, Response
from unittest.mock import Mock, patch, MagicMock

from isminet.clients.base import (
    APIConfig,
    BaseAPIClient,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    APIError,
    ResponseValidationError,
)
from isminet.models.base import UnifiBaseModel


@pytest.mark.parametrize(
    "config_data,expected_error",
    [
        ({"api_key": "", "host": "unifi.local"}, "API key cannot be empty"),
        ({"api_key": "test_key", "host": ""}, "Host cannot be empty"),
        (
            {"api_key": "test_key", "host": "unifi.local", "port": -1},
            "Port must be between 1 and 65535",
        ),
        (
            {"api_key": "test_key", "host": "unifi.local", "port": 65536},
            "Port must be between 1 and 65535",
        ),
    ],
)
def test_api_client_initialization_errors(
    config_data: Dict[str, Any], expected_error: str
) -> None:
    """Test that API client initialization fails with invalid configuration."""
    with pytest.raises(ValueError, match=expected_error):
        config = APIConfig(**config_data)
        BaseAPIClient(config)


def test_api_client_initialization_optional_params() -> None:
    """Test API client initialization with optional parameters."""
    config = APIConfig(
        api_key="test_key",
        host="unifi.local",
        port=8443,
        site="default",
        verify_ssl=False,
    )
    client = BaseAPIClient(config)

    assert client.config.api_key == "test_key"
    assert client.config.host == "unifi.local"
    assert client.config.port == 8443
    assert client.config.site == "default"
    assert client.config.verify_ssl is False

    # Test session initialization
    assert client.session is not None
    assert client.session.verify is False
    assert "X-API-Key" in client.session.headers
    assert client.session.headers["X-API-Key"] == "test_key"


@pytest.mark.slow
def test_retry_mechanism() -> None:
    """Test that retry mechanism works correctly."""
    config = APIConfig(api_key="test", host="localhost")
    client = BaseAPIClient(config)

    # Mock a connection error that succeeds after 2 retries
    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = [
            ConnectionError("Connection failed"),
            ConnectionError("Connection failed"),
            MagicMock(ok=True, json=lambda: {"data": []}),
        ]

        response: Union[Dict[str, Any], List[Any]] = client.get("/test")
        assert response == {"data": []}
        assert mock_request.call_count == 3


@pytest.mark.parametrize(
    "status_code,expected_exception,error_msg",
    [
        (401, AuthenticationError, "Authentication failed"),
        (403, PermissionError, "Permission denied"),
        (404, NotFoundError, "Resource not found"),
        (500, APIError, "Internal server error"),
        (502, APIError, "Bad gateway"),
        (503, APIError, "Service unavailable"),
    ],
)
def test_error_handling(
    status_code: int, expected_exception: Type[Exception], error_msg: str
) -> None:
    """Test that HTTP errors are properly converted to custom exceptions."""
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    mock_response = Mock(spec=Response)
    mock_response.status_code = status_code
    mock_response.ok = False
    mock_response.text = error_msg

    with patch("requests.Session.request", return_value=mock_response):
        with pytest.raises(expected_exception, match=error_msg):
            client.get("/test")


class NestedModel(UnifiBaseModel):
    """Test nested model for response validation."""

    value: int
    description: Optional[str] = None


class ArrayModel(UnifiBaseModel):
    """Test array model for response validation."""

    items: List[str]


class TestModel(UnifiBaseModel):
    """Test model for response validation."""

    id: int
    name: str
    tags: List[str] = []
    nested: Optional[NestedModel] = None
    arrays: Optional[List[ArrayModel]] = None


def test_response_validation() -> None:
    """Test response validation using Pydantic models."""
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    # Test valid response
    valid_response = {
        "data": [
            {
                "id": 1,
                "name": "Test",
                "tags": ["tag1", "tag2"],
                "nested": {"value": 42, "description": "nested"},
                "arrays": [{"items": ["item1", "item2"]}],
            }
        ]
    }

    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = valid_response

    with patch("requests.Session.request", return_value=mock_response):
        result = client.get("/test", response_model=TestModel)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TestModel)
        assert result[0].id == 1
        assert result[0].name == "Test"
        assert result[0].tags == ["tag1", "tag2"]
        assert result[0].nested is not None
        assert result[0].nested.value == 42
        assert result[0].nested.description == "nested"
        assert result[0].arrays is not None
        assert len(result[0].arrays) == 1
        assert result[0].arrays[0].items == ["item1", "item2"]

    # Test invalid response
    invalid_response = {
        "data": [
            {
                "id": "not_an_integer",  # Should be an integer
                "name": "Test",
            }
        ]
    }

    mock_response.json.return_value = invalid_response

    with patch("requests.Session.request", return_value=mock_response):
        with pytest.raises(ResponseValidationError):
            client.get("/test", response_model=TestModel)

    # Test missing required field
    missing_field_response = {
        "data": [
            {
                "id": 1,
                # Missing required 'name' field
            }
        ]
    }

    mock_response.json.return_value = missing_field_response

    with patch("requests.Session.request", return_value=mock_response):
        with pytest.raises(ResponseValidationError):
            client.get("/test", response_model=TestModel)

    # Test invalid nested model
    invalid_nested_response = {
        "data": [
            {
                "id": 1,
                "name": "Test",
                "nested": {
                    # Missing required 'value' field
                    "description": "nested",
                },
            }
        ]
    }

    mock_response.json.return_value = invalid_nested_response

    with patch("requests.Session.request", return_value=mock_response):
        with pytest.raises(ResponseValidationError):
            client.get("/test", response_model=TestModel)

    # Test invalid array model
    invalid_array_response = {
        "data": [
            {
                "id": 1,
                "name": "Test",
                "arrays": [
                    {
                        # Missing required 'items' field
                    }
                ],
            }
        ]
    }

    mock_response.json.return_value = invalid_array_response

    with patch("requests.Session.request", return_value=mock_response):
        with pytest.raises(ResponseValidationError):
            client.get("/test", response_model=TestModel)


def test_context_manager() -> None:
    """Test that context manager properly closes session."""
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    with client:
        assert client.session is not None
        # Make a request to verify session is active
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {"data": []}

        with patch("requests.Session.request", return_value=mock_response):
            client.get("/test")

    # Try to make a request after context exit to verify session is closed
    with pytest.raises(RuntimeError, match="Session is closed"):
        client.get("/test")
