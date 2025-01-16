"""Base models for the UniFi Network API."""

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class UnifiBaseModel(BaseModel):
    """Base model with common configuration for all UniFi models."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
        strict=True,
    )


class Meta(UnifiBaseModel):
    """Response metadata from the UniFi API."""

    rc: str = Field(description="Response code, 'ok' indicates success")


class BaseResponse(UnifiBaseModel, Generic[T]):
    """Base response model for UniFi API endpoints."""

    meta: Meta
    data: List[T]
