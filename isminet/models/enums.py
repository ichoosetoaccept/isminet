"""Enums for UniFi Network models."""

from enum import Enum


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
