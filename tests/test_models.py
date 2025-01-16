"""Tests for UniFi Network API models."""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from isminet.models.base import BaseResponse
from isminet.models import Site
from isminet.models.devices import (
    Device,
    Client,
    RadioType,
    RadioProto,
    DeviceType,
    PortStats,
    WifiStats,
)
from isminet.models.version import VersionInfo
from isminet.models.base import (
    ValidationMixin,
    NetworkMixin,
    SystemStatsMixin,
    TimestampMixin,
    PoEMixin,
    SFPMixin,
    StormControlMixin,
    UnifiBaseModel,
)

# Load test data from API response examples
DOCS_DIR = Path(__file__).parent.parent / "docs" / "api_responses"
with open(DOCS_DIR / "sites_response.json") as f:
    SITES_RESPONSE = json.load(f)

# Sample valid data for testing
VALID_MAC = "00:11:22:33:44:55"
VALID_IPV4 = "192.168.1.100"
VALID_IPV6 = "2001:db8::1"
VALID_NETMASK = "255.255.255.0"


def test_site_model_valid():
    """Test that the Site model can parse a valid site response."""
    site_data = SITES_RESPONSE["data"][0]
    site = Site(**site_data)

    # Test that all fields are correctly parsed
    assert site.name == "default"
    assert site.desc == "Default"
    assert site.id == "66450709e650bd21e774c55c"
    assert site.device_count == 3
    assert site.anonymous_id == "22263757-6495-476b-b62c-8e7b46cc2c73"
    assert site.external_id == "88f7af54-98f8-306a-a1c7-c9349722b1f6"
    assert site.attr_no_delete is True
    assert site.attr_hidden_id == "default"
    assert site.role == "admin"
    assert site.role_hotspot is False


def test_site_model_minimal():
    """Test that the Site model works with minimal data."""
    site_data = {
        "name": "test-site",
        "desc": "Test Site",
        "_id": "123456789",
        "device_count": 0,
    }
    site = Site(**site_data)

    assert site.name == "test-site"
    assert site.desc == "Test Site"
    assert site.id == "123456789"
    assert site.device_count == 0
    assert site.anonymous_id is None
    assert site.external_id is None
    assert site.attr_no_delete is None
    assert site.attr_hidden_id is None
    assert site.role is None
    assert site.role_hotspot is None


def test_site_model_invalid():
    """Test that the Site model properly validates input data."""
    invalid_sites = [
        # Missing required field
        {"name": "test-site", "desc": "Test Site"},
        # Invalid device count
        {
            "name": "test-site",
            "desc": "Test Site",
            "_id": "123456789",
            "device_count": -1,
        },
        # Empty string for required field
        {"name": "", "desc": "Test Site", "_id": "123456789", "device_count": 0},
    ]

    for data in invalid_sites:
        with pytest.raises(ValidationError):
            Site(**data)


def test_base_response_with_sites():
    """Test that the BaseResponse model can parse a response with sites."""
    response = BaseResponse[Site](**SITES_RESPONSE)

    assert response.meta.rc == "ok"
    assert len(response.data) == 1
    assert isinstance(response.data[0], Site)
    assert response.data[0].name == "default"


def test_port_stats_validation():
    """Test PortStats model validation."""
    valid_data = {
        "port_idx": 1,
        "name": "Port 1",
        "media": "GE",
        "port_poe": True,
        "speed": 1000,
        "up": True,
        "is_uplink": False,
        "mac": VALID_MAC,
        "rx_bytes": 1000000,
        "tx_bytes": 2000000,
        "rx_packets": 1000,
        "tx_packets": 2000,
        "rx_errors": 0,
        "tx_errors": 0,
        "type": "copper",
    }
    port = PortStats(**valid_data)
    assert port.mac == VALID_MAC.lower()
    assert port.speed == 1000

    # Test invalid port index
    with pytest.raises(ValidationError):
        PortStats(**{**valid_data, "port_idx": 0})

    # Test invalid MAC address
    with pytest.raises(ValidationError):
        PortStats(**{**valid_data, "mac": "invalid"})

    # Test invalid IP address
    with pytest.raises(ValidationError):
        PortStats(**{**valid_data, "ip": "invalid"})


