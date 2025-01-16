"""Device models for the UniFi Network API."""

from typing import Optional, List
from ipaddress import IPv4Address, IPv6Address
import re
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    ValidationInfo,
    model_validator,
)

MAC_PATTERN = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")


class RadioType(str, Enum):
    """Radio types."""

    NG = "ng"  # 2.4 GHz
    NA = "na"  # 5 GHz
    _6E = "6e"  # 6 GHz


class RadioProto(str, Enum):
    """Radio protocols."""

    NG = "ng"  # 802.11n
    AC = "ac"  # 802.11ac
    AX = "ax"  # 802.11ax (WiFi 6)
    BE = "be"  # 802.11be (WiFi 7)


class DeviceType(str, Enum):
    """Device types."""

    UAP = "uap"  # UniFi Access Point
    USW = "usw"  # UniFi Switch
    UGW = "ugw"  # UniFi Gateway
    UDM = "udm"  # UniFi Dream Machine
    UDMPRO = "udm-pro"  # UniFi Dream Machine Pro


class PoEMode(str, Enum):
    """PoE modes."""

    OFF = "off"
    AUTO = "auto"
    PASV24 = "pasv24"
    AUTO_PLUS = "auto+"


class LedOverride(str, Enum):
    """LED override settings."""

    ON = "on"
    OFF = "off"
    DEFAULT = "default"


