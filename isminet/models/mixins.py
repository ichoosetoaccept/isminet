"""Mixins for UniFi Network models."""

from typing import Optional, List
from pydantic import Field, field_validator

from .base import UnifiBaseModel
from .validators import (
    VERSION_PATTERN,
    validate_ip,
    validate_mac,
    validate_mac_list,
)


class ValidationMixin:
    """Mixin class for common validation methods."""

    @field_validator("mac")
    @classmethod
    def validate_mac(cls, v: str) -> str:
        """Validate MAC address."""
        try:
            validate_mac(v)
            return v
        except ValueError:
            raise ValueError("Invalid MAC address format")

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IPv4 address."""
        try:
            validate_ip(v)
            return v
        except ValueError:
            raise ValueError("Invalid IPv4 address")

    @field_validator("netmask")
    @classmethod
    def validate_netmask(cls, v: str) -> str:
        """Validate network mask."""
        try:
            validate_ip(v)
            return v
        except ValueError:
            raise ValueError("Invalid network mask")

    @field_validator("mac_list")
    @classmethod
    def validate_mac_list(cls, v: List[str]) -> List[str]:
        """Validate list of MAC addresses."""
        try:
            validate_mac_list(v)
            return v
        except ValueError:
            raise ValueError("Invalid MAC address list")

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version string."""
        if not VERSION_PATTERN.match(v):
            raise ValueError("Version must be in format x.y.z")
        return v


class StatisticsMixin(UnifiBaseModel):
    """Mixin for network statistics."""

    tx_bytes: Optional[int] = Field(None, ge=0, description="Total transmitted bytes")
    rx_bytes: Optional[int] = Field(None, ge=0, description="Total received bytes")
    tx_packets: Optional[int] = Field(
        None, ge=0, description="Total transmitted packets"
    )
    rx_packets: Optional[int] = Field(None, ge=0, description="Total received packets")
    bytes_r: Optional[float] = Field(None, ge=0, description="Bytes per second")
    tx_bytes_r: Optional[float] = Field(
        None, ge=0, description="Transmitted bytes per second"
    )
    rx_bytes_r: Optional[float] = Field(
        None, ge=0, description="Received bytes per second"
    )
    satisfaction: Optional[int] = Field(
        None, ge=0, le=100, description="Satisfaction percentage"
    )


class NetworkMixin(UnifiBaseModel):
    """Mixin for network fields."""

    network_name: Optional[str] = Field(None, min_length=1, description="Network name")
    network_id: Optional[str] = Field(None, min_length=1, description="Network ID")
    netmask: Optional[str] = Field(None, description="Network mask")
    is_guest: Optional[bool] = Field(None, description="Guest network flag")
    vlan: Optional[int] = Field(None, ge=1, le=4095, description="VLAN ID")


class SystemStatsMixin(UnifiBaseModel):
    """Mixin for system statistics."""

    cpu_usage: Optional[float] = Field(
        None, ge=0, le=100, description="CPU usage percentage"
    )
    mem_usage: Optional[float] = Field(
        None, ge=0, le=100, description="Memory usage percentage"
    )
    temperature: Optional[float] = Field(None, ge=0, description="System temperature")
    loadavg_1: Optional[float] = Field(None, ge=0, description="1 minute load average")
    loadavg_5: Optional[float] = Field(None, ge=0, description="5 minute load average")
    loadavg_15: Optional[float] = Field(
        None, ge=0, description="15 minute load average"
    )


class WifiMixin(UnifiBaseModel):
    """Mixin for WiFi fields."""

    channel: Optional[int] = Field(None, ge=1, description="WiFi channel")
    tx_rate: Optional[int] = Field(None, ge=0, description="Transmit rate")
    rx_rate: Optional[int] = Field(None, ge=0, description="Receive rate")
    tx_power: Optional[int] = Field(None, ge=0, description="Transmit power")
    tx_retries: Optional[int] = Field(None, ge=0, description="Transmit retries")
    channel_width: Optional[int] = Field(None, description="Channel width")
    radio_name: Optional[str] = Field(None, min_length=1, description="Radio name")
    authorized: Optional[bool] = Field(None, description="Authorization status")
    qos_policy_applied: Optional[bool] = Field(None, description="QoS policy status")

    @field_validator("channel_width")
    @classmethod
    def validate_channel_width(cls, v: Optional[int]) -> Optional[int]:
        """Validate channel width."""
        if v is not None:
            valid_widths = {20, 40, 80, 160, 320}
            if v not in valid_widths:
                raise ValueError("Invalid channel width")
        return v
