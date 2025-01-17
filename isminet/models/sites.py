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
        """
        Validate the site name by ensuring it is not an empty string.

        Parameters:
            cls (type): The class calling the validator method
            v (str): The site name to validate

        Returns:
            str: The validated site name

        Raises:
            ValueError: If the site name is empty or contains only whitespace characters

        Example:
            # Valid usage
            site_name = "My Network Site"
            validated_name = Site.validate_name(Site, site_name)  # Returns "My Network Site"

            # Invalid usage
            site_name = "   "
            Site.validate_name(Site, site_name)  # Raises ValueError
        """
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v
