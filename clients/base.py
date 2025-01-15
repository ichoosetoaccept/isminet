"""Base API client implementation."""

import logging
from typing import Any, TypeVar
from functools import wraps

import requests
from requests.exceptions import RequestException

from ..config import APIConfig
from ..models import BaseResponse  # We'll create this later

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for response models
T = TypeVar("T", bound=BaseResponse)


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
                except RequestException as e:
                    last_error = e
                    if attempt == max_retries:
                        break
                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(
                        "Request failed (attempt %d/%d). Retrying in %.1f seconds...",
                        attempt + 1, max_retries, delay
                    )
                    import time
                    time.sleep(delay)
            raise last_error
        return wrapper
    return decorator


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, response: requests.Response | None = None):
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code if response else None


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

    @with_retry()
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to API.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response data as dict

        Raises:
            APIError: If request fails
        """
        url = f"{self.config.api_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.config.timeout,
                **kwargs,
            )

            response.raise_for_status()
            return response.json()

        except RequestException as e:
            message = f"API request failed: {str(e)}"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    if "meta" in error_data and "msg" in error_data["meta"]:
                        message = error_data["meta"]["msg"]
                except ValueError:
                    pass
            raise APIError(message, getattr(e, "response", None)) from e

    def get(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make GET request to API endpoint."""
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make POST request to API endpoint."""
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make PUT request to API endpoint."""
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make DELETE request to API endpoint."""
        return self._request("DELETE", endpoint, **kwargs)

    def close(self) -> None:
        """Close the API client session."""
        self.session.close()

    def __enter__(self) -> "BaseAPIClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit context manager."""
        self.close()
