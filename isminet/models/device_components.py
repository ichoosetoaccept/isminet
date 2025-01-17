"""Device component models for UniFi Network devices."""

from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator

from .base import UnifiBaseModel, ValidationMixin
from .validators import validate_ip
from .enums import LedOverride
from ..logging import get_logger

logger = get_logger(__name__)


class DeviceNetwork(ValidationMixin, UnifiBaseModel):
    """Network configuration for UniFi devices."""

    inform_url: Optional[str] = Field(None, description="Inform URL")
    inform_ip: Optional[str] = Field(None, description="Inform IP address")
    config_network: Optional[Dict[str, Any]] = Field(
        None, description="Network configuration"
    )
    ethernet_table: Optional[List[Dict[str, Any]]] = Field(
        None, description="Ethernet table"
    )
    uplink: Optional[Dict[str, Any]] = Field(None, description="Uplink information")
    uplink_table: Optional[List[Dict[str, Any]]] = Field(
        None, description="Uplink table"
    )

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

    radio_table: Optional[List[Dict[str, Any]]] = Field(None, description="Radio table")
    vap_table: Optional[List[Dict[str, Any]]] = Field(None, description="VAP table")
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


class DeviceSystem(UnifiBaseModel):
    """Model representing the system component of a UniFi Network device."""

    system_stats: Optional[Dict[str, Any]] = Field(
        None, description="System statistics"
    )
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

    def __init__(self, **data: Any) -> None:
        """Initialize the device system and log initialization details."""
        super().__init__(**data)
        logger.info(
            event="device_system_initialized",
            state=self.state,
            state_code=self.state_code,
            unsupported=self.unsupported,
            upgradable=self.upgradable,
            adopted=self.adopted,
            discovered_via=self.discovered_via,
            led_override=self.led_override,
        )

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Dump model to dict and log changes."""
        data = super().model_dump(**kwargs)
        logger.debug(
            "device_system_dumped",
            state=self.state,
            state_code=self.state_code,
            system_stats=self.system_stats,
            adopted=self.adopted,
            upgradable=self.upgradable,
        )
        return data
