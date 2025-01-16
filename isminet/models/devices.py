"""Device models for the UniFi Network API."""

from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, model_validator, ValidationError
from pydantic_core import PydanticCustomError

from .base import (
    UnifiBaseModel,
    StatisticsMixin,
    DeviceBaseMixin,
    NetworkMixin,
    WifiMixin,
    TimestampMixin,
    PoEMixin,
    SFPMixin,
    StormControlMixin,
    PortConfigMixin,
    ValidationMixin,
    DeviceIdentificationMixin,
    VersionMixin,
)
from .validators import (
    validate_mac,
    validate_mac_list,
    validate_ip,
    validate_version,
)
from .device_components import (
    DeviceNetwork,
    DeviceWireless,
    DeviceSecurity,
    DeviceSystem,
)
from .client_components import (
    ClientNetwork,
    ClientTracking,
    ClientGuest,
    ClientDNS,
)
from .enums import (
    RadioType,
    RadioProto,
    DeviceType,
)


class PortStats(
    StatisticsMixin,
    NetworkMixin,
    PoEMixin,
    SFPMixin,
    StormControlMixin,
    PortConfigMixin,
    ValidationMixin,
    UnifiBaseModel,
):
    """Port statistics and configuration."""

    port_idx: int = Field(description="Port index", ge=1)
    name: str = Field(description="Port name")
    media: str = Field(description="Port media type (GE, SFP+)")
    speed: int = Field(description="Current port speed", ge=0)
    up: bool = Field(description="Whether port is up")
    is_uplink: bool = Field(description="Whether port is an uplink")
    mac: str = Field(description="MAC address")
    rx_errors: int = Field(description="Total receive errors", ge=0)
    tx_errors: int = Field(description="Total transmit errors", ge=0)
    type: str = Field(description="Port type")
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

    _validate_mac = field_validator("mac")(validate_mac)
    _validate_ip = field_validator("ip")(validate_ip)
    _validate_netmask = field_validator("netmask")(validate_ip)
    _validate_mac_list = field_validator("port_security_mac_address")(validate_mac_list)


class WifiStats(WifiMixin, UnifiBaseModel):
    """WiFi-specific statistics for wireless clients."""

    ap_mac: str = Field(description="MAC address")
    radio: RadioType = Field(description="Radio type (ng, na, 6e)")
    radio_proto: RadioProto = Field(description="Radio protocol (ng, ac, ax, be)")
    essid: str = Field(description="Network SSID")
    bssid: str = Field(description="MAC address")
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
    tx_retry_burst_count: Optional[int] = Field(
        None, description="Transmit retry burst count", ge=0
    )
    ccq: Optional[int] = Field(
        None, description="Client connection quality", ge=0, le=1000
    )

    @model_validator(mode="after")
    def validate_channel_radio(self) -> "WifiStats":
        """Validate channel and radio type combination."""
        if self.channel is not None:
            if self.radio == RadioType.NG:
                if not 1 <= self.channel <= 14:
                    raise ValueError("2.4 GHz channels must be between 1 and 14")
            elif self.radio == RadioType.NA:
                if not 36 <= self.channel <= 165:
                    raise ValueError("5 GHz channels must be between 36 and 165")
            elif self.radio == RadioType._6E:
                if not 1 <= self.channel <= 233:
                    raise ValueError("6 GHz channels must be between 1 and 233")
        return self

    @field_validator("channel_width")
    @classmethod
    def validate_channel_width(cls, v: Optional[int]) -> Optional[int]:
        """Validate channel width is a standard value."""
        if v is not None and v not in [20, 40, 80, 160, 320]:
            raise ValueError("Channel width must be 20, 40, 80, 160, or 320")
        return v

    _validate_mac = field_validator("ap_mac", "bssid")(validate_mac)


