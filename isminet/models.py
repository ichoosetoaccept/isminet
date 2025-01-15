from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class Meta(BaseModel):
    """Response metadata from the UniFi API."""

    rc: str = Field(description="Response code, 'ok' indicates success")


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for UniFi API endpoints."""

    meta: Meta
    data: List[T]


class Site(BaseModel):
    """
    UniFi Network site information.

    This model represents a UniFi Network site, which is a logical grouping of devices
    and configurations in the UniFi Network system.
    """

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1, strict=True)

    name: str = Field(description="Name of the site")
    desc: str = Field(description="Description of the site")
    id: str = Field(alias="_id", description="Unique identifier for the site")
    device_count: int = Field(description="Number of devices in the site")
    anonymous_id: Optional[str] = Field(
        None, description="Anonymous identifier for the site"
    )
    external_id: Optional[str] = Field(
        None, description="External identifier for the site"
    )
    attr_no_delete: Optional[bool] = Field(
        None, description="Whether the site can be deleted"
    )
    attr_hidden_id: Optional[str] = Field(
        None, description="Hidden identifier for the site"
    )
    role: Optional[str] = Field(None, description="User's role in the site")
    role_hotspot: Optional[bool] = Field(
        None, description="Whether the site has hotspot role enabled"
    )
