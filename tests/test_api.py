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
    assert client.session is not None


def test_retry_mechanism():
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
        mock_request.side_effect = ConnectionError("Connection failed")
        with pytest.raises(APIError) as exc_info:
            client.get("/test")
        assert "Request failed" in str(exc_info.value)


def test_response_validation():
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
        assert client.session is not None
        assert isinstance(client.session, Session)
    # Session should be closed after context
    assert client.session is None
