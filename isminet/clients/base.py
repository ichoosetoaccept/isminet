"""Base API client implementation."""

import time
from typing import Any, Dict, List, Optional, Type, Union, TypeVar, ParamSpec
from urllib.parse import urljoin

from requests import Response, Session
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
        """Initialize a ResponseValidationError with an optional validation error."""
        super().__init__(message)
        self.validation_error = validation_error


class BaseAPIClient:
    """Base API client implementation."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize API client with configuration."""
        self.config = config
        self._session: Optional[Session] = None
        self._is_closed = False

    @property
    def session(self) -> Session:
        """Get or create session."""
        if self._is_closed:
            raise RuntimeError("Session is closed")
        if self._session is None:
            self._session = Session()
            self._session.verify = self.config.verify_ssl
            self._session.headers.update(self.config.get_headers())
        return self._session

    def close(self) -> None:
        """Close session."""
        if self._session is not None:
            self._session.close()
            self._session = None
        self._is_closed = True

    def __enter__(self) -> "BaseAPIClient":
        """Enter context manager."""
        self._is_closed = False
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        self.close()

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[Dict[str, Any], T, List[T]]:
        """Send GET request."""
        return self.request("GET", path, params=params, response_model=response_model)

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[Dict[str, Any], T, List[T]]:
        """Send POST request."""
        return self.request("POST", path, json=json, response_model=response_model)

    def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[Dict[str, Any], T, List[T]]:
        """Send PUT request."""
        return self.request("PUT", path, json=json, response_model=response_model)

    def delete(
        self,
        path: str,
        response_model: Optional[Type[T]] = None,
    ) -> Union[Dict[str, Any], T, List[T]]:
        """Send DELETE request."""
        return self.request("DELETE", path, response_model=response_model)

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[Dict[str, Any], T, List[T]]:
        """Send HTTP request."""
        if self._is_closed:
            raise RuntimeError("Session is closed")

        url = urljoin(self.config.api_url, path)
        retries = 3
        delay = 1.0

        while True:
            try:
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    timeout=self.config.timeout,
                )
                break
            except ConnectionError:
                if retries <= 0:
                    raise
                retries -= 1
                time.sleep(delay)
                delay *= 2

        if not response.ok:
            self._handle_error_response(response)

        data = response.json()

        if response_model is not None:
            try:
                if isinstance(data.get("data"), list):
                    return [response_model(**item) for item in data["data"]]
                return response_model(**data["data"])
            except ValidationError as e:
                raise ResponseValidationError("Response validation failed", e)

        return data

    def _handle_error_response(self, response: Response) -> None:
        """Handle error response."""
        error_msg = response.text
        try:
            error_data = response.json()
            if "meta" in error_data and "msg" in error_data["meta"]:
                error_msg = error_data["meta"]["msg"]
        except Exception:
            pass

        if response.status_code == 401:
            raise AuthenticationError(error_msg)
        elif response.status_code == 403:
            raise PermissionError(error_msg)
        elif response.status_code == 404:
            raise NotFoundError(error_msg)
        else:
            raise APIError(error_msg)