def test_wifi_stats_validation():
    """Test WifiStats model validation."""
    valid_data = {
        "ap_mac": VALID_MAC,
        "channel": 36,
        "radio": RadioType.NA,
        "radio_proto": RadioProto.AX,
        "essid": "Test Network",
        "bssid": VALID_MAC,
        "signal": -65,
        "noise": -95,
        "tx_rate": 866000,
        "rx_rate": 866000,
        "tx_power": 20,
        "tx_retries": 10,
    }
    wifi = WifiStats(**valid_data)
    assert wifi.radio == RadioType.NA
    assert wifi.radio_proto == RadioProto.AX

    # Test invalid channel for radio type
    with pytest.raises(ValidationError):
        WifiStats(**{**valid_data, "channel": 1})  # 2.4 GHz channel for 5 GHz radio

    # Test invalid signal value
    with pytest.raises(ValidationError):
        WifiStats(**{**valid_data, "signal": 10})  # Positive dBm value

    # Test invalid channel width
    with pytest.raises(ValidationError):
        WifiStats(**{**valid_data, "channel_width": 30})  # Invalid channel width


def test_client_validation():
    """Test Client model validation."""
    valid_data = {
        "site_id": "default",
        "mac": VALID_MAC,
        "hostname": "test-device",
        "ip": VALID_IPV4,
        "last_ip": VALID_IPV4,
        "is_guest": False,
        "is_wired": True,
        "network": "Default",
        "network_id": "default",
        "uptime": 3600,
        "last_seen": 1600000000,
        "first_seen": 1500000000,
        "tx_bytes": 1000000,
        "rx_bytes": 2000000,
        "tx_packets": 1000,
        "rx_packets": 2000,
        "gw_mac": VALID_MAC,
        "sw_mac": VALID_MAC,
    }
    client = Client(**valid_data)
    assert client.mac == VALID_MAC.lower()
    assert client.ip == VALID_IPV4

    # Test invalid MAC address
    with pytest.raises(ValidationError):
        Client(**{**valid_data, "mac": "invalid"})

    # Test invalid IP address
    with pytest.raises(ValidationError):
        Client(**{**valid_data, "ip": "invalid"})

    # Test invalid first_seen/last_seen combination
    with pytest.raises(ValidationError):
        Client(**{**valid_data, "first_seen": 1700000000})  # After last_seen


def test_device_validation():
    """Test Device model validation."""
    valid_data = {
        "mac": VALID_MAC,
        "type": DeviceType.UAP,
        "model": "U6-Pro",
        "version": "7.0.0",
        "site_id": "default",
        "port_table": [],
    }
    device = Device(**valid_data)
    assert device.mac == VALID_MAC.lower()
    assert device.type == DeviceType.UAP

    # Test invalid MAC address
    with pytest.raises(ValidationError):
        Device(**{**valid_data, "mac": "invalid"})

    # Test invalid version format
    with pytest.raises(ValidationError):
        Device(**{**valid_data, "version": "invalid"})

    # Test invalid device type
    with pytest.raises(ValidationError):
        Device(**{**valid_data, "type": "invalid"})


def test_version_info_validation():
    """Test VersionInfo model validation."""
    valid_data = {
        "version": "7.0.0",
        "build": "1234",
        "site_id": "default",
    }
    version = VersionInfo(**valid_data)
    assert version.version == "7.0.0"

    # Test invalid version format
    with pytest.raises(ValidationError, match="Invalid version format"):
        invalid_data = valid_data.copy()
        invalid_data["version"] = "invalid.version"
        VersionInfo(**invalid_data)


def test_validation_mixin():
    """Test ValidationMixin functionality."""

    class TestModel(ValidationMixin, UnifiBaseModel):
        """Test model using ValidationMixin."""

    # Test range validation
    assert TestModel.validate_range(50, 0, 100, "test") == 50
    with pytest.raises(ValueError, match="test must be between 0 and 100"):
        TestModel.validate_range(101, 0, 100, "test")
    with pytest.raises(ValueError, match="test must be between 0 and 100"):
        TestModel.validate_range(-1, 0, 100, "test")

    # Test non-negative validation
    assert TestModel.validate_non_negative(0) == 0
    assert TestModel.validate_non_negative(1) == 1
    with pytest.raises(ValueError, match="Value must be non-negative"):
        TestModel.validate_non_negative(-1)

    # Test percentage validation
    assert TestModel.validate_percentage(0.0) == 0.0
    assert TestModel.validate_percentage(100.0) == 100.0
    with pytest.raises(ValueError, match="Percentage must be between 0 and 100"):
        TestModel.validate_percentage(101.0)

    # Test negative validation
    assert TestModel.validate_negative(-1) == -1
    with pytest.raises(ValueError, match="Value must be negative"):
        TestModel.validate_negative(0)


