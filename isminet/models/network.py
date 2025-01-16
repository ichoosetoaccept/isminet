"""Network configuration models for UniFi Network devices."""

from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, model_validator

from .base import UnifiBaseModel, ValidationMixin, NetworkMixin
from .validators import validate_ip, validate_ip_list
from .enums import DHCPMode, IGMPMode


class DHCPConfiguration(ValidationMixin, UnifiBaseModel):
    """DHCP server configuration."""

    mode: DHCPMode = Field(description="DHCP mode (disabled, server, relay)")
    enabled: bool = Field(description="Whether DHCP is enabled")
    start: Optional[str] = Field(None, description="DHCP range start IP")
    end: Optional[str] = Field(None, description="DHCP range end IP")
    lease_time: Optional[int] = Field(
        None, description="Lease time in seconds", ge=300, le=2592000
    )
    dns: Optional[List[str]] = Field(None, description="DNS servers")
    gateway_ip: Optional[str] = Field(None, description="Gateway IP address")
    unifi_controller: Optional[str] = Field(None, description="UniFi controller IP")
    ntp_server: Optional[str] = Field(None, description="NTP server IP")
    domain_name: Optional[str] = Field(None, description="Domain name")
    tftp_server: Optional[str] = Field(None, description="TFTP server IP")
    boot_file: Optional[str] = Field(None, description="Boot file name")
    static_leases: Optional[List[Dict[str, Any]]] = Field(
        None, description="Static DHCP leases"
    )

    _validate_ip = field_validator(
        "start", "end", "gateway_ip", "unifi_controller", "ntp_server", "tftp_server"
    )(validate_ip)
    _validate_ip_list = field_validator("dns")(validate_ip_list)

    @model_validator(mode="after")
    def validate_dhcp_range(self) -> "DHCPConfiguration":
        """Validate DHCP range if server mode is enabled."""
        if self.mode == DHCPMode.SERVER and self.enabled:
            if not all([self.start, self.end]):
                raise ValueError(
                    "DHCP range start and end must be set when server mode is enabled"
                )
            # Could add IP range validation here if needed
        return self


class VLANConfiguration(ValidationMixin, NetworkMixin, UnifiBaseModel):
    """VLAN configuration."""

    vlan_id: int = Field(description="VLAN ID", ge=1, le=4094)
    name: str = Field(description="VLAN name")
    enabled: bool = Field(description="Whether VLAN is enabled")
    subnet: str = Field(description="VLAN subnet")
    dhcp: Optional[DHCPConfiguration] = Field(None, description="DHCP configuration")
    igmp_snooping: Optional[bool] = Field(None, description="IGMP snooping enabled")
    igmp_mode: Optional[IGMPMode] = Field(None, description="IGMP mode")
    multicast_dns: Optional[bool] = Field(None, description="mDNS enabled")
    tagged_ports: Optional[List[int]] = Field(None, description="Tagged ports")
    untagged_ports: Optional[List[int]] = Field(None, description="Untagged ports")

    _validate_ip = field_validator("subnet")(validate_ip)

    @model_validator(mode="after")
    def validate_ports(self) -> "VLANConfiguration":
        """Validate port configurations."""
        if self.tagged_ports and self.untagged_ports:
            common_ports = set(self.tagged_ports) & set(self.untagged_ports)
            if common_ports:
                raise ValueError(
                    f"Ports {common_ports} cannot be both tagged and untagged"
                )
        return self


class NetworkConfiguration(ValidationMixin, UnifiBaseModel):
    """Network configuration for UniFi devices."""

    name: str = Field(description="Network name")
    purpose: str = Field(description="Network purpose (corporate, guest, iot)")
    enabled: bool = Field(description="Whether network is enabled")
    subnet: str = Field(description="Network subnet")
    vlan_enabled: bool = Field(description="Whether VLAN is enabled")
    vlans: Optional[List[VLANConfiguration]] = Field(
        None, description="VLAN configurations"
    )
    dhcp: Optional[DHCPConfiguration] = Field(None, description="DHCP configuration")
    igmp_snooping: Optional[bool] = Field(None, description="IGMP snooping enabled")
    igmp_mode: Optional[IGMPMode] = Field(None, description="IGMP mode")
    multicast_dns: Optional[bool] = Field(None, description="mDNS enabled")
    multicast_enhancement: Optional[bool] = Field(
        None, description="Multicast enhancement"
    )
    ipv6_interface_type: Optional[str] = Field(None, description="IPv6 interface type")
    ipv6_ra_enabled: Optional[bool] = Field(None, description="IPv6 RA enabled")
    ipv6_pd_interface: Optional[str] = Field(None, description="IPv6 PD interface")
    ipv6_pd_prefixid: Optional[int] = Field(None, description="IPv6 PD prefix ID")
    ipv6_pd_start: Optional[str] = Field(None, description="IPv6 PD start")
    ipv6_pd_stop: Optional[str] = Field(None, description="IPv6 PD stop")

    _validate_ip = field_validator("subnet")(validate_ip)

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, v: str) -> str:
        """Validate network purpose."""
        valid_purposes = {"corporate", "guest", "iot"}
        if v not in valid_purposes:
            raise ValueError(f"Purpose must be one of: {', '.join(valid_purposes)}")
        return v

    @model_validator(mode="after")
    def validate_vlan_config(self) -> "NetworkConfiguration":
        """Validate VLAN configuration."""
        if self.vlan_enabled and not self.vlans:
            raise ValueError(
                "VLAN configurations must be provided when VLAN is enabled"
            )
        if self.vlans:
            vlan_ids = [vlan.vlan_id for vlan in self.vlans]
            if len(vlan_ids) != len(set(vlan_ids)):
                raise ValueError("Duplicate VLAN IDs are not allowed")
        return self
