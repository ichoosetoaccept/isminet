"""Site models for the UniFi Network API."""

from pydantic import BaseModel, Field, ConfigDict


class Site(BaseModel):
    """UniFi Network site."""

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    name: str = Field(description="Site name")
    desc: str = Field(description="Site description")
    id: str = Field(alias="_id", description="Site identifier")
    device_count: int = Field(description="Number of devices in site", ge=0)
    anonymous_id: str | None = Field(None, description="Anonymous site identifier")
    external_id: str | None = Field(None, description="External site identifier")
    attr_no_delete: bool | None = Field(None, description="Whether site can be deleted")
    attr_hidden_id: str | None = Field(None, description="Hidden site identifier")
    role: str | None = Field(None, description="User role in site")
    role_hotspot: bool | None = Field(None, description="Whether site is a hotspot")
