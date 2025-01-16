"""Site models for the UniFi Network API."""

from typing import Optional
from pydantic import Field

from .base import UnifiBaseModel


class Site(UnifiBaseModel):
    """UniFi Network site."""

    name: str = Field(description="Site name")
    desc: str = Field(description="Site description")
    id: str = Field(alias="_id", description="Site identifier")
    device_count: int = Field(description="Number of devices in site", ge=0)
    anonymous_id: Optional[str] = Field(None, description="Anonymous site identifier")
    external_id: Optional[str] = Field(None, description="External site identifier")
    attr_no_delete: Optional[bool] = Field(
        None, description="Whether site can be deleted"
    )
    attr_hidden_id: Optional[str] = Field(None, description="Hidden site identifier")
    role: Optional[str] = Field(None, description="User role in site")
    role_hotspot: Optional[bool] = Field(None, description="Whether site is a hotspot")
