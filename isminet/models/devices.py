"""Device models for the UniFi Network API."""

from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, ValidationInfo
import ipaddress

from .base import UnifiBaseModel
from .enums import DeviceType, RadioType, RadioProto
from .validators import (
    validate_mac,
    validate_ip,
    MAC_PATTERN,
    VERSION_PATTERN,
)
from .system import SystemHealth


class WifiStats(UnifiBaseModel):
    """WiFi-specific statistics for wireless clients."""

    ap_mac: str = Field(description="MAC address", min_length=1)
    radio: RadioType = Field(description="Radio type (ng, na, 6e)")
    radio_proto: RadioProto = Field(description="Radio protocol (ng, ac, ax, be)")
    essid: str = Field(description="Network SSID", min_length=1)
    bssid: str = Field(description="MAC address", min_length=1)
    signal: int = Field(description="Signal strength in dBm", lt=0)
    noise: int = Field(description="Noise level in dBm", lt=0)
    channel: Optional[int] = Field(None, description="WiFi channel")
    nss: Optional[int] = Field(
        None, description="Number of spatial streams", ge=1, le=8
    )
    powersave_enabled: Optional[bool] = Field(
        None, description="Whether power save is enabled"
    )
    is_11r: Optional[bool] = Field(None, description="Whether 802.11r is enabled")
    idletime: Optional[int] = Field(None, description="Idle time in seconds", ge=0)
    wifi_tx_attempts: Optional[int] = Field(
        None, description="WiFi transmit attempts", ge=0
    )
    wifi_tx_dropped: Optional[int] = Field(
        None, description="WiFi dropped transmits", ge=0
    )
    wifi_tx_retries_percentage: Optional[float] = Field(
        None, description="WiFi retries percentage", ge=0, le=100
    )
    is_mlo: Optional[bool] = Field(None, description="Whether MLO is enabled")
    tx_mcs: Optional[int] = Field(None, description="Transmit MCS index", ge=0, le=11)
    tx_retries: Optional[int] = Field(None, description="Transmit retry count", ge=0)
    tx_power: Optional[int] = Field(None, description="Transmit power in dBm", ge=0)
    tx_rate: Optional[int] = Field(None, description="Transmit rate in Mbps", ge=0)
    rx_rate: Optional[int] = Field(None, description="Receive rate in Mbps", ge=0)
    channel_width: Optional[int] = Field(None, description="Channel width in MHz")
    satisfaction: Optional[int] = Field(
        None, description="Client satisfaction", ge=0, le=100
    )

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        """Validate channel based on radio type."""
        if v is not None:
            radio = info.data.get("radio")
            if radio == RadioType.NG and not (1 <= v <= 14):
                raise ValueError("2.4 GHz channels must be between 1 and 14")
            elif radio == RadioType.NA and not (36 <= v <= 165):
                raise ValueError("5 GHz channels must be between 36 and 165")
            elif radio == RadioType._6E and not (1 <= v <= 233):
                raise ValueError("6 GHz channels must be between 1 and 233")
        return v

    @field_validator("channel_width")
    @classmethod
    def validate_channel_width(cls, v: Optional[int]) -> Optional[int]:
        """Validate channel width is a standard value."""
        if v is not None and v not in {20, 40, 80, 160, 320}:
            raise ValueError("Channel width must be 20, 40, 80, 160, or 320")
        return v

    @field_validator("ap_mac", "bssid")
    @classmethod
    def validate_mac_fields(cls, v: str) -> str:
        """Validate MAC address fields."""
        if not validate_mac(v):
            raise ValueError("Invalid MAC address format")
        return v


