# test_api.py
"""Tests for API client functionality."""

import pytest
from unittest.mock import Mock, patch
import requests
from requests.exceptions import Timeout, ConnectionError, SSLError

from isminet.clients.base import (
    BaseAPIClient,
    APIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ServerError,
    ResponseValidationError,
)
from isminet.config import APIConfig
from isminet.models.base import UnifiBaseModel


class TestModel(UnifiBaseModel):
    """Test model for response validation."""

    name: str
    value: int


def test_api_client_initialization():
    """Test API client initialization."""
    config = APIConfig(api_key="test-key", host="example.com")
    client = BaseAPIClient(config)

    assert client.config == config
    assert client.session.headers.get("X-API-KEY") == "test-key"
    assert client.session.verify == config.verify_ssl


def test_retry_mechanism():
    """Test request retry mechanism."""
    config = APIConfig(api_key="test-key", host="example.com")
    client = BaseAPIClient(config)

    mock_response = Mock(spec=requests.Response)
    mock_response.ok = True
    mock_response.json.return_value = {"data": []}

    with patch("requests.Session.request") as mock_request:
        # Simulate two failures then success
        mock_request.side_effect = [
            ConnectionError("Connection failed"),
            ConnectionError("Connection failed"),
            mock_response,
        ]

        with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
            result = client.get("test")
            assert result == {"data": []}
            assert mock_request.call_count == 3
            assert mock_sleep.call_count == 2  # Should sleep twice between retries


def test_error_handling():
    """Test different error scenarios."""
    config = APIConfig(api_key="test-key", host="example.com")
    client = BaseAPIClient(config)

    mock_response = Mock(spec=requests.Response)
    mock_response.ok = False
    mock_response.status_code = 401
    mock_response.json.return_value = {"meta": {"msg": "Unauthorized"}}

    with patch("requests.Session.request", return_value=mock_response):
        with pytest.raises(AuthenticationError):
            client.get("test")

    mock_response.status_code = 429
    with patch("requests.Session.request", return_value=mock_response):
        with pytest.raises(RateLimitError):
            client.get("test")

    mock_response.status_code = 404
    with patch("requests.Session.request", return_value=mock_response):
        with pytest.raises(NotFoundError):
            client.get("test")

    mock_response.status_code = 500
    with patch("requests.Session.request", return_value=mock_response):
        with pytest.raises(ServerError):
            client.get("test")


def test_request_exceptions():
    """Test handling of request exceptions."""
    config = APIConfig(api_key="test-key", host="example.com")
    client = BaseAPIClient(config)

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = Timeout("Request timed out")
        with pytest.raises(APIError, match="Request timed out"):
            client.get("test")

        mock_request.side_effect = ConnectionError("Connection failed")
        with pytest.raises(APIError, match="Connection failed"):
            client.get("test")

        mock_request.side_effect = SSLError("SSL verification failed")
        with pytest.raises(APIError, match="SSL verification failed"):
            client.get("test")


def test_response_validation():
    """Test response data validation."""
    config = APIConfig(api_key="test-key", host="example.com")
    client = BaseAPIClient(config)

    mock_response = Mock(spec=requests.Response)
    mock_response.ok = True
    mock_response.json.return_value = {"data": [{"name": "test", "value": 42}]}

    with patch("requests.Session.request", return_value=mock_response):
        # Valid response data
        result = client.get("test", response_model=TestModel)
        assert isinstance(result, TestModel)
        assert result.name == "test"
        assert result.value == 42

        # Invalid response data
        mock_response.json.return_value = {
            "data": [{"name": "test", "value": "not_an_int"}]
        }
        with pytest.raises(ResponseValidationError):
            client.get("test", response_model=TestModel)


def test_context_manager():
    """Test client as context manager."""
    config = APIConfig(api_key="test-key", host="example.com")

    with patch("requests.Session.close") as mock_close:
        with BaseAPIClient(config) as client:
            assert isinstance(client, BaseAPIClient)
            assert client.session is not None

        # Verify session was closed
        mock_close.assert_called_once()
