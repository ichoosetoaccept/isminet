"""Base models for the UniFi Network API."""

from typing import (
    Generic,
    List,
    Optional,
    TypeVar,
    get_args,
    get_origin,
    Dict,
    Any,
    Union,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    ValidationInfo,
)
from pydantic_core import PydanticCustomError

T = TypeVar("T")


class UnifiBaseModel(BaseModel):
    """Base model for all UniFi Network API models."""

    model_config = ConfigDict(
        extra="ignore", str_strip_whitespace=True, validate_assignment=True
    )


class ValidationMixin(UnifiBaseModel):
    """Common validation patterns."""

    @classmethod
    def validate_range(
        cls, v: Optional[int], min_val: int, max_val: int, field_name: str
    ) -> Optional[int]:
        """Validate integer is within range."""
        if v is not None and not min_val <= v <= max_val:
            raise PydanticCustomError(
                "value_out_of_range",
                "{field_name} must be between {min_val} and {max_val}",
                {"field_name": field_name, "min_val": min_val, "max_val": max_val},
            )
        return v

    @classmethod
    def validate_non_negative(cls, v: Optional[int]) -> Optional[int]:
        """Validate integer is non-negative."""
        if v is not None and v < 0:
            raise PydanticCustomError(
                "value_negative",
                "Value must be non-negative",
                {},
            )
        return v

    @classmethod
    def validate_percentage(cls, v: Optional[float]) -> Optional[float]:
        """Validate value is a valid percentage (0-100)."""
        if v is not None and not 0 <= v <= 100:
            raise PydanticCustomError(
                "value_out_of_range",
                "Percentage must be between 0 and 100",
                {},
            )
        return v

    @classmethod
    def validate_negative(cls, v: Optional[int]) -> Optional[int]:
        """Validate integer is negative."""
        if v is not None and v >= 0:
            raise PydanticCustomError(
                "value_not_negative",
                "Value must be negative",
                {},
            )
        return v