def test_network_mixin():
    """Test NetworkMixin validation."""

    class TestModel(NetworkMixin, UnifiBaseModel):
        """Test model using NetworkMixin."""

    # Test valid VLAN range
    model = TestModel(vlan=1)
    assert model.vlan == 1

    # Test VLAN boundaries
    model = TestModel(vlan=0)
    assert model.vlan == 0
    model = TestModel(vlan=4095)
    assert model.vlan == 4095

    # Test invalid VLAN
    with pytest.raises(ValidationError):
        TestModel(vlan=4096)
    with pytest.raises(ValidationError):
        TestModel(vlan=-1)


def test_system_stats_mixin():
    """Test SystemStatsMixin validation."""

    class TestModel(SystemStatsMixin, UnifiBaseModel):
        """Test model using SystemStatsMixin."""

    # Test valid percentages
    model = TestModel(cpu_usage=50.0, mem_usage=75.5)
    assert model.cpu_usage == 50.0
    assert model.mem_usage == 75.5

    # Test percentage boundaries
    model = TestModel(cpu_usage=0, mem_usage=100)
    assert model.cpu_usage == 0
    assert model.mem_usage == 100

    # Test invalid percentages
    with pytest.raises(ValidationError):
        TestModel(cpu_usage=101)
    with pytest.raises(ValidationError):
        TestModel(mem_usage=-1)

    # Test load averages
    model = TestModel(loadavg_1=0.5, loadavg_5=1.0, loadavg_15=1.5)
    assert model.loadavg_1 == 0.5
    assert model.loadavg_5 == 1.0
    assert model.loadavg_15 == 1.5

    # Test invalid load averages
    with pytest.raises(ValidationError):
        TestModel(loadavg_1=-1)


def test_timestamp_mixin():
    """Test TimestampMixin validation."""

    class TestModel(TimestampMixin, UnifiBaseModel):
        """Test model using TimestampMixin."""

    # Test valid timestamps
    model = TestModel(
        first_seen=1000,
        last_seen=2000,
        assoc_time=1500,
        latest_assoc_time=1600,
    )
    assert model.first_seen == 1000
    assert model.last_seen == 2000

    # Test invalid timestamp order
    with pytest.raises(ValidationError):
        TestModel(first_seen=2000, last_seen=1000)

    # Test invalid association time order
    with pytest.raises(ValidationError):
        TestModel(assoc_time=2000, latest_assoc_time=1000)

    # Test partial timestamps
    model = TestModel(first_seen=1000)  # No last_seen
    assert model.first_seen == 1000

    model = TestModel(last_seen=2000)  # No first_seen
    assert model.last_seen == 2000


def test_poe_mixin():
    """Test PoEMixin validation."""

    class TestModel(PoEMixin, UnifiBaseModel):
        """Test model using PoEMixin."""

    # Test valid PoE configuration
    model = TestModel(
        port_poe=True,
        poe_enable=True,
        poe_mode="auto",
        poe_power="15.4W",
        poe_caps=1,
    )
    assert model.port_poe is True
    assert model.poe_enable is True

    # Test optional fields
    model = TestModel()
    assert model.port_poe is None
    assert model.poe_enable is None


def test_sfp_mixin():
    """Test SFPMixin validation."""

    class TestModel(SFPMixin, UnifiBaseModel):
        """Test model using SFPMixin."""

    # Test valid SFP module data
    model = TestModel(
        sfp_vendor="Ubiquiti",
        sfp_part="UF-MM-10G",
        sfp_serial="ABCD1234",
        sfp_temperature=45.5,
        sfp_voltage=3.3,
        sfp_rxpower=-10.0,
        sfp_txpower=-5.0,
    )
    assert model.sfp_vendor == "Ubiquiti"
    assert model.sfp_temperature == 45.5

    # Test voltage constraints
    with pytest.raises(ValidationError):
        TestModel(sfp_voltage=-1)

    # Test power constraints
    with pytest.raises(ValidationError):
        TestModel(sfp_rxpower=1)
    with pytest.raises(ValidationError):
        TestModel(sfp_txpower=1)


def test_storm_control_mixin():
    """Test StormControlMixin validation."""

    class TestModel(StormControlMixin, UnifiBaseModel):
        """Test model using StormControlMixin."""

    # Test valid storm control settings
    model = TestModel(
        stormctrl_bcast_enabled=True,
        stormctrl_bcast_rate=80,
        stormctrl_mcast_enabled=True,
        stormctrl_mcast_rate=70,
        stormctrl_ucast_enabled=True,
        stormctrl_ucast_rate=60,
    )
    assert model.stormctrl_bcast_rate == 80
    assert model.stormctrl_mcast_rate == 70
    assert model.stormctrl_ucast_rate == 60

    # Test rate boundaries
    model = TestModel(
        stormctrl_bcast_rate=0,
        stormctrl_mcast_rate=100,
    )
    assert model.stormctrl_bcast_rate == 0
    assert model.stormctrl_mcast_rate == 100

    # Test invalid rates
    with pytest.raises(ValidationError):
        TestModel(stormctrl_bcast_rate=101)
    with pytest.raises(ValidationError):
        TestModel(stormctrl_mcast_rate=-1)
    with pytest.raises(ValidationError):
        TestModel(stormctrl_ucast_rate=200)


