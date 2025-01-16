"""Tests for wireless settings models."""

import pytest
from pydantic import ValidationError

from isminet.models.wireless import RadioSettings, NetworkProfile, WLANConfiguration
from isminet.models.enums import RadioType, RadioProto

# Test data
VALID_RADIO_SETTINGS_2G = {
    "name": "Radio0",
    "radio": RadioType.NG,
    "radio_proto": RadioProto.AX,
    "is_enabled": True,
    "channel": 6,
    "channel_width": 40,
    "tx_power": 20,
    "tx_power_mode": "auto",
}

VALID_RADIO_SETTINGS_5G = {
    "name": "Radio1",
    "radio": RadioType.NA,
    "radio_proto": RadioProto.AX,
    "is_enabled": True,
    "channel": 36,
    "channel_width": 80,
    "tx_power": 23,
    "tx_power_mode": "auto",
}

VALID_RADIO_SETTINGS_6G = {
    "name": "Radio2",
    "radio": RadioType._6E,
    "radio_proto": RadioProto.AX,
    "is_enabled": True,
    "channel": 37,
    "channel_width": 160,
    "tx_power": 25,
    "tx_power_mode": "auto",
}

VALID_NETWORK_PROFILE = {
    "name": "Main Network",
    "ssid": "MyWiFi",
    "enabled": True,
    "is_guest": False,
    "security": "wpa-psk",
    "wpa_mode": "wpa3",
    "encryption": "aes",
}

VALID_WLAN_CONFIG = {
    "radio_table": [VALID_RADIO_SETTINGS_2G, VALID_RADIO_SETTINGS_5G],
    "network_profiles": [VALID_NETWORK_PROFILE],
}


class TestRadioSettings:
    """Test RadioSettings model."""

    def test_valid_2g_radio(self):
        """Test valid 2.4 GHz radio settings."""
        radio = RadioSettings(**VALID_RADIO_SETTINGS_2G)
        assert radio.name == "Radio0"
        assert radio.radio == RadioType.NG
        assert radio.channel == 6

    def test_valid_5g_radio(self):
        """Test valid 5 GHz radio settings."""
        radio = RadioSettings(**VALID_RADIO_SETTINGS_5G)
        assert radio.name == "Radio1"
        assert radio.radio == RadioType.NA
        assert radio.channel == 36

    def test_valid_6g_radio(self):
        """Test valid 6 GHz radio settings."""
        radio = RadioSettings(**VALID_RADIO_SETTINGS_6G)
        assert radio.name == "Radio2"
        assert radio.radio == RadioType._6E
        assert radio.channel == 37

    def test_invalid_2g_channel(self):
        """Test invalid 2.4 GHz channel."""
        invalid_data = VALID_RADIO_SETTINGS_2G.copy()
        invalid_data["channel"] = 15
        with pytest.raises(
            ValidationError, match="2.4 GHz channels must be between 1 and 14"
        ):
            RadioSettings(**invalid_data)

    def test_invalid_5g_channel(self):
        """Test invalid 5 GHz channel."""
        invalid_data = VALID_RADIO_SETTINGS_5G.copy()
        invalid_data["channel"] = 35
        with pytest.raises(
            ValidationError, match="5 GHz channels must be between 36 and 165"
        ):
            RadioSettings(**invalid_data)

    def test_invalid_6g_channel(self):
        """Test invalid 6 GHz channel."""
        invalid_data = VALID_RADIO_SETTINGS_6G.copy()
        invalid_data["channel"] = 234
        with pytest.raises(
            ValidationError, match="6 GHz channels must be between 1 and 233"
        ):
            RadioSettings(**invalid_data)

    def test_invalid_channel_width(self):
        """Test invalid channel width."""
        invalid_data = VALID_RADIO_SETTINGS_2G.copy()
        invalid_data["channel_width"] = 30
        with pytest.raises(
            ValidationError, match="Channel width must be 20, 40, 80, 160, or 320"
        ):
            RadioSettings(**invalid_data)

    def test_invalid_tx_power(self):
        """Test invalid transmit power."""
        invalid_data = VALID_RADIO_SETTINGS_2G.copy()
        invalid_data["tx_power"] = 31
        with pytest.raises(ValidationError):
            RadioSettings(**invalid_data)


