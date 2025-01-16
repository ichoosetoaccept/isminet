"""Base API client implementation."""

import logging
from typing import Any, TypeVar, Optional, Type, cast
from functools import wraps

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, SSLError
from pydantic import ValidationError as PydanticValidationError

from ..config import APIConfig
from ..models.base import BaseResponse, UnifiBaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for response models
T = TypeVar("T", bound=UnifiBaseModel)


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, response: Optional[requests.Response] = None):
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code if response else None
        self.error_data = None
        if response:
            try:
                self.error_data = response.json()
            except ValueError:
                pass


class AuthenticationError(APIError):
    """Raised when authentication fails."""


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""


class ValidationError(APIError):
    """Raised when request validation fails."""


class NotFoundError(APIError):
    """Raised when requested resource is not found."""


class ServerError(APIError):
    """Raised when server returns 5xx error."""


class ResponseValidationError(ValidationError):
    """Raised when response validation fails."""

    def __init__(
        self,
        message: str,
        validation_error: PydanticValidationError,
        response: Optional[requests.Response] = None,
    ):
        super().__init__(message, response)
        self.validation_error = validation_error


def with_retry(max_retries: int = 3, backoff_factor: float = 0.5):
    """Decorator for retrying failed API requests.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Delay multiplier between retries
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, Timeout) as e:
                    last_error = e
                    if attempt == max_retries:
                        break
                    delay = backoff_factor * (2**attempt)
                    logger.warning(
                        "Request failed (attempt %d/%d). Retrying in %.1f seconds...",
                        attempt + 1,
                        max_retries,
                        delay,
                    )
                    import time

                    time.sleep(delay)
                except (AuthenticationError, ValidationError, NotFoundError):
                    # Don't retry client errors
                    raise
            raise APIError(
                f"Request failed after {max_retries} retries: {str(last_error)}"
            )

        return wrapper

    return decorator


class BaseAPIClient:
    """Base implementation for UniFi Network API client."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize API client.

        Args:
            config: API configuration
        """
        self.config = config
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create and configure requests session.

        Returns:
            Configured requests Session
        """
        session = requests.Session()

        # Set default headers
        session.headers.update(self.config.get_headers())

        # Configure SSL verification
        session.verify = self.config.verify_ssl
        if not self.config.verify_ssl:
            # Disable SSL warning if verification is disabled
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return session

    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error responses based on status code.

        Args:
            response: Response object from request

        Raises:
            AuthenticationError: For 401/403 errors
            RateLimitError: For 429 errors
            ValidationError: For 400/422 errors
            NotFoundError: For 404 errors
            ServerError: For 5xx errors
            APIError: For other errors
        """
        error_msg = "API request failed"
        try:
            error_data = response.json()
            if "meta" in error_data and "msg" in error_data["meta"]:
                error_msg = error_data["meta"]["msg"]
        except ValueError:
            error_msg = response.text or error_msg

        if response.status_code in (401, 403):
            raise AuthenticationError(f"Authentication failed: {error_msg}", response)
        elif response.status_code == 429:
            raise RateLimitError(f"Rate limit exceeded: {error_msg}", response)
        elif response.status_code in (400, 422):
            raise ValidationError(f"Request validation failed: {error_msg}", response)
        elif response.status_code == 404:
            raise NotFoundError(f"Resource not found: {error_msg}", response)
        elif 500 <= response.status_code < 600:
            raise ServerError(f"Server error: {error_msg}", response)
        else:
            raise APIError(f"Unexpected error: {error_msg}", response)

    def _validate_response(
        self, response_data: dict[str, Any], response_model: Type[T]
    ) -> T:
        """Validate response data against expected model.

        Args:
            response_data: Response data to validate
            response_model: Expected response model type

        Returns:
            Validated response model instance

        Raises:
            ResponseValidationError: If validation fails
        """
        try:
            if issubclass(response_model, BaseResponse):
                # For BaseResponse types, validate the entire response
                return cast(T, response_model(**response_data))
            else:
                # For other models, expect data to be in the 'data' field
                if "data" not in response_data or not isinstance(
                    response_data["data"], list
                ):
                    raise ResponseValidationError(
                        "Invalid response format: missing or invalid 'data' field",
                        PydanticValidationError("Invalid response format", []),
                        None,
                    )
                if len(response_data["data"]) == 0:
                    # Return empty instance for empty data
                    return response_model()
                # Validate first item in data array
                return cast(T, response_model(**response_data["data"][0]))
        except PydanticValidationError as e:
            raise ResponseValidationError(
                f"Response validation failed: {str(e)}", e, None
            )

    @with_retry()
    def _request(
        self,
        method: str,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make HTTP request to API.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            response_model: Expected response model type
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response data as dict or validated model instance

        Raises:
            APIError: If request fails
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            ValidationError: If request validation fails
            NotFoundError: If resource is not found
            ServerError: If server returns 5xx error
            ResponseValidationError: If response validation fails
        """
        url = f"{self.config.api_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.config.timeout,
                **kwargs,
            )

            if response.ok:
                response_data = response.json()
                if response_model is not None:
                    return self._validate_response(response_data, response_model)
                return response_data

            self._handle_error_response(response)

        except (ConnectionError, Timeout):
            # Let the retry decorator handle these errors
            raise
        except SSLError as e:
            # Don't retry SSL errors
            raise APIError(
                "SSL verification failed", getattr(e, "response", None)
            ) from e
        except RequestException as e:
            # Don't retry other request exceptions
            raise APIError(str(e), getattr(e, "response", None)) from e

    def get(
        self, endpoint: str, response_model: Optional[Type[T]] = None, **kwargs: Any
    ) -> Any:
        """Make GET request to API endpoint."""
        return self._request("GET", endpoint, response_model, **kwargs)

    def post(
        self, endpoint: str, response_model: Optional[Type[T]] = None, **kwargs: Any
    ) -> Any:
        """Make POST request to API endpoint."""
        return self._request("POST", endpoint, response_model, **kwargs)

    def put(
        self, endpoint: str, response_model: Optional[Type[T]] = None, **kwargs: Any
    ) -> Any:
        """Make PUT request to API endpoint."""
        return self._request("PUT", endpoint, response_model, **kwargs)

    def delete(
        self, endpoint: str, response_model: Optional[Type[T]] = None, **kwargs: Any
    ) -> Any:
        """Make DELETE request to API endpoint."""
        return self._request("DELETE", endpoint, response_model, **kwargs)

    def close(self) -> None:
        """Close the API client session."""
        self.session.close()

    def __enter__(self) -> "BaseAPIClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit context manager."""
        self.close()
