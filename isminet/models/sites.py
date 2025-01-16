"""Site models for the UniFi Network API."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Site(BaseModel):
    """Model for UniFi Network site."""

    id: str = Field(min_length=1, alias="_id")
    name: str = Field(min_length=1)
    desc: Optional[str] = None
    device_count: int = Field(ge=0)
    anonymous_id: Optional[str] = None
    external_id: Optional[str] = None
    attr_no_delete: Optional[bool] = None
    attr_hidden_id: Optional[str] = None
    role: Optional[str] = None
    role_hotspot: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate site name."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v