class TestNetworkProfile:
    """Test NetworkProfile model."""

    def test_valid_network(self):
        """Test valid network profile."""
        network = NetworkProfile(**VALID_NETWORK_PROFILE)
        assert network.name == "Main Network"
        assert network.ssid == "MyWiFi"
        assert network.security == "wpa-psk"

    def test_invalid_security(self):
        """Test invalid security type."""
        invalid_data = VALID_NETWORK_PROFILE.copy()
        invalid_data["security"] = "invalid"
        with pytest.raises(ValidationError, match="Security type must be one of"):
            NetworkProfile(**invalid_data)

    def test_invalid_wpa_mode(self):
        """Test invalid WPA mode."""
        invalid_data = VALID_NETWORK_PROFILE.copy()
        invalid_data["wpa_mode"] = "invalid"
        with pytest.raises(ValidationError, match="WPA mode must be one of"):
            NetworkProfile(**invalid_data)

    def test_invalid_encryption(self):
        """Test invalid encryption type."""
        invalid_data = VALID_NETWORK_PROFILE.copy()
        invalid_data["encryption"] = "invalid"
        with pytest.raises(ValidationError, match="Encryption type must be one of"):
            NetworkProfile(**invalid_data)

    def test_invalid_vlan_id(self):
        """Test invalid VLAN ID."""
        invalid_data = VALID_NETWORK_PROFILE.copy()
        invalid_data["vlan_enabled"] = True
        invalid_data["vlan_id"] = 4095
        with pytest.raises(ValidationError):
            NetworkProfile(**invalid_data)

    def test_mac_filter_validation(self):
        """Test MAC filter list validation."""
        valid_data = VALID_NETWORK_PROFILE.copy()
        valid_data["mac_filter_enabled"] = True
        valid_data["mac_filter_list"] = ["00:11:22:33:44:55", "AA:BB:CC:DD:EE:FF"]
        valid_data["mac_filter_policy"] = "allow"
        network = NetworkProfile(**valid_data)
        assert len(network.mac_filter_list) == 2

        # Test invalid MAC address
        invalid_data = valid_data.copy()
        invalid_data["mac_filter_list"] = ["invalid-mac"]
        with pytest.raises(ValidationError):
            NetworkProfile(**invalid_data)


class TestWLANConfiguration:
    """Test WLANConfiguration model."""

    def test_valid_config(self):
        """Test valid WLAN configuration."""
        config = WLANConfiguration(**VALID_WLAN_CONFIG)
        assert len(config.radio_table) == 2
        assert len(config.network_profiles) == 1

    def test_invalid_pmf_mode(self):
        """Test invalid PMF mode."""
        invalid_data = VALID_WLAN_CONFIG.copy()
        invalid_data["pmf_mode"] = "invalid"
        with pytest.raises(ValidationError, match="PMF mode must be one of"):
            WLANConfiguration(**invalid_data)

    def test_invalid_rssi_threshold(self):
        """Test invalid RSSI threshold."""
        invalid_data = VALID_WLAN_CONFIG.copy()
        invalid_data["minimum_rssi"] = 1  # Must be <= 0
        with pytest.raises(ValidationError):
            WLANConfiguration(**invalid_data)

    def test_invalid_rate_limits(self):
        """Test invalid rate limits."""
        invalid_data = VALID_WLAN_CONFIG.copy()
        invalid_data["minimum_uplink"] = -1  # Must be >= 0
        with pytest.raises(ValidationError):
            WLANConfiguration(**invalid_data)

        invalid_data = VALID_WLAN_CONFIG.copy()
        invalid_data["minimum_downlink"] = -1  # Must be >= 0
        with pytest.raises(ValidationError):
            WLANConfiguration(**invalid_data)

    def test_invalid_max_clients(self):
        """Test invalid max clients."""
        invalid_data = VALID_WLAN_CONFIG.copy()
        invalid_data["max_clients"] = -1  # Must be >= 0
        with pytest.raises(ValidationError):
            WLANConfiguration(**invalid_data)