class Client(
    DeviceBaseMixin,
    StatisticsMixin,
    NetworkMixin,
    TimestampMixin,
    DeviceIdentificationMixin,
    ValidationMixin,
    UnifiBaseModel,
):
    """UniFi Network client device."""

    first_seen: int = Field(description="First seen timestamp")
    wifi_stats: Optional[WifiStats] = Field(
        None, description="WiFi statistics if wireless client"
    )
    priority: Optional[int] = Field(None, description="Client priority")
    anomalies: Optional[int] = Field(None, description="Client anomalies")
    virtual_network_override_enabled: Optional[bool] = Field(
        None, description="Whether virtual network override is enabled"
    )
    virtual_network_override_id: Optional[str] = Field(
        None, description="Virtual network override ID"
    )
    eagerly_discovered: Optional[bool] = Field(
        None, description="Whether client was eagerly discovered"
    )
    satisfaction_avg: Optional[Dict[str, Any]] = Field(
        None, description="Average satisfaction stats"
    )
    ip: Optional[str] = Field(None, description="IP address")

    # Component models for better SRP adherence
    network: Optional[ClientNetwork] = Field(None, description="Network configuration")
    tracking: Optional[ClientTracking] = Field(None, description="Tracking information")
    guest: Optional[ClientGuest] = Field(None, description="Guest configuration")
    dns: Optional[ClientDNS] = Field(None, description="DNS configuration")

    _validate_mac = field_validator("mac")(validate_mac)
    _validate_ip = field_validator("ip")(validate_ip)

    @model_validator(mode="before")
    @classmethod
    def validate_component_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fields for component models in a client device.
        
        This method performs validation of required fields and component-specific data for a client device. It ensures that essential fields are present and that component-specific data can be successfully instantiated.
        
        Parameters:
            cls (type): The class on which the validation is being performed.
            data (Dict[str, Any]): A dictionary containing client device data to be validated.
        
        Returns:
            Dict[str, Any]: The original input data if validation is successful.
        
        Raises:
            PydanticCustomError: If required fields are missing or component data is invalid.
                - Error code "missing_required_fields": Raised when essential fields like 'mac' or 'first_seen' are absent.
                - Error code "invalid_component_data": Raised when component-specific data fails validation.
        
        Notes:
            - Checks for mandatory fields: 'mac' and 'first_seen'
            - Extracts and validates data for network, tracking, guest, and DNS components
            - Uses Pydantic models (ClientNetwork, ClientTracking, ClientGuest, ClientDNS) for component validation
        """
        # Check required fields
        required_fields = {"mac", "first_seen"}
        missing_fields = required_fields - data.keys()
        if missing_fields:
            raise PydanticCustomError(
                "missing_required_fields",
                "Missing required fields: {missing_fields}",
                {"missing_fields": list(missing_fields)},
            )

        # Extract component data
        network_data = {
            k: v for k, v in data.items() if k in ClientNetwork.__annotations__
        }
        tracking_data = {
            k: v for k, v in data.items() if k in ClientTracking.__annotations__
        }
        guest_data = {k: v for k, v in data.items() if k in ClientGuest.__annotations__}
        dns_data = {k: v for k, v in data.items() if k in ClientDNS.__annotations__}

        # Validate component data
        try:
            if network_data:
                ClientNetwork(**network_data)
            if tracking_data:
                ClientTracking(**tracking_data)
            if guest_data:
                ClientGuest(**guest_data)
            if dns_data:
                ClientDNS(**dns_data)
        except ValidationError:
            raise PydanticCustomError(
                "invalid_component_data",
                "Invalid component data",
                {},
            )

        return data

    def __init__(self, **data: Any) -> None:
        """
        Initialize a Client instance with component models.
        
        This method extracts and initializes component-specific data for network, tracking, 
        guest, and DNS configurations. It separates component-specific fields from the main 
        data dictionary and creates corresponding Pydantic models for each component.
        
        Parameters:
            **data (Any): Keyword arguments containing client data, including component-specific fields.
        
        Notes:
            - Extracts fields specific to each component model (ClientNetwork, ClientTracking, 
              ClientGuest, ClientDNS) based on their type annotations.
            - Removes component-specific fields from the main data dictionary.
            - Creates component models only if corresponding data is present.
            - Uses the parent class's __init__ method to finalize initialization.
        
        Example:
            client = Client(
                mac='00:11:22:33:44:55', 
                network_vlan=100, 
                tracking_first_seen=datetime.now()
            )
        """
        # Extract component data
        network_data = {
            k: v for k, v in data.items() if k in ClientNetwork.__annotations__
        }
        tracking_data = {
            k: v for k, v in data.items() if k in ClientTracking.__annotations__
        }
        guest_data = {k: v for k, v in data.items() if k in ClientGuest.__annotations__}
        dns_data = {k: v for k, v in data.items() if k in ClientDNS.__annotations__}

        # Remove component data from main data
        for k in (
            network_data.keys()
            | tracking_data.keys()
            | guest_data.keys()
            | dns_data.keys()
        ):
            data.pop(k, None)

        # Initialize component models
        if network_data:
            data["network"] = ClientNetwork(**network_data)
        if tracking_data:
            data["tracking"] = ClientTracking(**tracking_data)
        if guest_data:
            data["guest"] = ClientGuest(**guest_data)
        if dns_data:
            data["dns"] = ClientDNS(**dns_data)

        super().__init__(**data)

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to component models."""
        # Try network component
        if name in ClientNetwork.__annotations__:
            if self.network is not None:
                return getattr(self.network, name)
            return None

        # Try tracking component
        if name in ClientTracking.__annotations__:
            if self.tracking is not None:
                return getattr(self.tracking, name)
            return None

        # Try guest component
        if name in ClientGuest.__annotations__:
            if self.guest is not None:
                return getattr(self.guest, name)
            return None

        # Try dns component
        if name in ClientDNS.__annotations__:
            if self.dns is not None:
                return getattr(self.dns, name)
            return None

        raise AttributeError(
            f"{self.__class__.__name__!r} object has no attribute {name!r}"
        )


