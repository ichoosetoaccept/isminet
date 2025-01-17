"""Network configuration models for UniFi Network devices."""

from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, model_validator
import ipaddress

from .base import UnifiBaseModel, ValidationMixin
from .validators import validate_ip, validate_ip_list
from .enums import DHCPMode


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
        """
        Validates the DHCP range configuration when server mode is enabled.

        Ensures that both start and end IP addresses are specified when DHCP server mode is active.

        Raises:
            ValueError: If DHCP server mode is enabled but start or end IP addresses are not set.

        Returns:
            DHCPConfiguration: The validated configuration instance.
        """
        if self.mode == DHCPMode.SERVER and self.enabled:
            if not all([self.start, self.end]):
                raise ValueError(
                    "DHCP range start and end must be set when server mode is enabled"
                )
            # Could add IP range validation here if needed
        return self


class VLANConfiguration(UnifiBaseModel):
    """VLAN configuration model."""

    id: int = Field(description="VLAN ID", ge=1, le=4094)
    name: str = Field(description="VLAN name", min_length=1)
    enabled: bool = Field(description="VLAN enabled")
    subnet: str = Field(description="VLAN subnet")
    gateway_ip: str = Field(description="Gateway IP address")
    tagged_ports: List[int] = Field(description="Tagged ports", default_factory=list)
    untagged_ports: List[int] = Field(
        description="Untagged ports", default_factory=list
    )
    dhcp: Optional[DHCPConfiguration] = Field(None, description="DHCP configuration")

    @model_validator(mode="after")
    def validate_ports(self) -> "VLANConfiguration":
        """Validate port configuration."""
        tagged_set = set(self.tagged_ports)
        untagged_set = set(self.untagged_ports)
        if tagged_set & untagged_set:
            raise ValueError("Port cannot be both tagged and untagged")
        return self


class NetworkConfiguration(UnifiBaseModel):
    """Network configuration model."""

    name: str = Field(description="Network name", min_length=1)
    enabled: bool = Field(description="Network enabled")
    purpose: str = Field(description="Network purpose")
    subnet: str = Field(description="Network subnet")
    vlan_enabled: bool = Field(description="VLAN enabled")
    vlans: List[VLANConfiguration] = Field(description="VLAN configuration")
    dhcp: Optional[DHCPConfiguration] = Field(None, description="DHCP configuration")
    ipv6_ra_enabled: Optional[bool] = Field(
        None, description="IPv6 router advertisements enabled"
    )
    ipv6_interface_type: Optional[str] = Field(None, description="IPv6 interface type")
    ipv6_pd_prefixid: Optional[int] = Field(
        None, description="IPv6 prefix delegation ID", ge=0
    )
    ipv6_addresses: Optional[List[str]] = Field(None, description="IPv6 addresses")

    @field_validator("ipv6_interface_type")
    @classmethod
    def validate_ipv6_interface_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate IPv6 interface type."""
        if v is not None and v not in ["upstream", "downstream"]:
            raise ValueError("IPv6 interface type must be 'upstream' or 'downstream'")
        return v

    @field_validator("ipv6_addresses")
    @classmethod
    def validate_ipv6_addresses(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate IPv6 addresses."""
        if v is not None:
            for addr in v:
                try:
                    ipaddress.IPv6Address(addr)
                except ValueError:
                    raise ValueError("Invalid IPv6 address format")
        return v
