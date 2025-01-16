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

import pytest
from unittest.mock import Mock, patch
import requests

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


def test_api_client_initialization() -> None:
    """
    Test the initialization of the BaseAPIClient with a given configuration.

    This test verifies that:
        1. The client is created with the correct configuration
        2. A session is successfully initialized

    Args:
        None

    Raises:
        AssertionError: If the client configuration or session is not correctly set up
    """
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)
    assert client.config == config
    assert isinstance(client.session, requests.Session)


def test_retry_mechanism() -> None:
    """
    Test the retry mechanism of the BaseAPIClient when handling connection failures.

    This test verifies that the client attempts to retry a request multiple times
    when encountering connection errors, ultimately succeeding on the third attempt.

    Parameters:
        None

    Raises:
        AssertionError: If the retry mechanism does not function as expected

    Behavior:
        - Simulates two consecutive connection failures
        - Checks that the request is attempted three times
        - Confirms that the final request returns the expected response
    """
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    mock_response = Mock()
    mock_response.json.return_value = {"data": [{"id": 1}]}
    mock_response.status_code = 200

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = [
            requests.ConnectionError(),
            requests.ConnectionError(),
            mock_response,
        ]
        result = client.get("/test")
        assert result == {"data": [{"id": 1}]}
        assert mock_request.call_count == 3


def test_error_handling() -> None:
    """
    Test the error handling capabilities of the BaseAPIClient for various HTTP status codes.

    This test verifies that the client correctly raises specific exceptions based on different HTTP status codes. It checks the following error scenarios:
    - 401 (Unauthorized): Raises AuthenticationError
    - 403 (Forbidden): Raises PermissionError
    - 404 (Not Found): Raises NotFoundError
    - 500 (Internal Server Error): Raises generic APIError

    Parameters:
        None

    Raises:
        AssertionError: If the expected exceptions are not raised or do not contain the correct error messages
        Various custom exceptions (AuthenticationError, PermissionError, NotFoundError, APIError):
            Depending on the mocked HTTP status code
    """
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    mock_response = Mock()
    mock_response.json.return_value = {"meta": {"msg": "Error message"}}

    with patch("requests.Session.request") as mock_request:
        # Test 401 Unauthorized
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        with pytest.raises(AuthenticationError):
            client.get("/test")

        # Test 403 Forbidden
        mock_response.status_code = 403
        with pytest.raises(PermissionError):
            client.get("/test")

        # Test 404 Not Found
        mock_response.status_code = 404
        with pytest.raises(NotFoundError):
            client.get("/test")

        # Test 500 Internal Server Error
        mock_response.status_code = 500
        with pytest.raises(APIError):
            client.get("/test")


def test_request_exceptions() -> None:
    """
    Test the handling of request exceptions in the BaseAPIClient.

    This test verifies that when a ConnectionError occurs during a request,
    the client raises an APIError with an appropriate error message.

    Args:
        None

    Raises:
        APIError: When a connection error occurs during the request
    """
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = requests.ConnectionError()
        with pytest.raises(APIError):
            client.get("/test")


class TestModel(UnifiBaseModel):
    """Test model for response validation."""

    id: int
    name: str


def test_response_validation() -> None:
    """
    Test the response validation mechanism of the BaseAPIClient when the response data does not conform to the expected model.

    This test verifies that the client raises a ResponseValidationError when the JSON response contains data
    that fails type validation against a specified Pydantic model.

    Parameters:
        None

    Raises:
        ResponseValidationError: When the response data does not match the expected model's type constraints
    """
    config = APIConfig(api_key="test_key", host="unifi.local")
    client = BaseAPIClient(config)

    mock_response = Mock()
    mock_response.json.return_value = {"data": [{"id": "invalid", "name": 123}]}
    mock_response.status_code = 200

    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = mock_response
        with pytest.raises(ResponseValidationError):
            client.get("/test", response_model=TestModel)


def test_context_manager() -> None:
    """
    Test the context manager behavior of the BaseAPIClient.

    Verifies that:
        - A session is created and active when entering the context
        - The session is an instance of requests.Session
        - The session is closed and set to None when exiting the context

    Parameters:
        None

    Raises:
        AssertionError: If session management does not behave as expected
    """
    config = APIConfig(api_key="test_key", host="unifi.local")
    with BaseAPIClient(config) as client:
        # Session should be active inside context
        assert isinstance(client.session, requests.Session)

    # Session should be closed after context
    assert client.session is None