class PortStats(UnifiBaseModel):
    """Port statistics and configuration."""

    port_idx: int = Field(description="Port index", ge=1)
    name: str = Field(description="Port name", min_length=1)
    media: str = Field(description="Port media type (GE, SFP+)")
    speed: int = Field(description="Current port speed", ge=0)
    up: bool = Field(description="Whether port is up")
    is_uplink: bool = Field(description="Whether port is an uplink")
    mac: str = Field(description="MAC address", min_length=1)
    rx_errors: int = Field(description="Total receive errors", ge=0)
    tx_errors: int = Field(description="Total transmit errors", ge=0)
    type: str = Field(description="Port type", min_length=1)
    ip: Optional[str] = Field(None, description="IP address")
    masked: Optional[bool] = Field(None, description="Whether port is masked")
    aggregated_by: Optional[bool] = Field(
        None, description="Whether port is aggregated"
    )
    native_networkconf_id: Optional[str] = Field(
        None, description="Native network configuration ID"
    )
    ifname: Optional[str] = Field(None, description="Interface name")
    port_delta: Optional[Dict[str, Any]] = Field(
        None, description="Port delta statistics"
    )
    rx_multicast: Optional[int] = Field(
        None, description="Multicast packets received", ge=0
    )
    tx_multicast: Optional[int] = Field(
        None, description="Multicast packets transmitted", ge=0
    )
    rx_broadcast: Optional[int] = Field(
        None, description="Broadcast packets received", ge=0
    )
    tx_broadcast: Optional[int] = Field(
        None, description="Broadcast packets transmitted", ge=0
    )
    tx_bytes: Optional[int] = Field(None, description="Total bytes transmitted", ge=0)
    rx_bytes: Optional[int] = Field(None, description="Total bytes received", ge=0)
    tx_packets: Optional[int] = Field(
        None, description="Total packets transmitted", ge=0
    )
    rx_packets: Optional[int] = Field(None, description="Total packets received", ge=0)

    @field_validator("mac")
    @classmethod
    def validate_mac(cls, v: str) -> str:
        """Validate MAC address."""
        if not validate_mac(v):
            raise ValueError("Invalid MAC address format")
        return v

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address."""
        if v is not None and not validate_ip(v):
            raise ValueError("Invalid IPv4 address")
        return v


class Device(UnifiBaseModel):
    """Device model."""

    type: DeviceType = Field(description="Device type")
    mac: str = Field(description="MAC address")
    model: str = Field(description="Device model")
    name: str = Field(description="Device name")
    version: str = Field(description="Firmware version")
    uptime: int = Field(description="Device uptime", ge=0)
    adopted: bool = Field(description="Device adopted")
    status: str = Field(description="Device status")
    upgradable: bool = Field(description="Device can be upgraded")
    update_available: bool = Field(description="Device update available")
    health: Optional[List[SystemHealth]] = Field(
        None, description="Device health status"
    )
    hostname: Optional[str] = Field(None, description="Device hostname")
    ip: Optional[str] = Field(None, description="Device IP address")
    site_id: Optional[str] = Field(None, description="Site ID")
    first_seen: Optional[int] = Field(None, description="First seen timestamp")
    last_seen: Optional[int] = Field(None, description="Last seen timestamp")
    is_guest: Optional[bool] = Field(None, description="Guest device")

    @field_validator("mac")
    @classmethod
    def validate_mac(cls, v: str) -> str:
        """Validate MAC address."""
        if not MAC_PATTERN.match(v):
            raise ValueError("Invalid MAC address format")
        return v

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address."""
        if v is not None:
            try:
                ipaddress.IPv4Address(v)
            except ValueError:
                raise ValueError("Invalid IPv4 address")
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version field."""
        if not VERSION_PATTERN.match(v):
            raise ValueError("Version must be in format x.y.z")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status field."""
        valid_statuses = {"connected", "disconnected", "pending"}
        if v not in valid_statuses:
            raise ValueError("Status must be one of: connected, disconnected, pending")
        return v

    @field_validator("health")
    @classmethod
    def validate_health(cls, v: Optional[List[SystemHealth]]) -> List[SystemHealth]:
        """Validate health field."""
        if v is None:
            return []
        return v