def test_wifi_stats_edge_cases():
    """Test WifiStats edge cases and complex validations."""
    # Test all radio types with valid channels
    valid_combinations = [
        (RadioType.NG, 1),  # 2.4 GHz min
        (RadioType.NG, 14),  # 2.4 GHz max
        (RadioType.NA, 36),  # 5 GHz min
        (RadioType.NA, 165),  # 5 GHz max
        (RadioType._6E, 1),  # 6 GHz min
        (RadioType._6E, 233),  # 6 GHz max
    ]
    for radio_type, channel in valid_combinations:
        stats = WifiStats(
            ap_mac=VALID_MAC,
            radio=radio_type,
            radio_proto=RadioProto.AX,
            essid="test",
            bssid=VALID_MAC,
            signal=-70,
            noise=-90,
            channel=channel,
        )
        assert stats.channel == channel

    # Test invalid channel combinations
    invalid_combinations = [
        (RadioType.NG, 0),  # Below 2.4 GHz
        (RadioType.NG, 15),  # Above 2.4 GHz
        (RadioType.NA, 35),  # Below 5 GHz
        (RadioType.NA, 166),  # Above 5 GHz
        (RadioType._6E, 0),  # Below 6 GHz
        (RadioType._6E, 234),  # Above 6 GHz
    ]
    for radio_type, channel in invalid_combinations:
        with pytest.raises(ValidationError):
            WifiStats(
                ap_mac=VALID_MAC,
                radio=radio_type,
                radio_proto=RadioProto.AX,
                essid="test",
                bssid=VALID_MAC,
                signal=-70,
                noise=-90,
                channel=channel,
            )

    # Test signal/noise constraints
    with pytest.raises(ValidationError):
        WifiStats(
            ap_mac=VALID_MAC,
            radio=RadioType.NG,
            radio_proto=RadioProto.AX,
            essid="test",
            bssid=VALID_MAC,
            signal=0,  # Should be negative
            noise=-90,
        )

    with pytest.raises(ValidationError):
        WifiStats(
            ap_mac=VALID_MAC,
            radio=RadioType.NG,
            radio_proto=RadioProto.AX,
            essid="test",
            bssid=VALID_MAC,
            signal=-70,
            noise=0,  # Should be negative
        )

    # Test channel width values
    valid_widths = [20, 40, 80, 160, 320]
    for width in valid_widths:
        stats = WifiStats(
            ap_mac=VALID_MAC,
            radio=RadioType.NA,
            radio_proto=RadioProto.AX,
            essid="test",
            bssid=VALID_MAC,
            signal=-70,
            noise=-90,
            channel_width=width,
        )
        assert stats.channel_width == width

    # Test invalid channel width
    invalid_widths = [10, 30, 60, 120, 240]
    for width in invalid_widths:
        with pytest.raises(ValidationError):
            WifiStats(
                ap_mac=VALID_MAC,
                radio=RadioType.NA,
                radio_proto=RadioProto.AX,
                essid="test",
                bssid=VALID_MAC,
                signal=-70,
                noise=-90,
                channel_width=width,
            )