class Device(
    DeviceBaseMixin,
    StatisticsMixin,
    DeviceIdentificationMixin,
    VersionMixin,
    ValidationMixin,
    UnifiBaseModel,
):
    """UniFi Network device."""

    type: DeviceType = Field(description="Device type")
    port_table: List[PortStats] = Field(
        default_factory=list, description="Port statistics"
    )
    bytes: Optional[int] = Field(None, description="Total bytes", ge=0)
    device_id: Optional[str] = Field(None, description="Device identifier")

    # Component models for better SRP adherence
    network: Optional[DeviceNetwork] = Field(None, description="Network configuration")
    wireless: Optional[DeviceWireless] = Field(
        None, description="Wireless configuration"
    )
    security: Optional[DeviceSecurity] = Field(
        None, description="Security configuration"
    )
    system: Optional[DeviceSystem] = Field(None, description="System information")

    _validate_mac = field_validator("mac")(validate_mac)
    _validate_version = field_validator("version", "required_version")(validate_version)

    @model_validator(mode="before")
    @classmethod
    def validate_component_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fields for device component models, ensuring required fields are present and component data is valid.
        
        This method performs two primary validation tasks:
        1. Checks that essential device fields (mac, type, version) are present
        2. Extracts and validates data for device component models (network, wireless, security, system)
        
        Parameters:
            cls (type): The class on which the validation is being performed
            data (Dict[str, Any]): A dictionary of device data to validate
        
        Returns:
            Dict[str, Any]: The original input data if validation succeeds
        
        Raises:
            PydanticCustomError: If required fields are missing or component data is invalid
                - Error code "missing_required_fields": When essential fields are not present
                - Error code "invalid_component_data": When component model validation fails
        """
        # Check required fields
        required_fields = {"mac", "type", "version"}
        missing_fields = required_fields - data.keys()
        if missing_fields:
            raise PydanticCustomError(
                "missing_required_fields",
                "Missing required fields: {missing_fields}",
                {"missing_fields": list(missing_fields)},
            )

        # Extract component data
        network_data = {
            k: v for k, v in data.items() if k in DeviceNetwork.__annotations__
        }
        wireless_data = {
            k: v for k, v in data.items() if k in DeviceWireless.__annotations__
        }
        security_data = {
            k: v for k, v in data.items() if k in DeviceSecurity.__annotations__
        }
        system_data = {
            k: v for k, v in data.items() if k in DeviceSystem.__annotations__
        }

        # Validate component data
        try:
            if network_data:
                DeviceNetwork(**network_data)
            if wireless_data:
                DeviceWireless(**wireless_data)
            if security_data:
                DeviceSecurity(**security_data)
            if system_data:
                DeviceSystem(**system_data)
        except ValidationError:
            raise PydanticCustomError(
                "invalid_component_data",
                "Invalid component data",
                {},
            )

        return data

    def __init__(self, **data: Any) -> None:
        """
        Initialize a Device instance with component models.
        
        This method extracts and separates component-specific data for DeviceNetwork, 
        DeviceWireless, DeviceSecurity, and DeviceSystem from the input data. It creates 
        separate component models for each valid component type and removes their 
        corresponding keys from the main data dictionary.
        
        Parameters:
            **data (Any): Keyword arguments containing device configuration data. 
                Data will be split into component-specific models and remaining 
                general device attributes.
        
        Notes:
            - Component models are only created if corresponding data is provided
            - Component models are added to the main data dictionary under keys 
              'network', 'wireless', 'security', and 'system'
            - Remaining data is passed to the parent class constructor
        """
        # Extract component data
        network_data = {
            k: v for k, v in data.items() if k in DeviceNetwork.__annotations__
        }
        wireless_data = {
            k: v for k, v in data.items() if k in DeviceWireless.__annotations__
        }
        security_data = {
            k: v for k, v in data.items() if k in DeviceSecurity.__annotations__
        }
        system_data = {
            k: v for k, v in data.items() if k in DeviceSystem.__annotations__
        }

        # Remove component data from main data
        for k in (
            network_data.keys()
            | wireless_data.keys()
            | security_data.keys()
            | system_data.keys()
        ):
            data.pop(k, None)

        # Initialize component models
        if network_data:
            data["network"] = DeviceNetwork(**network_data)
        if wireless_data:
            data["wireless"] = DeviceWireless(**wireless_data)
        if security_data:
            data["security"] = DeviceSecurity(**security_data)
        if system_data:
            data["system"] = DeviceSystem(**system_data)

        super().__init__(**data)

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to component models."""
        # Try network component
        if name in DeviceNetwork.__annotations__:
            if self.network is not None:
                return getattr(self.network, name)
            return None

        # Try wireless component
        if name in DeviceWireless.__annotations__:
            if self.wireless is not None:
                return getattr(self.wireless, name)
            return None

        # Try security component
        if name in DeviceSecurity.__annotations__:
            if self.security is not None:
                return getattr(self.security, name)
            return None

        # Try system component
        if name in DeviceSystem.__annotations__:
            if self.system is not None:
                return getattr(self.system, name)
            return None

        raise AttributeError(
            f"{self.__class__.__name__!r} object has no attribute {name!r}"
        )