class Client(UnifiBaseModel):
    """UniFi Network client device."""

    mac: str = Field(description="MAC address", min_length=1)
    first_seen: int = Field(description="First seen timestamp", ge=0)
    hostname: str = Field(description="Client hostname", min_length=1)
    ip: Optional[str] = Field(None, description="IP address")
    name: Optional[str] = Field(None, description="Client name")
    is_guest: Optional[bool] = Field(None, description="Whether client is a guest")
    is_wired: Optional[bool] = Field(None, description="Whether client is wired")
    last_seen: Optional[int] = Field(None, description="Last seen timestamp", ge=0)
    uptime: Optional[int] = Field(None, description="Client uptime in seconds", ge=0)
    tx_bytes: Optional[int] = Field(None, description="Total bytes transmitted", ge=0)
    rx_bytes: Optional[int] = Field(None, description="Total bytes received", ge=0)
    tx_packets: Optional[int] = Field(
        None, description="Total packets transmitted", ge=0
    )
    rx_packets: Optional[int] = Field(None, description="Total packets received", ge=0)
    tx_retries: Optional[int] = Field(None, description="Total retries", ge=0)
    wifi_tx_attempts: Optional[int] = Field(
        None, description="WiFi transmit attempts", ge=0
    )
    satisfaction: Optional[int] = Field(
        None, description="Client satisfaction", ge=0, le=100
    )
    signal: Optional[int] = Field(None, description="Signal strength in dBm", lt=0)
    noise: Optional[int] = Field(None, description="Noise level in dBm", lt=0)
    channel: Optional[int] = Field(None, description="WiFi channel")
    radio: Optional[str] = Field(None, description="Radio type (ng, na, 6e)")
    radio_proto: Optional[str] = Field(
        None, description="Radio protocol (ng, ac, ax, be)"
    )
    essid: Optional[str] = Field(None, description="Network SSID")
    bssid: Optional[str] = Field(None, description="BSSID")
    powersave_enabled: Optional[bool] = Field(
        None, description="Whether power save is enabled"
    )
    is_11r: Optional[bool] = Field(None, description="Whether 802.11r is enabled")
    network_id: Optional[str] = Field(None, description="Network ID")
    site_id: Optional[str] = Field(None, description="Site ID")
    oui: Optional[str] = Field(None, description="OUI vendor")
    radio_name: Optional[str] = Field(None, description="Radio name")
    anomalies: Optional[int] = Field(None, description="Client anomalies", ge=0)
    fingerprint: Optional[Dict[str, Any]] = Field(
        None, description="Client fingerprint"
    )
    satisfaction_reason: Optional[str] = Field(None, description="Satisfaction reason")
    satisfaction_avg: Optional[Dict[str, Any]] = Field(
        None, description="Average satisfaction stats"
    )
    wifi_stats: Optional[WifiStats] = Field(
        None, description="WiFi statistics if wireless client"
    )

    @field_validator("mac")
    @classmethod
    def validate_mac(cls, v: str) -> str:
        """Validate MAC address."""
        if not validate_mac(v):
            raise ValueError("Invalid MAC address format")
        return v

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address."""
        if v is not None and not validate_ip(v):
            raise ValueError("Invalid IPv4 address")
        return v

    @field_validator("bssid")
    @classmethod
    def validate_bssid(cls, v: Optional[str]) -> Optional[str]:
        """Validate BSSID."""
        if v is not None and not validate_mac(v):
            raise ValueError("Invalid MAC address format")
        return v

    @field_validator("radio")
    @classmethod
    def validate_radio(cls, v: Optional[str]) -> Optional[str]:
        """Validate radio type."""
        if v is not None and v not in ["ng", "na", "6e"]:
            raise ValueError("Radio type must be one of: ng, na, 6e")
        return v

    @field_validator("radio_proto")
    @classmethod
    def validate_radio_proto(cls, v: Optional[str]) -> Optional[str]:
        """Validate radio protocol."""
        if v is not None and v not in ["ng", "ac", "ax", "be"]:
            raise ValueError("Radio protocol must be one of: ng, ac, ax, be")
        return v
