"""Central configuration management for isminet."""

from enum import Enum
from pathlib import Path
from typing import Literal, Optional

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


class Settings(BaseSettings):
    """Central configuration for isminet.

    This class loads all configuration from environment variables and .env file.
    Environment variables take precedence over .env file values.
    """

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    LOG_DIR: Path = PROJECT_ROOT / "logs"

    # UniFi Network API Configuration
    unifi_api_key: str = Field(description="UniFi Network API key")
    unifi_host: str = Field(description="UniFi Network controller hostname/IP")
    unifi_port: Optional[int] = Field(
        default=None,
        description="UniFi Network controller port",
    )
    unifi_verify_ssl: bool = Field(
        default=False, description="Whether to verify SSL certificates"
    )
    unifi_timeout: int = Field(default=10, description="API request timeout in seconds")
    unifi_site: str = Field(default="default", description="UniFi Network site name")
    unifi_api_version: APIVersion = Field(
        default=APIVersion.V1, description="UniFi Network API version"
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level", alias="isminet_log_level"
    )
    development_mode: bool = Field(
        default=False,
        description="Whether to run in development mode",
        alias="isminet_dev_mode",
    )
    log_to_file: bool = Field(
        default=True, description="Whether to log to file", alias="isminet_log_to_file"
    )

    # Test Configuration
    test_api_key: str = Field(
        default="test_key", description="Default API key for tests"
    )
    test_host: str = Field(default="test.host", description="Default host for tests")
    test_port: int = Field(
        default=8443,
        description="Default port for tests",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown environment variables
    )

    @field_validator("unifi_host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host is not empty."""
        if not v:
            raise ValueError("Host cannot be empty")
        return v

    @field_validator("unifi_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is not empty."""
        if not v:
            raise ValueError("API key cannot be empty")
        return v

    @field_validator("unifi_port", "test_port")
    @classmethod
    def validate_port(cls, v: Optional[int]) -> Optional[int]:
        """Validate port is in valid range."""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError("Port must be an integer")
            if v < 1 or v > 65535:
                raise ValueError("Port must be between 1 and 65535")
        return v

    def get_log_file_path(self) -> str:
        """Get the appropriate log file path based on mode."""
        self.LOG_DIR.mkdir(exist_ok=True)
        return str(self.LOG_DIR / ("dev.log" if self.development_mode else "prod.log"))


# Create a global settings instance
settings = Settings()
