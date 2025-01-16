"""Base models for the UniFi Network API."""

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, ConfigDict


class Meta(BaseModel):
    """Response metadata from the UniFi API."""

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1, strict=True)

    rc: str = Field(description="Response code, 'ok' indicates success")


T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for UniFi API endpoints."""

    meta: Meta
    data: List[T]