class PortStats(BaseModel):
    """Port statistics and configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    port_idx: int = Field(description="Port index", ge=1)
    name: str = Field(description="Port name")
    media: str = Field(description="Port media type (GE, SFP+)")
    port_poe: bool = Field(description="Whether port supports PoE")
    speed: int = Field(description="Current port speed", ge=0)
    up: bool = Field(description="Whether port is up")
    is_uplink: bool = Field(description="Whether port is an uplink")
    mac: str = Field(description="Port MAC address")
    rx_bytes: int = Field(description="Total bytes received", ge=0)
    tx_bytes: int = Field(description="Total bytes transmitted", ge=0)
    rx_packets: int = Field(description="Total packets received", ge=0)
    tx_packets: int = Field(description="Total packets transmitted", ge=0)
    rx_errors: int = Field(description="Total receive errors", ge=0)
    tx_errors: int = Field(description="Total transmit errors", ge=0)
    type: str = Field(description="Port type")
    poe_power: Optional[str] = Field(None, description="PoE power consumption")
    network_name: Optional[str] = Field(None, description="Network name")
    ip: Optional[str] = Field(None, description="Port IP address")
    netmask: Optional[str] = Field(None, description="Port netmask")
    sfp_vendor: Optional[str] = Field(None, description="SFP module vendor")
    sfp_part: Optional[str] = Field(None, description="SFP module part number")
    sfp_serial: Optional[str] = Field(None, description="SFP module serial number")
    sfp_temperature: Optional[float] = Field(None, description="SFP module temperature")
    sfp_voltage: Optional[float] = Field(None, description="SFP module voltage", ge=0)
    sfp_rxpower: Optional[float] = Field(
        None, description="SFP module RX power in dBm", le=0
    )
    sfp_txpower: Optional[float] = Field(
        None, description="SFP module TX power in dBm", le=0
    )
    bytes_r: Optional[float] = Field(None, description="Current bytes rate", ge=0)
    tx_bytes_r: Optional[float] = Field(
        None, description="Current transmit bytes rate", ge=0
    )
    rx_bytes_r: Optional[float] = Field(
        None, description="Current receive bytes rate", ge=0
    )
    autoneg: Optional[bool] = Field(None, description="Auto-negotiation enabled")
    flowctrl_rx: Optional[bool] = Field(None, description="RX flow control enabled")
    flowctrl_tx: Optional[bool] = Field(None, description="TX flow control enabled")
    full_duplex: Optional[bool] = Field(None, description="Full duplex enabled")
    masked: Optional[bool] = Field(None, description="Whether port is masked")
    aggregated_by: Optional[bool] = Field(
        None, description="Whether port is aggregated"
    )
    poe_mode: Optional[PoEMode] = Field(None, description="PoE mode")
    poe_enable: Optional[bool] = Field(None, description="PoE enabled")
    poe_caps: Optional[int] = Field(None, description="PoE capabilities")
    speed_caps: Optional[int] = Field(None, description="Speed capabilities")
    op_mode: Optional[str] = Field(None, description="Operation mode")
    stormctrl_bcast_enabled: Optional[bool] = Field(
        None, description="Broadcast storm control enabled"
    )
    stormctrl_bcast_rate: Optional[int] = Field(
        None, description="Broadcast storm control rate", ge=0, le=100
    )
    stormctrl_mcast_enabled: Optional[bool] = Field(
        None, description="Multicast storm control enabled"
    )
    stormctrl_mcast_rate: Optional[int] = Field(
        None, description="Multicast storm control rate", ge=0, le=100
    )
    stormctrl_ucast_enabled: Optional[bool] = Field(
        None, description="Unicast storm control enabled"
    )
    stormctrl_ucast_rate: Optional[int] = Field(
        None, description="Unicast storm control rate", ge=0, le=100
    )
    port_security_enabled: Optional[bool] = Field(
        None, description="Port security enabled"
    )
    port_security_mac_address: Optional[List[str]] = Field(
        None, description="Allowed MAC addresses"
    )
    isolation: Optional[bool] = Field(None, description="Port isolation enabled")
    native_networkconf_id: Optional[str] = Field(
        None, description="Native network configuration ID"
    )
    ifname: Optional[str] = Field(None, description="Interface name")
    port_delta: Optional[dict] = Field(None, description="Port delta statistics")
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

    @field_validator("mac")
    @classmethod
    def validate_mac(cls, v: str) -> str:
        """Validate MAC address format."""
        if not MAC_PATTERN.match(v):
            raise ValueError("Invalid MAC address format")
        return v.lower()

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address format."""
        if v is None:
            return None
        try:
            IPv4Address(v)
            return v
        except ValueError as e:
            raise ValueError(f"Invalid IP address: {e}")

    @field_validator("netmask")
    @classmethod
    def validate_netmask(cls, v: Optional[str]) -> Optional[str]:
        """Validate netmask format."""
        if v is None:
            return None
        try:
            # Convert to int to check if it's a valid netmask
            mask = IPv4Address(v)
            mask_int = int(mask)
            # Check if bits are contiguous
            mask_bin = bin(mask_int)[2:].rjust(32, "0")
            if "01" in mask_bin:
                raise ValueError("Invalid netmask: bits must be contiguous")
            return v
        except ValueError as e:
            raise ValueError(f"Invalid netmask: {e}")

    @field_validator("port_security_mac_address")
    @classmethod
    def validate_mac_list(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate list of MAC addresses."""
        if v is None:
            return None
        validated = []
        for mac in v:
            if not MAC_PATTERN.match(mac):
                raise ValueError(f"Invalid MAC address format: {mac}")
            validated.append(mac.lower())
        return validated


class WifiStats(BaseModel):
    """WiFi-specific statistics for wireless clients."""

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    ap_mac: str = Field(description="Access point MAC address")
    channel: int = Field(description="WiFi channel")
    radio: RadioType = Field(description="Radio type (ng, na, 6e)")
    radio_proto: RadioProto = Field(description="Radio protocol (ng, ac, ax, be)")
    essid: str = Field(description="Network SSID")
    bssid: str = Field(description="BSSID")
    signal: int = Field(description="Signal strength in dBm", le=0)
    noise: int = Field(description="Noise level in dBm", le=0)
    tx_rate: int = Field(description="Transmit rate in Kbps", ge=0)
    rx_rate: int = Field(description="Receive rate in Kbps", ge=0)
    tx_power: int = Field(description="Transmit power")
    tx_retries: int = Field(description="Number of transmit retries", ge=0)
    satisfaction: Optional[int] = Field(
        None, description="Client satisfaction score (0-100)", ge=0, le=100
    )
    ccq: Optional[int] = Field(
        None, description="Client connection quality", ge=0, le=1000
    )
    nss: Optional[int] = Field(
        None, description="Number of spatial streams", ge=1, le=8
    )
    channel_width: Optional[int] = Field(None, description="Channel width in MHz")
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
    tx_retry_burst_count: Optional[int] = Field(
        None, description="Transmit retry burst count", ge=0
    )
    radio_name: Optional[str] = Field(None, description="Radio name")
    authorized: Optional[bool] = Field(None, description="Whether client is authorized")
    qos_policy_applied: Optional[bool] = Field(
        None, description="Whether QoS policy is applied"
    )

    @field_validator("signal", "noise")
    @classmethod
    def validate_dbm(cls, v: int) -> int:
        """Validate dBm values are in reasonable range."""
        if not -100 <= v <= 0:
            raise ValueError("dBm value must be between -100 and 0")
        return v

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: int, info: ValidationInfo) -> int:
        """Validate channel based on radio type."""
        radio = info.data.get("radio")
        if radio is None:
            return v

        if isinstance(radio, str):
            radio_value = radio
        else:
            radio_value = radio.value

        if radio_value == "na":  # 5 GHz
            if not (36 <= v <= 165):
                raise ValueError("5 GHz channel must be between 36 and 165")
        elif radio_value == "ng":  # 2.4 GHz
            if not (1 <= v <= 14):
                raise ValueError("2.4 GHz channel must be between 1 and 14")
        elif radio_value == "6e":  # 6 GHz
            if not (1 <= v <= 233):
                raise ValueError("6 GHz channel must be between 1 and 233")
        return v

    @model_validator(mode="after")
    def validate_channel_radio(self) -> "WifiStats":
        """Validate channel based on radio type."""
        if self.radio == RadioType.NA and not (36 <= self.channel <= 165):
            raise ValueError("5 GHz channel must be between 36 and 165")
        elif self.radio == RadioType.NG and not (1 <= self.channel <= 14):
            raise ValueError("2.4 GHz channel must be between 1 and 14")
        elif self.radio == RadioType._6E and not (1 <= self.channel <= 233):
            raise ValueError("6 GHz channel must be between 1 and 233")
        return self

    @field_validator("channel_width")
    @classmethod
    def validate_channel_width(cls, v: Optional[int]) -> Optional[int]:
        """Validate channel width."""
        if v is not None and v not in [20, 40, 80, 160]:
            raise ValueError("Channel width must be 20, 40, 80, or 160 MHz")
        return v

    @field_validator("ap_mac", "bssid")
    @classmethod
    def validate_mac(cls, v: str) -> str:
        """Validate MAC address format."""
        if not MAC_PATTERN.match(v):
            raise ValueError("Invalid MAC address format")
        return v.lower()


class Client(BaseModel):
    """UniFi Network client device."""

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    site_id: str = Field(description="Site identifier")
    mac: str = Field(description="Client MAC address")
    hostname: str = Field(description="Client hostname")
    ip: str = Field(description="Current IP address")
    last_ip: str = Field(description="Last known IP address")
    is_guest: bool = Field(description="Whether client is a guest")
    is_wired: bool = Field(description="Whether client is wired")
    network: str = Field(description="Network name")
    network_id: str = Field(description="Network identifier")
    uptime: int = Field(description="Client uptime in seconds", ge=0)
    last_seen: int = Field(description="Last seen timestamp")
    first_seen: int = Field(description="First seen timestamp")
    tx_bytes: int = Field(description="Total bytes transmitted", ge=0)
    rx_bytes: int = Field(description="Total bytes received", ge=0)
    tx_packets: int = Field(description="Total packets transmitted", ge=0)
    rx_packets: int = Field(description="Total packets received", ge=0)
    satisfaction: Optional[int] = Field(
        None, description="Client satisfaction score (0-100)", ge=0, le=100
    )
    wifi_stats: Optional[WifiStats] = Field(
        None, description="WiFi statistics if wireless client"
    )
    oui: Optional[str] = Field(None, description="Organizationally Unique Identifier")
    dev_cat: Optional[int] = Field(None, description="Device category")
    dev_family: Optional[int] = Field(None, description="Device family")
    dev_vendor: Optional[int] = Field(None, description="Device vendor")
    os_name: Optional[int] = Field(None, description="Operating system")
    hostname_source: Optional[str] = Field(None, description="Hostname source")
    authorized: Optional[bool] = Field(None, description="Whether client is authorized")
    qos_policy_applied: Optional[bool] = Field(
        None, description="Whether QoS policy is applied"
    )
    use_fixedip: Optional[bool] = Field(None, description="Whether using fixed IP")
    fixed_ip: Optional[str] = Field(None, description="Fixed IP address")
    ipv6_addresses: Optional[List[str]] = Field(None, description="IPv6 addresses")
    noted: Optional[bool] = Field(None, description="Whether client is noted")
    name: Optional[str] = Field(None, description="Custom name")
    bytes_r: Optional[float] = Field(None, description="Current bytes rate", ge=0)
    tx_bytes_r: Optional[float] = Field(
        None, description="Current transmit bytes rate", ge=0
    )
    rx_bytes_r: Optional[float] = Field(
        None, description="Current receive bytes rate", ge=0
    )
    satisfaction_avg: Optional[dict] = Field(
        None, description="Average satisfaction stats"
    )
    fingerprint_source: Optional[int] = Field(
        None, description="Device fingerprint source"
    )
    fingerprint_engine_version: Optional[str] = Field(
        None, description="Device fingerprint engine version"
    )
    confidence: Optional[int] = Field(
        None, description="Device identification confidence", ge=0, le=100
    )
    gw_mac: Optional[str] = Field(None, description="Gateway MAC address")
    gw_vlan: Optional[int] = Field(None, description="Gateway VLAN ID", ge=0, le=4095)
    disconnect_timestamp: Optional[int] = Field(
        None, description="Last disconnect timestamp"
    )
    assoc_time: Optional[int] = Field(None, description="Association time")
    latest_assoc_time: Optional[int] = Field(
        None, description="Latest association time"
    )
    dhcpend_time: Optional[int] = Field(None, description="DHCP lease end time")
    priority: Optional[int] = Field(None, description="Client priority")
    anomalies: Optional[int] = Field(None, description="Client anomalies")
    os_class: Optional[int] = Field(None, description="Operating system class")
    local_dns_record_enabled: Optional[bool] = Field(
        None, description="Whether local DNS record is enabled"
    )
    local_dns_record: Optional[str] = Field(None, description="Local DNS record")
    virtual_network_override_enabled: Optional[bool] = Field(
        None, description="Whether virtual network override is enabled"
    )
    virtual_network_override_id: Optional[str] = Field(
        None, description="Virtual network override ID"
    )
    eagerly_discovered: Optional[bool] = Field(
        None, description="Whether client was eagerly discovered"
    )
    wired_rate_mbps: Optional[int] = Field(
        None, description="Wired connection speed in Mbps", ge=0
    )
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
    is_guest_by_uap: Optional[bool] = Field(
        None, description="Guest status tracked by AP"
    )
    is_guest_by_usw: Optional[bool] = Field(
        None, description="Guest status tracked by switch"
    )
    is_guest_by_ugw: Optional[bool] = Field(
        None, description="Guest status tracked by gateway"
    )

    @field_validator("mac", "gw_mac", "sw_mac")
    @classmethod
    def validate_mac(cls, v: Optional[str]) -> Optional[str]:
        """Validate MAC address format."""
        if v is None:
            return None
        if not MAC_PATTERN.match(v):
            raise ValueError("Invalid MAC address format")
        return v.lower()

    @field_validator("ip", "last_ip", "fixed_ip")
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address format."""
        if v is None:
            return None
        try:
            IPv4Address(v)
            return v
        except ValueError as e:
            raise ValueError(f"Invalid IP address: {e}")

    @field_validator("ipv6_addresses")
    @classmethod
    def validate_ipv6_list(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate list of IPv6 addresses."""
        if v is None:
            return None
        validated = []
        for ip in v:
            try:
                IPv6Address(ip)
                validated.append(ip)
            except ValueError as e:
                raise ValueError(f"Invalid IPv6 address {ip}: {e}")
        return validated

    @field_validator("first_seen")
    @classmethod
    def validate_first_seen(cls, v: int, info: ValidationInfo) -> int:
        """Validate first_seen is before last_seen."""
        if "last_seen" in info.data and v > info.data["last_seen"]:
            raise ValueError("first_seen must be before last_seen")
        return v

    @field_validator("latest_assoc_time")
    @classmethod
    def validate_latest_assoc_time(
        cls, v: Optional[int], info: ValidationInfo
    ) -> Optional[int]:
        """Validate latest_assoc_time is not before assoc_time."""
        if v is not None and "assoc_time" in info.data and v < info.data["assoc_time"]:
            raise ValueError("latest_assoc_time must not be before assoc_time")
        return v


class Device(BaseModel):
    """UniFi Network device."""

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    mac: str = Field(description="Device MAC address")
    ip: Optional[str] = Field(None, description="Device IP address")
    type: DeviceType = Field(description="Device type")
    model: Optional[str] = Field(None, description="Device model")
    version: Optional[str] = Field(None, description="Firmware version")
    required_version: Optional[str] = Field(
        None, description="Required firmware version"
    )
    port_table: List[PortStats] = Field(
        default_factory=list, description="Port statistics"
    )
    uptime: Optional[int] = Field(None, description="Device uptime in seconds", ge=0)
    last_seen: Optional[int] = Field(None, description="Last seen timestamp")
    adopted: Optional[bool] = Field(None, description="Whether device is adopted")
    site_id: Optional[str] = Field(None, description="Site identifier")
    name: Optional[str] = Field(None, description="Device name")
    led_override: Optional[LedOverride] = Field(
        None, description="LED override setting"
    )
    inform_url: Optional[str] = Field(None, description="Inform URL")
    inform_ip: Optional[str] = Field(None, description="Inform IP address")
    cfgversion: Optional[str] = Field(None, description="Configuration version")
    config_network: Optional[dict] = Field(None, description="Network configuration")
    ethernet_table: Optional[List[dict]] = Field(None, description="Ethernet table")
    radio_table: Optional[List[dict]] = Field(None, description="Radio table")
    vap_table: Optional[List[dict]] = Field(None, description="VAP table")
    uplink: Optional[dict] = Field(None, description="Uplink information")
    system_stats: Optional[dict] = Field(None, description="System statistics")
    stat: Optional[dict] = Field(None, description="Device statistics")
    tx_bytes: Optional[int] = Field(None, description="Total bytes transmitted", ge=0)
    rx_bytes: Optional[int] = Field(None, description="Total bytes received", ge=0)
    bytes: Optional[int] = Field(None, description="Total bytes", ge=0)
    num_sta: Optional[int] = Field(
        None, description="Number of connected clients", ge=0
    )
    user_num_sta: Optional[int] = Field(
        None, description="Number of user clients", ge=0
    )
    guest_num_sta: Optional[int] = Field(
        None, description="Number of guest clients", ge=0
    )
    bytes_r: Optional[float] = Field(None, description="Current bytes rate", ge=0)
    tx_bytes_r: Optional[float] = Field(
        None, description="Current transmit bytes rate", ge=0
    )
    rx_bytes_r: Optional[float] = Field(
        None, description="Current receive bytes rate", ge=0
    )
    state: Optional[int] = Field(None, description="Device state")
    upgradable: Optional[bool] = Field(None, description="Whether device is upgradable")
    discovered_via: Optional[str] = Field(None, description="How device was discovered")
    loadavg_1: Optional[float] = Field(None, description="1-minute load average", ge=0)
    loadavg_5: Optional[float] = Field(None, description="5-minute load average", ge=0)
    loadavg_15: Optional[float] = Field(
        None, description="15-minute load average", ge=0
    )
    temperature: Optional[float] = Field(None, description="Device temperature")
    cpu_usage: Optional[float] = Field(
        None, description="CPU usage percentage", ge=0, le=100
    )
    mem_usage: Optional[float] = Field(
        None, description="Memory usage percentage", ge=0, le=100
    )
    uplink_table: Optional[List[dict]] = Field(None, description="Uplink table")
    kernel_version: Optional[str] = Field(None, description="Device kernel version")
    architecture: Optional[str] = Field(None, description="Device architecture")
    board_rev: Optional[int] = Field(None, description="Board revision")
    manufacturer_id: Optional[int] = Field(None, description="Manufacturer ID")
    model_in_lts: Optional[bool] = Field(None, description="Whether model is in LTS")
    model_in_eol: Optional[bool] = Field(None, description="Whether model is EOL")
    scan_radio_table: Optional[List[dict]] = Field(
        None, description="Radio scan results"
    )
    antenna_table: Optional[List[dict]] = Field(
        None, description="Antenna configuration"
    )
    radio_table_stats: Optional[List[dict]] = Field(
        None, description="Radio statistics"
    )
    port_overrides: Optional[List[dict]] = Field(
        None, description="Port override settings"
    )
    license_state: Optional[str] = Field(None, description="License state")
    hw_caps: Optional[int] = Field(None, description="Hardware capabilities")
    guest_token: Optional[str] = Field(None, description="Guest authentication token")
    x_ssh_hostkey: Optional[str] = Field(None, description="SSH host key")
    x_fingerprint: Optional[str] = Field(None, description="Device fingerprint")
    x_has_ssh_hostkey: Optional[bool] = Field(
        None, description="Whether device has SSH host key"
    )
    unsupported: Optional[bool] = Field(
        None, description="Whether device is unsupported"
    )
    unsupported_reason: Optional[int] = Field(
        None, description="Reason for being unsupported"
    )
    device_id: Optional[str] = Field(None, description="Device identifier")
    state_code: Optional[int] = Field(None, description="Device state code")
    x_aes_gcm: Optional[bool] = Field(None, description="Whether AES-GCM is supported")
    x_has_default_route_distance: Optional[bool] = Field(
        None, description="Whether default route distance is set"
    )
    x_inform_authkey: Optional[str] = Field(
        None, description="Inform authentication key"
    )
    satisfaction: Optional[int] = Field(
        None, description="Device satisfaction score", ge=0, le=100
    )

    @field_validator("mac")
    @classmethod
    def validate_mac(cls, v: str) -> str:
        """Validate MAC address format."""
        if not MAC_PATTERN.match(v):
            raise ValueError("Invalid MAC address format")
        return v.lower()

    @field_validator("ip", "inform_ip")
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address format."""
        if v is None:
            return None
        try:
            IPv4Address(v)
            return v
        except ValueError as e:
            raise ValueError(f"Invalid IP address: {e}")

    @field_validator("inform_url")
    @classmethod
    def validate_inform_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate inform URL format."""
        if v is None:
            return None
        if not v.startswith(("http://", "https://")):
            raise ValueError("Inform URL must start with http:// or https://")
        return v

    @field_validator("version", "required_version")
    @classmethod
    def validate_version(cls, v: Optional[str]) -> Optional[str]:
        """Validate version format."""
        if v is None:
            return None
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError("Invalid version format")
        return v


class VersionInfo(BaseModel):
    """UniFi Network controller version information."""

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    version: str = Field(description="Controller version")
    build: Optional[str] = Field(None, description="Build number")
    site_id: str = Field(description="Site identifier")
    update_available: Optional[bool] = Field(
        None, description="Whether update is available"
    )
    update_downloaded: Optional[bool] = Field(
        None, description="Whether update is downloaded"
    )
    update_version: Optional[str] = Field(None, description="Available update version")
    update_notes: Optional[str] = Field(None, description="Update release notes")
    internal_version: Optional[str] = Field(None, description="Internal version number")
    hardware_version: Optional[str] = Field(None, description="Hardware version")
    api_version: Optional[str] = Field(None, description="API version")
    api_version_min: Optional[str] = Field(
        None, description="Minimum supported API version"
    )
    api_version_max: Optional[str] = Field(
        None, description="Maximum supported API version"
    )

    @field_validator("version", "update_version")
    @classmethod
    def validate_version(cls, v: Optional[str]) -> Optional[str]:
        """Validate version format."""
        if v is None:
            return None
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError("Invalid version format")
        return v
