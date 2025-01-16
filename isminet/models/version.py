"""Version models for the UniFi Network API."""

from typing import Optional
from pydantic import Field, field_validator

from .base import UnifiBaseModel
from .validators import validate_version, version_field, site_id_field


class VersionInfo(UnifiBaseModel):
    """UniFi Network controller version information."""

    version: str = Field(description="Controller version")  # Required field
    build: Optional[str] = Field(None, description="Build number")
    site_id: str = site_id_field
    update_available: Optional[bool] = Field(
        None, description="Whether update is available"
    )
    update_downloaded: Optional[bool] = Field(
        None, description="Whether update is downloaded"
    )
    update_version: Optional[str] = version_field
    update_notes: Optional[str] = Field(None, description="Update release notes")
    internal_version: Optional[str] = Field(None, description="Internal version number")
    hardware_version: Optional[str] = Field(None, description="Hardware version")
    api_version: Optional[str] = Field(None, description="API version")
    api_version_min: Optional[str] = Field(
        None, description="Minimum supported API version"
    )
    api_version_max: Optional[str] = Field(
        None, description="Maximum supported API version"
    )

    _validate_version = field_validator("version", "update_version")(validate_version)
