"""Base API client implementation."""

import time
from typing import Any, Dict, Optional, Type, Union, Callable, TypeVar, ParamSpec
from urllib.parse import urljoin

from requests import Response, Session, Timeout
from requests.exceptions import ConnectionError
from pydantic import ValidationError

from ..config import APIConfig
from ..models.base import UnifiBaseModel

T = TypeVar("T", bound=UnifiBaseModel)
P = ParamSpec("P")
R = TypeVar("R")


class APIError(Exception):
    """Base class for API errors."""


class AuthenticationError(APIError):
    """Authentication error."""


class PermissionError(APIError):
    """Permission error."""


class NotFoundError(APIError):
    """Resource not found error."""


class ResponseValidationError(APIError):
    """Response validation error."""

    def __init__(
        self, message: str, validation_error: Optional[ValidationError] = None
    ) -> None:
        super().__init__(message)
        self.validation_error = validation_error


def with_retry(
    max_retries: int = 3, delay: float = 1.0
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to retry failed requests."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, Timeout) as e:
                    last_error = e
                    if attempt == max_retries - 1:
                        break
                    time.sleep(delay * (attempt + 1))

            if last_error:
                raise APIError(
                    f"Request failed after {max_retries} retries: {str(last_error)}"
                )
            return func(*args, **kwargs)  # Final attempt

        return wrapper

    return decorator


class BaseAPIClient:
    """Base API client for UniFi Network API."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize the API client."""
        self.config = config
        self.session = Session()
        self.session.verify = config.verify_ssl
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        if config.api_key:
            self.session.headers["Authorization"] = f"Bearer {config.api_key}"

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for an API endpoint."""
        scheme = "https" if self.config.verify_ssl else "http"
        port = f":{self.config.port}" if self.config.port else ""
        base_url = f"{scheme}://{self.config.host}{port}"
        return urljoin(base_url, endpoint.lstrip("/"))

    def _handle_error_response(self, response: Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
            error_message = error_data.get("message", "Unknown error")
            if "meta" in error_data and "msg" in error_data["meta"]:
                error_message = error_data["meta"]["msg"]
        except (ValueError, KeyError):
            error_message = response.text or "Unknown error"

        if response.status_code == 401:
            raise AuthenticationError("Authentication failed: " + error_message)
        elif response.status_code == 403:
            raise PermissionError("Permission error: " + error_message)
        elif response.status_code == 404:
            raise NotFoundError("Resource not found: " + error_message)
        else:
            raise APIError(f"HTTP {response.status_code}: {error_message}")

    @with_retry()
    def _request(
        self,
        method: str,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any]]:
        """Make an HTTP request to the UniFi Network API."""
        url = self._build_url(endpoint)
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.config.timeout,
                **kwargs,
            )
            if not response.ok:
                self._handle_error_response(response)

            data = response.json()
            if response_model:
                if "data" in data and isinstance(data["data"], list) and data["data"]:
                    # If data is a list and not empty, use first item
                    return response_model(**data["data"][0])
                elif "data" in data and not data["data"]:
                    # If data is empty list, return empty model
                    return response_model()
                else:
                    # Otherwise, try to parse entire response
                    return response_model(**data)
            return data
        except (ConnectionError, Timeout):
            raise
        except ValidationError as e:
            raise ResponseValidationError(
                f"Response validation failed: {str(e)}", e
            ) from e
        except (AuthenticationError, PermissionError, NotFoundError):
            raise
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}") from e

    def get(
        self,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any]]:
        """Make a GET request."""
        return self._request("GET", endpoint, response_model, **kwargs)

    def post(
        self,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any]]:
        """Make a POST request."""
        return self._request("POST", endpoint, response_model, **kwargs)

    def put(
        self,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any]]:
        """Make a PUT request."""
        return self._request("PUT", endpoint, response_model, **kwargs)

    def delete(
        self,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any]]:
        """Make a DELETE request."""
        return self._request("DELETE", endpoint, response_model, **kwargs)

    def close(self) -> None:
        """Close the session."""
        if self.session:
            self.session.close()

    def __enter__(self) -> "BaseAPIClient":
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Exit the context manager and close the session."""
        if self.session:
            self.session.close()
            self.session = None  # type: ignore
