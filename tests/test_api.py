"""Tests for UniFi Network API client."""

import pytest
from unittest.mock import Mock, patch
from requests import Session
from requests.exceptions import ConnectionError

from isminet.clients.base import (
    APIError,
    AuthenticationError,
    BaseAPIClient,
    NotFoundError,
    PermissionError,
    ResponseValidationError,
)
from isminet.config import APIConfig
from isminet.models.base import UnifiBaseModel


def test_api_client_initialization():
    """Test API client initialization."""
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)
    assert client.config == config
    assert client.session is not None


def test_retry_mechanism():
    """Test retry mechanism for failed requests."""
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"data": []}

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = [
            ConnectionError("Connection failed"),
            ConnectionError("Connection failed"),
            mock_response,
        ]
        result = client.get("/test")
        assert result == {"data": []}
        assert mock_request.call_count == 3


def test_error_handling():
    """Test error handling for different status codes."""
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    error_cases = [
        (401, AuthenticationError, "Authentication failed"),
        (403, PermissionError, "Permission error"),
        (404, NotFoundError, "Resource not found"),
        (500, APIError, "HTTP 500"),
    ]

    for status_code, error_class, error_msg in error_cases:
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = status_code
        mock_response.json.return_value = {"message": "Error message"}

        with patch("requests.Session.request") as mock_request:
            mock_request.return_value = mock_response
            with pytest.raises(error_class) as exc_info:
                client.get("/test")
            assert error_msg in str(exc_info.value)


def test_request_exceptions():
    """Test handling of request exceptions."""
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = ConnectionError("Connection failed")
        with pytest.raises(APIError) as exc_info:
            client.get("/test")
        assert "Request failed" in str(exc_info.value)


def test_response_validation():
    """Test response validation against models."""
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    class TestModel(UnifiBaseModel):
        name: str
        value: int

    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"data": [{"name": "test", "value": "invalid"}]}

    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = mock_response
        with pytest.raises(ResponseValidationError) as exc_info:
            client.get("/test", response_model=TestModel)
        assert "Response validation failed" in str(exc_info.value)


def test_context_manager():
    """Test API client as context manager."""
    config = APIConfig(api_key="test_key", host="unifi.local")
    with BaseAPIClient(config) as client:
        # Session should be active inside context
        assert client.session is not None
        assert isinstance(client.session, Session)
    # Session should be closed after context
    assert client.session is None