def test_client_complex_validation():
    """Test Client model complex validation scenarios."""
    # Test timestamp sequence validation
    timestamps = {
        "first_seen": 1000,
        "last_seen": 2000,
        "assoc_time": 1500,
        "latest_assoc_time": 1600,
        "disconnect_timestamp": 1800,
    }

    # Test valid sequence
    client = Client(
        hostname="test", mac=VALID_MAC, ip=VALID_IPV4, is_wired=True, **timestamps
    )
    assert client.first_seen == 1000
    assert client.latest_assoc_time == 1600

    # Test invalid sequences
    invalid_sequences = [
        {"first_seen": 2000, "last_seen": 1000},  # first after last
        {"assoc_time": 1600, "latest_assoc_time": 1500},  # latest before first
        {
            "first_seen": 2000,
            "assoc_time": 1000,
            "last_seen": 1500,
        },  # inconsistent order
    ]

    for invalid_seq in invalid_sequences:
        test_data = timestamps.copy()
        test_data.update(invalid_seq)
        with pytest.raises(ValidationError):
            Client(
                hostname="test",
                mac=VALID_MAC,
                ip=VALID_IPV4,
                is_wired=True,
                **test_data,
            )

    # Test IPv6 validation
    client = Client(
        hostname="test",
        mac=VALID_MAC,
        ip=VALID_IPV4,
        is_wired=True,
        first_seen=1000,
        ipv6_addresses=[VALID_IPV6],
    )
    assert client.ipv6_addresses == [VALID_IPV6]

    # Test invalid IPv6
    with pytest.raises(ValidationError):
        Client(
            hostname="test",
            mac=VALID_MAC,
            ip=VALID_IPV4,
            is_wired=True,
            first_seen=1000,
            ipv6_addresses=["invalid-ipv6"],
        )

    # Test multiple MAC addresses
    client = Client(
        hostname="test",
        mac=VALID_MAC,
        ip=VALID_IPV4,
        is_wired=True,
        first_seen=1000,
        gw_mac=VALID_MAC,
        sw_mac=VALID_MAC,
    )
    assert client.mac == VALID_MAC.lower()
    assert client.gw_mac == VALID_MAC.lower()
    assert client.sw_mac == VALID_MAC.lower()

    # Test invalid MAC combinations
    invalid_macs = [
        {"mac": "invalid", "gw_mac": VALID_MAC},
        {"mac": VALID_MAC, "gw_mac": "invalid"},
        {"mac": VALID_MAC, "sw_mac": "invalid"},
    ]

    for invalid_mac in invalid_macs:
        with pytest.raises(ValidationError):
            Client(
                hostname="test",
                ip=VALID_IPV4,
                is_wired=True,
                first_seen=1000,
                **invalid_mac,
            )


def test_port_stats_complex_validation():
    """Test PortStats model complex validation scenarios."""
    # Test valid port configuration
    port = PortStats(
        port_idx=1,
        name="Port 1",
        media="GE",
        speed=1000,
        up=True,
        is_uplink=False,
        mac=VALID_MAC,
        rx_errors=0,
        tx_errors=0,
        type="ethernet",
        port_poe=True,
        poe_mode="auto",
        stormctrl_bcast_rate=80,
        stormctrl_mcast_rate=80,
        stormctrl_ucast_rate=80,
        port_security_mac_address=[VALID_MAC],
    )
    assert port.port_idx == 1
    assert port.speed == 1000

    # Test invalid port index
    with pytest.raises(ValidationError):
        PortStats(
            port_idx=0,  # Must be >= 1
            name="Port 0",
            media="GE",
            speed=1000,
            up=True,
            is_uplink=False,
            mac=VALID_MAC,
            rx_errors=0,
            tx_errors=0,
            type="ethernet",
        )

    # Test storm control rate combinations
    invalid_rates = [
        {"stormctrl_bcast_rate": 101},
        {"stormctrl_mcast_rate": -1},
        {"stormctrl_ucast_rate": 1000},
    ]

    for invalid_rate in invalid_rates:
        with pytest.raises(ValidationError):
            PortStats(
                port_idx=1,
                name="Port 1",
                media="GE",
                speed=1000,
                up=True,
                is_uplink=False,
                mac=VALID_MAC,
                rx_errors=0,
                tx_errors=0,
                type="ethernet",
                **invalid_rate,
            )

    # Test SFP module validation
    port = PortStats(
        port_idx=1,
        name="Port 1",
        media="SFP+",
        speed=10000,
        up=True,
        is_uplink=True,
        mac=VALID_MAC,
        rx_errors=0,
        tx_errors=0,
        type="sfp",
        sfp_vendor="Ubiquiti",
        sfp_part="UF-MM-10G",
        sfp_voltage=3.3,
        sfp_rxpower=-10.0,
        sfp_txpower=-5.0,
    )
    assert port.media == "SFP+"
    assert port.sfp_voltage == 3.3

    # Test invalid SFP power values
    invalid_powers = [
        {"sfp_rxpower": 1.0},  # Must be negative
        {"sfp_txpower": 0.0},  # Must be negative
        {"sfp_voltage": -1.0},  # Must be positive
    ]

    for invalid_power in invalid_powers:
        with pytest.raises(ValidationError):
            PortStats(
                port_idx=1,
                name="Port 1",
                media="SFP+",
                speed=10000,
                up=True,
                is_uplink=True,
                mac=VALID_MAC,
                rx_errors=0,
                tx_errors=0,
                type="sfp",
                **invalid_power,
            )
