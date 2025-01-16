"""Device component models for UniFi Network devices."""

from typing import Optional, List
from pydantic import Field, field_validator

from .base import UnifiBaseModel, ValidationMixin
from .validators import validate_ip
from .enums import LedOverride


class DeviceNetwork(ValidationMixin, UnifiBaseModel):
    """Network configuration for UniFi devices."""

    inform_url: Optional[str] = Field(None, description="Inform URL")
    inform_ip: Optional[str] = Field(None, description="Inform IP address")
    config_network: Optional[dict] = Field(None, description="Network configuration")
    ethernet_table: Optional[List[dict]] = Field(None, description="Ethernet table")
    uplink: Optional[dict] = Field(None, description="Uplink information")
    uplink_table: Optional[List[dict]] = Field(None, description="Uplink table")

    _validate_ip = field_validator("inform_ip")(validate_ip)

    @field_validator("inform_url")
    @classmethod
    def validate_inform_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate inform URL format."""
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("Inform URL must start with http:// or https://")
        return v


class DeviceWireless(ValidationMixin, UnifiBaseModel):
    """Wireless configuration for UniFi devices."""

    radio_table: Optional[List[dict]] = Field(None, description="Radio table")
    vap_table: Optional[List[dict]] = Field(None, description="VAP table")
    num_sta: Optional[int] = Field(
        None, description="Number of connected clients", ge=0
    )
    user_num_sta: Optional[int] = Field(
        None, description="Number of user clients", ge=0
    )
    guest_num_sta: Optional[int] = Field(
        None, description="Number of guest clients", ge=0
    )


class DeviceSecurity(ValidationMixin, UnifiBaseModel):
    """Security configuration for UniFi devices."""

    x_ssh_hostkey: Optional[str] = Field(None, description="SSH host key")
    x_fingerprint: Optional[str] = Field(None, description="Device fingerprint")
    x_has_ssh_hostkey: Optional[bool] = Field(
        None, description="Whether device has SSH host key"
    )
    x_aes_gcm: Optional[bool] = Field(None, description="Whether AES-GCM is supported")
    x_inform_authkey: Optional[str] = Field(
        None, description="Inform authentication key"
    )
    guest_token: Optional[str] = Field(None, description="Guest authentication token")


class DeviceSystem(ValidationMixin, UnifiBaseModel):
    """System information for UniFi devices."""

    system_stats: Optional[dict] = Field(None, description="System statistics")
    state: Optional[int] = Field(None, description="Device state")
    state_code: Optional[int] = Field(None, description="Device state code")
    hw_caps: Optional[int] = Field(None, description="Hardware capabilities")
    unsupported: Optional[bool] = Field(
        None, description="Whether device is unsupported"
    )
    unsupported_reason: Optional[int] = Field(
        None, description="Reason for being unsupported"
    )
    upgradable: Optional[bool] = Field(None, description="Whether device is upgradable")
    discovered_via: Optional[str] = Field(None, description="How device was discovered")
    led_override: Optional[LedOverride] = Field(
        None, description="LED override setting"
    )
    adopted: Optional[bool] = Field(None, description="Whether device is adopted")
