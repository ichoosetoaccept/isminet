"""Wireless settings models for UniFi Network devices."""

from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, model_validator

from .base import UnifiBaseModel, ValidationMixin, WifiMixin
from .validators import validate_mac_list
from .enums import RadioType, RadioProto


class RadioSettings(WifiMixin, ValidationMixin, UnifiBaseModel):
    """Radio settings for UniFi access points."""

    name: str = Field(description="Radio name")
    radio: RadioType = Field(description="Radio type (ng, na, 6e)")
    radio_proto: RadioProto = Field(description="Radio protocol (ng, ac, ax, be)")
    is_enabled: bool = Field(description="Whether radio is enabled")
    channel: int = Field(description="WiFi channel")
    channel_width: int = Field(description="Channel width in MHz")
    tx_power: int = Field(description="Transmit power in dBm", ge=0, le=30)
    tx_power_mode: str = Field(
        description="Transmit power mode (auto, medium, high, low)"
    )
    he_enabled: Optional[bool] = Field(
        None, description="Whether HE (WiFi 6) is enabled"
    )
    dtim_mode: Optional[str] = Field(None, description="DTIM mode")
    dtim_period: Optional[int] = Field(None, description="DTIM period", ge=1, le=255)
    beacon_interval: Optional[int] = Field(
        None, description="Beacon interval in ms", ge=10, le=1000
    )

    @model_validator(mode="after")
    def validate_channel_for_radio(self) -> "RadioSettings":
        """Validate channel based on radio type."""
        if self.radio == RadioType.NG and not 1 <= self.channel <= 14:
            raise ValueError("2.4 GHz channels must be between 1 and 14")
        elif self.radio == RadioType.NA and not 36 <= self.channel <= 165:
            raise ValueError("5 GHz channels must be between 36 and 165")
        elif self.radio == RadioType._6E and not 1 <= self.channel <= 233:
            raise ValueError("6 GHz channels must be between 1 and 233")
        return self

    @field_validator("channel_width")
    @classmethod
    def validate_channel_width(cls, v: int) -> int:
        """Validate channel width is a standard value."""
        if v not in [20, 40, 80, 160, 320]:
            raise ValueError("Channel width must be 20, 40, 80, 160, or 320")
        return v


class NetworkProfile(ValidationMixin, UnifiBaseModel):
    """Network profile for wireless networks."""

    name: str = Field(description="Network name")
    ssid: str = Field(description="Network SSID")
    enabled: bool = Field(description="Whether network is enabled")
    is_guest: bool = Field(description="Whether network is for guests")
    security: str = Field(description="Security type (open, wpa-psk, wpa-enterprise)")
    wpa_mode: str = Field(description="WPA mode (wpa2, wpa3, wpa3-transition)")
    encryption: str = Field(description="Encryption type (none, aes, tkip)")
    vlan_enabled: Optional[bool] = Field(
        None, description="Whether VLAN tagging is enabled"
    )
    vlan_id: Optional[int] = Field(None, description="VLAN ID", ge=1, le=4094)
    hide_ssid: Optional[bool] = Field(None, description="Whether to hide SSID")
    is_private: Optional[bool] = Field(None, description="Whether network is private")
    group_rekey: Optional[int] = Field(
        None, description="Group rekey interval in seconds"
    )
    dtim_mode: Optional[str] = Field(None, description="DTIM mode")
    dtim_period: Optional[int] = Field(None, description="DTIM period", ge=1, le=255)
    mac_filter_enabled: Optional[bool] = Field(
        None, description="Whether MAC filtering is enabled"
    )
    mac_filter_list: Optional[List[str]] = Field(None, description="MAC filter list")
    mac_filter_policy: Optional[str] = Field(
        None, description="MAC filter policy (allow, deny)"
    )
    radius_servers: Optional[List[Dict[str, Any]]] = Field(
        None, description="RADIUS server configuration"
    )
    schedule: Optional[Dict[str, Any]] = Field(None, description="Network schedule")

    _validate_mac_list = field_validator("mac_filter_list")(validate_mac_list)

    @field_validator("security")
    @classmethod
    def validate_security(cls, v: str) -> str:
        """Validate security type."""
        valid_types = {"open", "wpa-psk", "wpa-enterprise"}
        if v not in valid_types:
            raise ValueError(f"Security type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("wpa_mode")
    @classmethod
    def validate_wpa_mode(cls, v: str) -> str:
        """Validate WPA mode."""
        valid_modes = {"wpa2", "wpa3", "wpa3-transition"}
        if v not in valid_modes:
            raise ValueError(f"WPA mode must be one of: {', '.join(valid_modes)}")
        return v

    @field_validator("encryption")
    @classmethod
    def validate_encryption(cls, v: str) -> str:
        """Validate encryption type."""
        valid_types = {"none", "aes", "tkip"}
        if v not in valid_types:
            raise ValueError(
                f"Encryption type must be one of: {', '.join(valid_types)}"
            )
        return v


class WLANConfiguration(ValidationMixin, UnifiBaseModel):
    """WLAN configuration for UniFi devices."""

    radio_table: List[RadioSettings] = Field(description="Radio settings")
    network_profiles: List[NetworkProfile] = Field(description="Network profiles")
    band_steering: Optional[bool] = Field(
        None, description="Whether band steering is enabled"
    )
    band_steering_mode: Optional[str] = Field(None, description="Band steering mode")
    pmf_mode: Optional[str] = Field(
        None, description="PMF mode (disabled, optional, required)"
    )
    minimum_rssi: Optional[int] = Field(
        None, description="Minimum RSSI threshold", le=0
    )
    minimum_uplink: Optional[int] = Field(
        None, description="Minimum uplink rate in Mbps", ge=0
    )
    minimum_downlink: Optional[int] = Field(
        None, description="Minimum downlink rate in Mbps", ge=0
    )
    load_balance_enabled: Optional[bool] = Field(
        None, description="Whether load balancing is enabled"
    )
    max_clients: Optional[int] = Field(
        None, description="Maximum number of clients", ge=0
    )

    @field_validator("pmf_mode")
    @classmethod
    def validate_pmf_mode(cls, v: Optional[str]) -> Optional[str]:
        """Validate PMF mode."""
        if v is not None:
            valid_modes = {"disabled", "optional", "required"}
            if v not in valid_modes:
                raise ValueError(f"PMF mode must be one of: {', '.join(valid_modes)}")
        return v
