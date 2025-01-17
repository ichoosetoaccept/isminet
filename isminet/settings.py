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
    unifi_timeout: int = Field(
        default=10,
        description="API request timeout in seconds",
        gt=0,
        le=300,  # Maximum 5 minutes timeout
    )
    unifi_site: str = Field(
        default="default",
        description="UniFi Network site name",
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",  # Only alphanumeric, underscore, and hyphen
    )
    unifi_api_version: APIVersion = Field(
        default=APIVersion.V1,
        description="UniFi Network API version",
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

    @field_validator("unifi_verify_ssl")
    @classmethod
    def validate_verify_ssl(cls, v: bool) -> bool:
        """Validate SSL verification setting."""
        if v and not settings.development_mode:
            pass
        return v

    @field_validator("unifi_timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout value."""
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        if v > 300:
            raise ValueError("Timeout cannot exceed 300 seconds (5 minutes)")
        if v > 60:
            pass
        return v

    @field_validator("unifi_site")
    @classmethod
    def validate_site(cls, v: str) -> str:
        """Validate site name."""
        if not v:
            raise ValueError("Site name cannot be empty")
        if not v.isascii():
            raise ValueError("Site name must contain only ASCII characters")
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Site name can only contain letters, numbers, hyphens, and underscores"
            )
        return v

    @field_validator("unifi_api_version")
    @classmethod
    def validate_api_version(cls, v: APIVersion) -> APIVersion:
        """Validate API version."""
        if v == APIVersion.V2 and settings.development_mode:
            pass
        return v

    def get_log_file_path(self) -> str:
        """Get the appropriate log file path based on mode."""
        self.LOG_DIR.mkdir(exist_ok=True)
        return str(self.LOG_DIR / ("dev.log" if self.development_mode else "prod.log"))


# Create a global settings instance
settings = Settings()


def warn_about_settings() -> None:
    """Add warning logs for certain settings combinations.

    This function should be called after logging is initialized.
    """
    # Import here to avoid circular imports
    from .logging import get_logger

    logger = get_logger(__name__)

    if settings.unifi_verify_ssl and not settings.development_mode:
        logger.warning(
            "SSL verification enabled in production mode",
            ssl_verification=settings.unifi_verify_ssl,
            dev_mode=settings.development_mode,
        )

    if settings.unifi_timeout > 60:
        logger.warning(
            "High timeout value configured",
            timeout=settings.unifi_timeout,
        )

    if settings.unifi_api_version == APIVersion.V2 and settings.development_mode:
        logger.warning(
            "Using V2 API in development mode",
            api_version=settings.unifi_api_version.value,
            dev_mode=settings.development_mode,
        )
