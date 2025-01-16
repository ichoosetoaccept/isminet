"""Configuration management for the isminet package."""

from enum import Enum
from typing import Any
from urllib.parse import urljoin

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIVersion(str, Enum):
    """UniFi Network API versions."""

    V1 = "v1"
    V2 = "v2"

    @property
    def path(self) -> str:
        """Get API path for version."""
        return "/proxy/network/api"


class APIConfig(BaseSettings):
    """UniFi Network API configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="UNIFI_",
        case_sensitive=False,
    )

    # Required settings
    api_key: str = Field(description="UniFi Network API key")

    # Optional settings with defaults
    host: str = Field(
        default="192.168.1.1", description="UniFi Network controller hostname/IP"
    )
    port: int = Field(default=443, description="UniFi Network controller port")
    verify_ssl: bool = Field(
        default=False, description="Whether to verify SSL certificates"
    )
    timeout: int = Field(default=10, description="API request timeout in seconds")
    site: str = Field(default="default", description="UniFi Network site name")
    api_version: APIVersion = Field(
        default=APIVersion.V1, description="UniFi Network API version"
    )

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host value."""
        if not v:
            raise ValueError("Host cannot be empty")
        if "://" in v:
            raise ValueError("Host should not include protocol")
        return v.strip()

    @property
    def base_url(self) -> str:
        """Get base URL for API requests."""
        return f"https://{self.host}:{self.port}"

    @property
    def api_url(self) -> str:
        """Get complete API URL."""
        return urljoin(self.base_url, self.api_version.path)

    def get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key,
        }

    @classmethod
    def from_env(cls, **kwargs: Any) -> "APIConfig":
        """Create configuration from environment variables.

        Args:
            **kwargs: Override any settings from environment

        Returns:
            APIConfig instance
        """
        return cls(**kwargs)
