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
        """
        Initialize a ResponseValidationError with an optional validation error.

        Parameters:
            message (str): A descriptive error message explaining the validation failure.
            validation_error (Optional[ValidationError], optional): The specific Pydantic validation error details. Defaults to None.
        """
        super().__init__(message)
        self.validation_error = validation_error


def with_retry(
    max_retries: int = 3, delay: float = 1.0
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to retry failed requests with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts. Defaults to 3.
        delay: Base delay between retry attempts in seconds. Defaults to 1.0.

    Returns:
        A decorator that wraps the original function with retry logic.

    Notes:
        Uses exponential backoff strategy to reduce load during outages.
        Delay increases exponentially with each retry attempt.
    """

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
                    # Use exponential backoff: delay * 2^attempt
                    time.sleep(delay * (2**attempt))

            if last_error:
                raise APIError(
                    f"Request failed after {max_retries} retries: {str(last_error)}"
                )

            # This case should never happen in practice since we only reach here after a failed attempt
            # But we need it for type safety
            return func(*args, **kwargs)

        return wrapper

    return decorator


class BaseAPIClient:
    """Base API client for UniFi Network API."""

    def __init__(self, config: APIConfig) -> None:
        """
        Initialize a new API client with the provided configuration.

        Parameters:
            config (APIConfig): Configuration object containing client settings such as SSL verification, API key, and other connection parameters.

        Attributes:
            config (APIConfig): Stored configuration for the API client.
            session (Session): Requests session with configured headers and SSL verification.

        Side Effects:
            - Creates a new requests Session
            - Sets SSL certificate verification based on configuration
            - Updates session headers with JSON content type and optional API key authorization
        """
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
        """
        Construct the full URL for an API endpoint using the client's configuration.

        Parameters:
            endpoint (str): The API endpoint path to be appended to the base URL.

        Returns:
            str: A complete URL combining the base URL scheme, host, port, and specified endpoint.

        Notes:
            - Uses HTTPS if SSL verification is enabled, otherwise defaults to HTTP
            - Automatically handles port configuration if specified
            - Removes leading slash from endpoint to prevent double-slashing
            - Utilizes urljoin to safely combine base URL and endpoint
        """
        scheme = "https" if self.config.verify_ssl else "http"
        port = f":{self.config.port}" if self.config.port else ""
        base_url = f"{scheme}://{self.config.host}{port}"
        return urljoin(base_url, endpoint.lstrip("/"))

    def _handle_error_response(self, response: Response) -> None:
        """
        Handle error responses from the API by parsing the response and raising appropriate exceptions.

        This method attempts to extract an error message from the API response JSON. If JSON parsing fails,
        it falls back to the response text. Based on the HTTP status code, it raises specific exceptions.

        Args:
            response: The HTTP response object containing error details

        Raises:
            AuthenticationError: If authentication fails (401)
            PermissionError: If permission is denied (403)
            NotFoundError: If resource is not found (404)
            APIError: For any other HTTP error status codes
        """
        try:
            error_data = response.json()
            error_message = error_data.get("message", "Unknown error")
            if "meta" in error_data and "msg" in error_data["meta"]:
                error_message = error_data["meta"]["msg"]
        except (ValueError, KeyError):
            error_message = response.text or "Unknown error"

        error_mapping = {
            401: AuthenticationError,
            403: PermissionError,
            404: NotFoundError,
        }

        exception_class = error_mapping.get(response.status_code, APIError)
        raise exception_class(f"HTTP {response.status_code}: {error_message}")

    @with_retry()
    def _request(
        self,
        method: str,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any]]:
        """
        Make an HTTP request to the UniFi Network API with optional response model validation.

        This method handles making HTTP requests to the specified endpoint, processing the response,
        and optionally validating the response against a Pydantic model.

        Parameters:
            method (str): The HTTP method to use (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            endpoint (str): The API endpoint to request.
            response_model (Optional[Type[T]], optional): A Pydantic model to validate and parse the response.
                Defaults to None.
            **kwargs: Additional arguments to pass to the request method.

        Returns:
            Union[T, Dict[str, Any]]: Either a validated Pydantic model instance or the raw response dictionary.

        Raises:
            ConnectionError: If there's a network connection issue.
            Timeout: If the request times out.
            ResponseValidationError: If the response fails Pydantic model validation.
            AuthenticationError: If authentication fails.
            PermissionError: If the request is not authorized.
            NotFoundError: If the requested resource is not found.
            APIError: For any other unexpected errors during the request.

        Notes:
            - Handles different response structures, including list and empty data scenarios.
            - Automatically builds the full URL using the _build_url method.
            - Uses the client's configured session and timeout settings.
        """
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
                if "data" in data:
                    data_content = data["data"]
                    if isinstance(data_content, list):
                        return (
                            response_model(**data_content[0])
                            if data_content
                            else response_model()
                        )
                    elif isinstance(data_content, dict):
                        return response_model(**data_content)
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
        """
        Make a GET request to the specified API endpoint.

        Parameters:
            endpoint (str): The API endpoint path to request.
            response_model (Optional[Type[T]], optional): A Pydantic model to validate and deserialize the response. Defaults to None.
            **kwargs (Any): Additional arguments to pass to the underlying request method.

        Returns:
            Union[T, Dict[str, Any]]: Either a validated response object of the specified model or a dictionary of the raw response data.

        Raises:
            AuthenticationError: If authentication fails.
            PermissionError: If the request is not authorized.
            NotFoundError: If the requested resource is not found.
            ResponseValidationError: If the response cannot be validated against the specified model.
            APIError: For other API-related errors.
        """
        return self._request("GET", endpoint, response_model, **kwargs)

    def post(
        self,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any]]:
        """
        Make a POST request to the specified API endpoint.

        Parameters:
            endpoint (str): The API endpoint path to send the POST request to.
            response_model (Optional[Type[T]], optional): A Pydantic model to validate and deserialize the response. Defaults to None.
            **kwargs (Any): Additional arguments to be passed to the underlying request method, such as data, headers, or query parameters.

        Returns:
            Union[T, Dict[str, Any]]: Either a deserialized response object using the provided Pydantic model or a dictionary of the raw response data.

        Raises:
            AuthenticationError: If authentication fails (HTTP 401).
            PermissionError: If the request is forbidden (HTTP 403).
            NotFoundError: If the requested resource is not found (HTTP 404).
            ResponseValidationError: If the response cannot be validated against the specified model.
            APIError: For other API-related errors or connection issues.
        """
        return self._request("POST", endpoint, response_model, **kwargs)

    def put(
        self,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any]]:
        """
        Make a PUT request to the specified API endpoint.

        Parameters:
            endpoint (str): The API endpoint path to send the PUT request to.
            response_model (Optional[Type[T]], optional): A Pydantic model to validate and deserialize the response. Defaults to None.
            **kwargs (Any): Additional arguments to be passed to the underlying request method.

        Returns:
            Union[T, Dict[str, Any]]: Either a deserialized response object using the provided response model or a dictionary of the raw response data.

        Raises:
            APIError: If the request fails due to connection issues, authentication problems, or other API-related errors.
            ResponseValidationError: If the response cannot be validated against the specified response model.
        """
        return self._request("PUT", endpoint, response_model, **kwargs)

    def delete(
        self,
        endpoint: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any]]:
        """
        Delete a resource via the API.

        Parameters:
            endpoint (str): The API endpoint path to delete the resource from.
            response_model (Optional[Type[T]], optional): Pydantic model to validate and parse the response. Defaults to None.
            **kwargs (Any): Additional arguments to pass to the underlying request method.

        Returns:
            Union[T, Dict[str, Any]]: Either a validated response object of type T or a dictionary of response data.

        Raises:
            APIError: If the request fails due to connection, authentication, or server issues.
            ResponseValidationError: If the response cannot be validated against the specified model.
        """
        return self._request("DELETE", endpoint, response_model, **kwargs)

    def close(self) -> None:
        """
        Close the active HTTP session.

        This method ensures that the underlying HTTP session is properly closed, releasing any network resources and connections associated with the session. If no session is currently open, the method does nothing.

        Raises:
            None
        """
        if self.session:
            self.session.close()

    def __enter__(self) -> "BaseAPIClient":
        """
        Enters the context manager for the BaseAPIClient, enabling use with the `with` statement.

        Returns:
            BaseAPIClient: The current instance of the API client, allowing method chaining and context management.

        Example:
            with BaseAPIClient(config) as client:
                response = client.get('/endpoint')
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """
        Exit the context manager and close the underlying HTTP session.

        This method is called when exiting a context managed by the BaseAPIClient, ensuring proper cleanup of resources.

        Parameters:
            exc_type (Optional[Type[BaseException]]): The type of exception that caused the context to be exited, if any.
            exc_val (Optional[BaseException]): The exception instance that caused the context to be exited, if any.
            exc_tb (Optional[Any]): A traceback object for the exception, if any.

        Notes:
            - Closes the active session if one exists
            - Creates a new closed session to maintain type safety
            - Part of the context manager protocol (__enter__/__exit__)
        """
        if self.session:
            self.session.close()
            self.session = Session()  # Create a new closed session instead of None
