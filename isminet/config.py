"""Configuration management for the isminet package."""

from typing import Any
from urllib.parse import urljoin

from .settings import settings


class APIConfig:
    """UniFi Network API configuration.

    This class is now a wrapper around the central settings,
    maintaining compatibility with existing code while using
    the centralized configuration.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize API configuration from settings or kwargs."""
        # Allow overriding settings with kwargs
        self.api_key = kwargs.get("api_key", settings.unifi_api_key)
        self.host = kwargs.get("host", settings.unifi_host)
        self.port = kwargs.get("port", settings.unifi_port)
        self.verify_ssl = kwargs.get("verify_ssl", settings.unifi_verify_ssl)
        self.timeout = kwargs.get("timeout", settings.unifi_timeout)
        self.site = kwargs.get("site", settings.unifi_site)
        self.api_version = kwargs.get("api_version", settings.unifi_api_version)

        # Validate required fields
        if not self.api_key:
            raise ValueError("API key cannot be empty")
        if not self.host:
            raise ValueError("Host cannot be empty")
        if self.port is not None:
            if not isinstance(self.port, int):
                raise ValueError("Port must be an integer")
            if self.port < 1 or self.port > 65535:
                raise ValueError("Port must be between 1 and 65535")

    @property
    def base_url(self) -> str:
        """Get base URL for API requests."""
        scheme = "https" if self.verify_ssl else "http"
        if self.port:
            return f"{scheme}://{self.host}:{self.port}"
        return f"{scheme}://{self.host}"

    @property
    def api_url(self) -> str:
        """Get API URL for requests."""
        return urljoin(self.base_url, self.api_version.path)

    def get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    @classmethod
    def from_env(cls, **kwargs: Any) -> "APIConfig":
        """Create config from environment variables."""
        from .logging import get_logger

        logger = get_logger(__name__)
        config = cls(**kwargs)
        logger.info(
            "config_loaded",
            host=config.host,
            port=config.port,
            verify_ssl=config.verify_ssl,
            site=config.site,
            api_version=config.api_version,
        )
        return config
