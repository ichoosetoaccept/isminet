"""Wireless settings models for UniFi Network devices."""

from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, ValidationInfo

from .base import UnifiBaseModel, ValidationMixin
from .validators import MAC_PATTERN


class RadioSettings(ValidationMixin, UnifiBaseModel):
    """Radio settings for a wireless network interface."""

    name: str = Field(description="Radio name")
    enabled: bool = Field(description="Whether the radio is enabled")
    radio: str = Field(description="Radio type (ng, na, 6e) with optional protocol")
    channel: int = Field(description="Channel number")
    channel_width: int = Field(description="Channel width in MHz")
    tx_power: int = Field(description="Transmit power in dBm")
    tx_power_mode: str = Field(description="Transmit power mode")

    @field_validator("radio")
    @classmethod
    def validate_radio(cls, v: str) -> str:
        """Validate radio type and protocol combinations."""
        if "+" in v:
            radio_type, proto = v.split("+")
            if radio_type not in {"ng", "na", "6e"}:
                raise ValueError("Invalid radio type")
            if radio_type == "ng":
                raise ValueError(
                    "Invalid radio type"
                )  # 2.4GHz doesn't support protocol specification
            if radio_type == "na" and proto not in {"ac", "ax"}:
                raise ValueError("5GHz radio must use AC or AX")
            if radio_type == "6e" and proto != "ax":
                raise ValueError("6GHz radio only supports AX")
        else:
            if v not in {"ng", "na", "6e"}:
                raise ValueError("Invalid radio type")

        return v

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: int, info: ValidationInfo) -> int:
        """Validate channel number based on radio type."""
        data = info.data
        radio = data.get("radio", "").split("+")[
            0
        ]  # Get base radio type without protocol

        if radio == "ng" and not 1 <= v <= 14:
            raise ValueError("Invalid 2.4GHz channel")
        elif radio == "na" and not 36 <= v <= 165:
            raise ValueError("Invalid 5GHz channel")
        elif radio == "6e" and not 1 <= v <= 195:
            raise ValueError("Invalid 6GHz channel")

        return v

    @field_validator("channel_width")
    @classmethod
    def validate_channel_width(cls, v: int) -> int:
        """Validate channel width."""
        if v not in [20, 40, 80, 160]:
            raise ValueError("Invalid channel width")
        return v

    @field_validator("tx_power")
    @classmethod
    def validate_tx_power(cls, v: int) -> int:
        """Validate tx_power field."""
        if not 0 <= v <= 30:
            raise ValueError("TX power must be between 0 and 30")
        return v

    @field_validator("tx_power_mode")
    @classmethod
    def validate_tx_power_mode(cls, v: str) -> str:
        """Validate transmit power mode."""
        if v not in ["auto", "medium", "high", "low", "custom"]:
            raise ValueError("Invalid TX power mode")
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
    vlan_id: Optional[int] = Field(None, description="VLAN ID")
    hide_ssid: Optional[bool] = Field(None, description="Whether to hide SSID")
    is_private: Optional[bool] = Field(None, description="Whether network is private")
    group_rekey: Optional[int] = Field(
        None, description="Group rekey interval in seconds"
    )
    dtim_mode: Optional[str] = Field(None, description="DTIM mode")
    dtim_period: Optional[int] = Field(None, description="DTIM period")
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

    @field_validator("mac_filter_list")
    @classmethod
    def validate_mac_filter_list(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate MAC filter list."""
        if v is not None:
            for mac in v:
                if not MAC_PATTERN.match(mac):
                    raise ValueError("Invalid MAC address format")
        return v

    @field_validator("security")
    @classmethod
    def validate_security(cls, v: str) -> str:
        """Validate security type."""
        valid_types = {"open", "wpa-psk", "wpa-enterprise"}
        if v not in valid_types:
            raise ValueError("Invalid security type")
        return v

    @field_validator("wpa_mode")
    @classmethod
    def validate_wpa_mode(cls, v: str) -> str:
        """Validate WPA mode."""
        valid_modes = {"wpa2", "wpa3", "wpa3-transition"}
        if v not in valid_modes:
            raise ValueError("Invalid WPA mode")
        return v

    @field_validator("encryption")
    @classmethod
    def validate_encryption(cls, v: str) -> str:
        """Validate encryption type."""
        valid_types = {"none", "aes", "tkip"}
        if v not in valid_types:
            raise ValueError("Invalid encryption type")
        return v

    @field_validator("vlan_id")
    @classmethod
    def validate_vlan_id(cls, v: Optional[int]) -> Optional[int]:
        """Validate VLAN ID."""
        if v is not None and not (1 <= v <= 4094):
            raise ValueError("VLAN ID must be between 1 and 4095")
        return v


class WLANConfiguration(UnifiBaseModel):
    """WLAN configuration for UniFi devices."""

    radio_table: List[RadioSettings] = Field(description="Radio settings")
    network_profiles: List[NetworkProfile] = Field(description="Network profiles")
    pmf_mode: Optional[str] = Field(
        None, description="Protected Management Frames mode"
    )
    minimum_rssi: Optional[int] = Field(None, description="Minimum RSSI threshold")
    minimum_uplink: Optional[int] = Field(None, description="Minimum uplink speed")
    minimum_downlink: Optional[int] = Field(None, description="Minimum downlink speed")
    max_clients: Optional[int] = Field(None, description="Maximum number of clients")

    @field_validator("pmf_mode")
    @classmethod
    def validate_pmf_mode(cls, v: Optional[str]) -> Optional[str]:
        """Validate PMF mode."""
        if v is not None and v not in {"disabled", "optional", "required"}:
            raise ValueError("Invalid PMF mode")
        return v

    @field_validator("minimum_rssi")
    @classmethod
    def validate_minimum_rssi(cls, v: Optional[int]) -> Optional[int]:
        """Validate minimum RSSI."""
        if v is not None and not (-100 <= v <= 0):
            raise ValueError("RSSI must be between -100 and 0")
        return v

    @field_validator("minimum_uplink", "minimum_downlink")
    @classmethod
    def validate_rate_limit(cls, v: Optional[int]) -> Optional[int]:
        """Validate rate limit."""
        if v is not None and v < 0:
            raise ValueError("Rate limit must be non-negative")
        return v

    @field_validator("max_clients")
    @classmethod
    def validate_max_clients(cls, v: Optional[int]) -> Optional[int]:
        """Validate maximum clients."""
        if v is not None and v < 1:
            raise ValueError("Maximum clients must be greater than 0")
        return v