class Meta(BaseModel):
    """Meta information for UniFi Network API responses."""

    rc: str = "ok"
    msg: Optional[str] = None


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for UniFi Network API."""

    model_config = ConfigDict(extra="allow")

    meta: Dict[str, Any]
    data: Union[T, List[T]]

    def validate_data(self) -> None:
        """
        Validate the data field against the specified generic type argument.
        
        This method ensures that the `data` attribute conforms to the expected type defined during BaseResponse instantiation. It handles both single instances and lists of instances.
        
        Parameters:
            None
        
        Raises:
            ValidationError: If the data does not match the expected type or cannot be converted to it.
        
        Notes:
            - Skips validation if no generic type is specified
            - Supports validation of both single items and lists of items
            - Uses model type constructor to validate and potentially convert input data
        """
        if not hasattr(self, "__orig_bases__"):
            return

        model_type = get_args(self.__orig_bases__[0])[0]
        if not self.data:
            return

        if isinstance(self.data, list):
            for item in self.data:
                if not isinstance(item, model_type):
                    model_type(**item)
        elif not isinstance(self.data, model_type):
            model_type(**self.data)

    @classmethod
    def get_data_type(cls) -> type:
        """Get the type of the data field."""
        for base in cls.__orig_bases__:  # type: ignore
            if get_origin(base) is BaseResponse:
                args = get_args(base)
                if args:
                    return args[0]
        raise TypeError("Could not determine data type for BaseResponse")


class StatisticsMixin(UnifiBaseModel):
    """Common statistics fields for UniFi models."""

    tx_bytes: Optional[int] = Field(None, description="Total bytes transmitted", ge=0)
    rx_bytes: Optional[int] = Field(None, description="Total bytes received", ge=0)
    tx_packets: Optional[int] = Field(
        None, description="Total packets transmitted", ge=0
    )
    rx_packets: Optional[int] = Field(None, description="Total packets received", ge=0)
    bytes_r: Optional[float] = Field(None, description="Current bytes rate", ge=0)
    tx_bytes_r: Optional[float] = Field(
        None, description="Current transmit bytes rate", ge=0
    )
    rx_bytes_r: Optional[float] = Field(
        None, description="Current receive bytes rate", ge=0
    )
    satisfaction: Optional[int] = Field(
        None, description="Satisfaction score (0-100)", ge=0, le=100
    )


class DeviceBaseMixin(UnifiBaseModel):
    """Common device fields for UniFi models."""

    mac: str = Field(description="MAC address")
    ip: Optional[str] = Field(None, description="IP address")
    uptime: Optional[int] = Field(None, description="Device uptime in seconds", ge=0)
    last_seen: Optional[int] = Field(None, description="Last seen timestamp")
    site_id: Optional[str] = Field(None, description="Site identifier")
    name: Optional[str] = Field(None, description="Device name")


class NetworkMixin(UnifiBaseModel):
    """Common network-related fields."""

    network_name: Optional[str] = Field(None, description="Network name")
    network_id: Optional[str] = Field(None, description="Network identifier")
    netmask: Optional[str] = Field(None, description="Network mask")
    is_guest: Optional[bool] = Field(None, description="Whether network is for guests")
    vlan: Optional[int] = Field(None, description="VLAN ID", ge=0, le=4095)


class SystemStatsMixin(UnifiBaseModel):
    """Common system statistics fields."""

    cpu_usage: Optional[float] = Field(
        None, description="CPU usage percentage", ge=0, le=100
    )
    mem_usage: Optional[float] = Field(
        None, description="Memory usage percentage", ge=0, le=100
    )
    temperature: Optional[float] = Field(None, description="Temperature")
    loadavg_1: Optional[float] = Field(None, description="1-minute load average", ge=0)
    loadavg_5: Optional[float] = Field(None, description="5-minute load average", ge=0)
    loadavg_15: Optional[float] = Field(
        None, description="15-minute load average", ge=0
    )


class WifiMixin(UnifiBaseModel):
    """Common WiFi-related fields."""

    channel: Optional[int] = Field(None, description="WiFi channel")
    tx_rate: Optional[int] = Field(None, description="Transmit rate in Kbps", ge=0)
    rx_rate: Optional[int] = Field(None, description="Receive rate in Kbps", ge=0)
    tx_power: Optional[int] = Field(None, description="Transmit power")
    tx_retries: Optional[int] = Field(
        None, description="Number of transmit retries", ge=0
    )
    channel_width: Optional[int] = Field(None, description="Channel width in MHz")
    radio_name: Optional[str] = Field(None, description="Radio name")
    authorized: Optional[bool] = Field(None, description="Whether client is authorized")
    qos_policy_applied: Optional[bool] = Field(
        None, description="Whether QoS policy is applied"
    )


class TimestampMixin(UnifiBaseModel):
    """Common timestamp-related fields."""

    first_seen: Optional[int] = Field(None, description="First seen timestamp")
    last_seen: Optional[int] = Field(None, description="Last seen timestamp")
    disconnect_timestamp: Optional[int] = Field(
        None, description="Last disconnect timestamp"
    )
    assoc_time: Optional[int] = Field(None, description="Association time")
    latest_assoc_time: Optional[int] = Field(
        None, description="Latest association time"
    )

    @field_validator("first_seen")
    @classmethod
    def validate_first_seen(
        cls, v: Optional[int], info: ValidationInfo
    ) -> Optional[int]:
        """Validate first_seen is before last_seen."""
        if (
            v is not None
            and "last_seen" in info.data
            and info.data["last_seen"] is not None
        ):
            if v > info.data["last_seen"]:
                raise ValueError("first_seen must be before last_seen")
        return v

    @field_validator("last_seen")
    @classmethod
    def validate_last_seen(
        cls, v: Optional[int], info: ValidationInfo
    ) -> Optional[int]:
        """Validate last_seen is after first_seen."""
        if (
            v is not None
            and "first_seen" in info.data
            and info.data["first_seen"] is not None
        ):
            if v < info.data["first_seen"]:
                raise ValueError("last_seen must be after first_seen")
        return v

    @field_validator("latest_assoc_time")
    @classmethod
    def validate_latest_assoc_time(
        cls, v: Optional[int], info: ValidationInfo
    ) -> Optional[int]:
        """Validate latest_assoc_time is after assoc_time."""
        if (
            v is not None
            and "assoc_time" in info.data
            and info.data["assoc_time"] is not None
        ):
            if v < info.data["assoc_time"]:
                raise ValueError("latest_assoc_time must be after assoc_time")
        return v


class PoEMixin(UnifiBaseModel):
    """Common PoE-related fields."""

    port_poe: Optional[bool] = Field(None, description="Whether port supports PoE")
    poe_power: Optional[str] = Field(None, description="PoE power consumption")
    poe_mode: Optional[str] = Field(None, description="PoE mode")
    poe_enable: Optional[bool] = Field(None, description="PoE enabled")
    poe_caps: Optional[int] = Field(None, description="PoE capabilities")


class SFPMixin(UnifiBaseModel):
    """Common SFP module-related fields."""

    sfp_vendor: Optional[str] = Field(None, description="SFP module vendor")
    sfp_part: Optional[str] = Field(None, description="SFP module part number")
    sfp_serial: Optional[str] = Field(None, description="SFP module serial number")
    sfp_temperature: Optional[float] = Field(None, description="SFP module temperature")
    sfp_voltage: Optional[float] = Field(None, description="SFP module voltage", ge=0)
    sfp_rxpower: Optional[float] = Field(
        None, description="SFP module RX power in dBm", lt=0
    )
    sfp_txpower: Optional[float] = Field(
        None, description="SFP module TX power in dBm", lt=0
    )


class StormControlMixin(UnifiBaseModel):
    """Common storm control fields."""

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


class PortConfigMixin(UnifiBaseModel):
    """Common port configuration fields."""

    autoneg: Optional[bool] = Field(None, description="Auto-negotiation enabled")
    flowctrl_rx: Optional[bool] = Field(None, description="RX flow control enabled")
    flowctrl_tx: Optional[bool] = Field(None, description="TX flow control enabled")
    full_duplex: Optional[bool] = Field(None, description="Full duplex enabled")
    speed_caps: Optional[int] = Field(None, description="Speed capabilities")
    op_mode: Optional[str] = Field(None, description="Operation mode")
    port_security_enabled: Optional[bool] = Field(
        None, description="Port security enabled"
    )
    port_security_mac_address: Optional[List[str]] = Field(
        None, description="Allowed MAC addresses"
    )
    isolation: Optional[bool] = Field(None, description="Port isolation enabled")


class DeviceIdentificationMixin(UnifiBaseModel):
    """Common device identification fields."""

    model: Optional[str] = Field(None, description="Device model")
    oui: Optional[str] = Field(None, description="Organizationally Unique Identifier")
    dev_cat: Optional[int] = Field(None, description="Device category")
    dev_family: Optional[int] = Field(None, description="Device family")
    dev_vendor: Optional[int] = Field(None, description="Device vendor")
    os_name: Optional[int] = Field(None, description="Operating system")
    os_class: Optional[int] = Field(None, description="Operating system class")
    fingerprint_source: Optional[int] = Field(
        None, description="Device fingerprint source"
    )
    fingerprint_engine_version: Optional[str] = Field(
        None, description="Device fingerprint engine version"
    )
    confidence: Optional[int] = Field(
        None, description="Device identification confidence", ge=0, le=100
    )
    manufacturer_id: Optional[int] = Field(None, description="Manufacturer ID")
    board_rev: Optional[int] = Field(None, description="Board revision")
    architecture: Optional[str] = Field(None, description="Device architecture")
    kernel_version: Optional[str] = Field(None, description="Device kernel version")


class VersionMixin(UnifiBaseModel):
    """Common version-related fields."""

    version: Optional[str] = Field(None, description="Version string")
    required_version: Optional[str] = Field(None, description="Required version string")
    cfgversion: Optional[str] = Field(None, description="Configuration version")
    model_in_lts: Optional[bool] = Field(None, description="Whether model is in LTS")
    model_in_eol: Optional[bool] = Field(None, description="Whether model is EOL")


class Site(BaseModel):
    """Site model for UniFi Network API."""

    id: str = Field(alias="_id", min_length=1)
    name: str = Field(min_length=1)
    desc: Optional[str] = None
    device_count: int = Field(ge=0)
    anonymous_id: Optional[str] = None
    attr_no_delete: Optional[bool] = None
    attr_hidden_id: Optional[str] = None
    role: Optional[str] = None
    role_hotspot: Optional[bool] = None
