"""Base models for the UniFi Network API."""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field, ConfigDict, ValidationInfo, field_validator

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


class WifiMixin(UnifiBaseModel):
    """Common WiFi-related fields."""

    channel: Optional[int] = Field(None, description="WiFi channel")
    tx_rate: Optional[int] = Field(None, description="Transmit rate in Kbps", ge=0)
    rx_rate: Optional[int] = Field(None, description="Receive rate in Kbps", ge=0)
    tx_power: Optional[int] = Field(None, description="Transmit power")
    tx_retries: Optional[int] = Field(
        None, description="Number of transmit retries", ge=0
    )
    channel_width: Optional[int] = Field(None, description="Channel width in MHz")
    radio_name: Optional[str] = Field(None, description="Radio name")
    authorized: Optional[bool] = Field(None, description="Whether client is authorized")
    qos_policy_applied: Optional[bool] = Field(
        None, description="Whether QoS policy is applied"
    )


class TimestampMixin(UnifiBaseModel):
    """Common timestamp-related fields."""

    first_seen: Optional[int] = Field(None, description="First seen timestamp")
    last_seen: Optional[int] = Field(None, description="Last seen timestamp")
    disconnect_timestamp: Optional[int] = Field(
        None, description="Last disconnect timestamp"
    )
    assoc_time: Optional[int] = Field(None, description="Association time")
    latest_assoc_time: Optional[int] = Field(
        None, description="Latest association time"
    )

    @field_validator("first_seen")
    @classmethod
    def validate_first_seen(
        cls, v: Optional[int], info: ValidationInfo
    ) -> Optional[int]:
        """Validate first_seen is before last_seen."""
        if (
            v is not None
            and "last_seen" in info.data
            and info.data["last_seen"] is not None
        ):
            if v > info.data["last_seen"]:
                raise ValueError("first_seen must be before last_seen")
        return v

    @field_validator("last_seen")
    @classmethod
    def validate_last_seen(
        cls, v: Optional[int], info: ValidationInfo
    ) -> Optional[int]:
        """Validate last_seen is after first_seen."""
        if (
            v is not None
            and "first_seen" in info.data
            and info.data["first_seen"] is not None
        ):
            if v < info.data["first_seen"]:
                raise ValueError("last_seen must be after first_seen")
        return v

    @field_validator("latest_assoc_time")
    @classmethod
    def validate_latest_assoc_time(
        cls, v: Optional[int], info: ValidationInfo
    ) -> Optional[int]:
        """Validate latest_assoc_time is after assoc_time."""
        if (
            v is not None
            and "assoc_time" in info.data
            and info.data["assoc_time"] is not None
        ):
            if v < info.data["assoc_time"]:
                raise ValueError("latest_assoc_time must be after assoc_time")
        return v
