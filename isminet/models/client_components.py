"""Client component models for UniFi Network devices."""

from typing import Optional, List
from pydantic import Field, field_validator

from .base import UnifiBaseModel, ValidationMixin
from .validators import validate_mac, validate_ip, validate_ipv6_list


class ClientNetwork(ValidationMixin, UnifiBaseModel):
    """Network configuration for UniFi clients."""

    last_ip: Optional[str] = Field(None, description="IP address")
    is_wired: bool = Field(description="Whether client is wired")
    use_fixedip: Optional[bool] = Field(None, description="Whether using fixed IP")
    fixed_ip: Optional[str] = Field(None, description="Fixed IP address")
    ipv6_addresses: Optional[List[str]] = Field(None, description="IPv6 addresses")
    gw_mac: Optional[str] = Field(None, description="Gateway MAC address")
    gw_vlan: Optional[int] = Field(None, description="Gateway VLAN ID", ge=0, le=4095)
    dhcpend_time: Optional[int] = Field(None, description="DHCP lease end time")
    wired_rate_mbps: Optional[int] = Field(
        None, description="Wired connection speed in Mbps", ge=0
    )

    _validate_mac = field_validator("gw_mac")(validate_mac)
    _validate_ip = field_validator("last_ip", "fixed_ip")(validate_ip)
    _validate_ipv6_list = field_validator("ipv6_addresses")(validate_ipv6_list)


class ClientTracking(ValidationMixin, UnifiBaseModel):
    """Tracking information for UniFi clients."""

    sw_depth: Optional[int] = Field(None, description="Switch depth", ge=0)
    sw_port: Optional[int] = Field(None, description="Switch port number", ge=1)
    sw_mac: Optional[str] = Field(None, description="Switch MAC address")
    uptime_by_uap: Optional[int] = Field(None, description="Uptime tracked by AP", ge=0)
    uptime_by_usw: Optional[int] = Field(
        None, description="Uptime tracked by switch", ge=0
    )
    uptime_by_ugw: Optional[int] = Field(
        None, description="Uptime tracked by gateway", ge=0
    )
    last_seen_by_uap: Optional[int] = Field(None, description="Last seen by AP")
    last_seen_by_usw: Optional[int] = Field(None, description="Last seen by switch")
    last_seen_by_ugw: Optional[int] = Field(None, description="Last seen by gateway")
    last_reachable_by_gw: Optional[int] = Field(
        None, description="Last reachable by gateway"
    )

    _validate_mac = field_validator("sw_mac")(validate_mac)


class ClientGuest(ValidationMixin, UnifiBaseModel):
    """Guest-specific information for UniFi clients."""

    is_guest_by_uap: Optional[bool] = Field(
        None, description="Guest status tracked by AP"
    )
    is_guest_by_usw: Optional[bool] = Field(
        None, description="Guest status tracked by switch"
    )
    is_guest_by_ugw: Optional[bool] = Field(
        None, description="Guest status tracked by gateway"
    )


class ClientDNS(ValidationMixin, UnifiBaseModel):
    """DNS configuration for UniFi clients."""

    hostname: str = Field(description="Client hostname")
    hostname_source: Optional[str] = Field(None, description="Hostname source")
    local_dns_record_enabled: Optional[bool] = Field(
        None, description="Whether local DNS record is enabled"
    )
    local_dns_record: Optional[str] = Field(None, description="Local DNS record")
