"""Base models for the UniFi Network API."""

from typing import Generic, TypeVar, List, Optional
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


class StatisticsMixin(UnifiBaseModel):
    """Common statistics fields for UniFi models."""

    tx_bytes: Optional[int] = Field(None, description="Total bytes transmitted", ge=0)
    rx_bytes: Optional[int] = Field(None, description="Total bytes received", ge=0)
    tx_packets: Optional[int] = Field(
        None, description="Total packets transmitted", ge=0
    )
    rx_packets: Optional[int] = Field(None, description="Total packets received", ge=0)
    bytes_r: Optional[float] = Field(None, description="Current bytes rate", ge=0)
    tx_bytes_r: Optional[float] = Field(
        None, description="Current transmit bytes rate", ge=0
    )
    rx_bytes_r: Optional[float] = Field(
        None, description="Current receive bytes rate", ge=0
    )
    satisfaction: Optional[int] = Field(
        None, description="Satisfaction score (0-100)", ge=0, le=100
    )


class DeviceBaseMixin(UnifiBaseModel):
    """Common device fields for UniFi models."""

    mac: str = Field(description="MAC address")
    ip: Optional[str] = Field(None, description="IP address")
    uptime: Optional[int] = Field(None, description="Device uptime in seconds", ge=0)
    last_seen: Optional[int] = Field(None, description="Last seen timestamp")
    site_id: Optional[str] = Field(None, description="Site identifier")
    name: Optional[str] = Field(None, description="Device name")


class NetworkMixin(UnifiBaseModel):
    """Common network-related fields."""

    network_name: Optional[str] = Field(None, description="Network name")
    network_id: Optional[str] = Field(None, description="Network identifier")
    netmask: Optional[str] = Field(None, description="Network mask")
    is_guest: Optional[bool] = Field(None, description="Whether network is for guests")
    vlan: Optional[int] = Field(None, description="VLAN ID", ge=0, le=4095)


class SystemStatsMixin(UnifiBaseModel):
    """Common system statistics fields."""

    cpu_usage: Optional[float] = Field(
        None, description="CPU usage percentage", ge=0, le=100
    )
    mem_usage: Optional[float] = Field(
        None, description="Memory usage percentage", ge=0, le=100
    )
    temperature: Optional[float] = Field(None, description="Temperature")
    loadavg_1: Optional[float] = Field(None, description="1-minute load average", ge=0)
    loadavg_5: Optional[float] = Field(None, description="5-minute load average", ge=0)
    loadavg_15: Optional[float] = Field(
        None, description="15-minute load average", ge=0
    )
