"""Configuration management for the isminet package."""

from enum import Enum
from typing import Any, Optional
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
    host: str = Field(description="UniFi Network controller hostname/IP")

    # Optional settings with defaults
    port: Optional[int] = Field(
        default=None, description="UniFi Network controller port"
    )
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
        """Validate host is not empty."""
        if not v:
            raise ValueError("Host cannot be empty")
        return v

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is not empty."""
        if not v:
            raise ValueError("API key cannot be empty")
        return v

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: Optional[int]) -> Optional[int]:
        """Validate port is in valid range."""
        if v is not None and (v < 1 or v > 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

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
        return cls(**kwargs)
