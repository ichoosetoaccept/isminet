"""Tests for wireless settings models."""

import pytest
from typing import Dict, Any, List, Optional
from pydantic import ValidationError

from isminet.models.wireless import RadioSettings, NetworkProfile, WLANConfiguration
from isminet.models.enums import RadioType

# Test data
VALID_RADIO_SETTINGS_2G: Dict[str, Any] = {
    "name": "Radio0",
    "radio": RadioType.NG,
    "enabled": True,
    "channel": 6,
    "channel_width": 40,
    "tx_power": 20,
    "tx_power_mode": "auto",
}

VALID_RADIO_SETTINGS_5G: Dict[str, Any] = {
    "name": "Radio1",
    "radio": RadioType.NA,
    "enabled": True,
    "channel": 36,
    "channel_width": 80,
    "tx_power": 23,
    "tx_power_mode": "auto",
}

VALID_RADIO_SETTINGS_6G: Dict[str, Any] = {
    "name": "Radio2",
    "radio": RadioType._6E,
    "enabled": True,
    "channel": 37,
    "channel_width": 160,
    "tx_power": 25,
    "tx_power_mode": "auto",
}

VALID_NETWORK_PROFILE: Dict[str, Any] = {
    "name": "Main Network",
    "ssid": "MyWiFi",
    "enabled": True,
    "is_guest": False,
    "security": "wpa-psk",
    "wpa_mode": "wpa3",
    "encryption": "aes",
}


class TestRadioSettings:
    @pytest.mark.parametrize(
        "settings,expected_name,expected_radio",
        [
            (VALID_RADIO_SETTINGS_2G, "Radio0", RadioType.NG),
            (VALID_RADIO_SETTINGS_5G, "Radio1", RadioType.NA),
            (VALID_RADIO_SETTINGS_6G, "Radio2", RadioType._6E),
        ],
    )
    def test_valid_radio_settings(
        self, settings: Dict[str, Any], expected_name: str, expected_radio: RadioType
    ) -> None:
        """Test that valid radio settings are correctly parsed for different bands."""
        radio = RadioSettings(**settings)
        assert radio.name == expected_name
        assert radio.radio == expected_radio

    @pytest.mark.parametrize(
        "radio_type,expected_error",
        [
            ("invalid", "Invalid radio type"),
            ("ng+ax", "Invalid radio type"),
            ("na+n", "5GHz radio must use AC or AX"),
            ("6e+n", "6GHz radio only supports AX"),
            ("6e+ac", "6GHz radio only supports AX"),
        ],
    )
    def test_invalid_radio_types(self, radio_type: str, expected_error: str) -> None:
        """Test invalid radio types and protocol combinations."""
        settings = VALID_RADIO_SETTINGS_2G.copy()
        settings["radio"] = radio_type
        with pytest.raises(ValidationError, match=expected_error):
            RadioSettings(**settings)

    @pytest.mark.parametrize(
        "base_settings,invalid_channel,radio_type",
        [
            (VALID_RADIO_SETTINGS_2G, 15, "2.4GHz"),
            (VALID_RADIO_SETTINGS_5G, 35, "5GHz"),
            (VALID_RADIO_SETTINGS_6G, 200, "6GHz"),
        ],
    )
    def test_invalid_channels(
        self, base_settings: Dict[str, Any], invalid_channel: int, radio_type: str
    ) -> None:
        """Test that invalid channels are rejected for each radio band."""
        invalid_settings = base_settings.copy()
        invalid_settings["channel"] = invalid_channel
        with pytest.raises(ValidationError, match=f"Invalid {radio_type} channel"):
            RadioSettings(**invalid_settings)

    @pytest.mark.parametrize(
        "field,invalid_value,error_message",
        [
            ("channel_width", 30, "Invalid channel width"),
            ("tx_power", 35, "TX power must be between"),
            ("tx_power_mode", "invalid", "Invalid TX power mode"),
        ],
    )
    def test_invalid_radio_settings(
        self, field: str, invalid_value: Any, error_message: str
    ) -> None:
        """Test various invalid radio settings."""
        invalid_settings = VALID_RADIO_SETTINGS_2G.copy()
        invalid_settings[field] = invalid_value
        with pytest.raises(ValidationError, match=error_message):
            RadioSettings(**invalid_settings)


class TestNetworkProfile:
    @pytest.mark.parametrize(
        "field,expected_value",
        [
            ("name", "Main Network"),
            ("ssid", "MyWiFi"),
            ("enabled", True),
            ("is_guest", False),
            ("security", "wpa-psk"),
            ("wpa_mode", "wpa3"),
            ("encryption", "aes"),
            ("mac_filter_list", None),
        ],
    )
    def test_network_profile_fields(self, field: str, expected_value: Any) -> None:
        """Test that NetworkProfile correctly parses all fields."""
        network = NetworkProfile(**VALID_NETWORK_PROFILE)
        assert getattr(network, field) == expected_value

    @pytest.mark.parametrize(
        "field,invalid_value,error_message",
        [
            ("security", "invalid", "Invalid security type"),
            ("wpa_mode", "invalid", "Invalid WPA mode"),
            ("encryption", "invalid", "Invalid encryption type"),
            ("vlan_id", 4096, "VLAN ID must be between 1 and 4095"),
        ],
    )
    def test_invalid_network_settings(
        self, field: str, invalid_value: Any, error_message: str
    ) -> None:
        """Test various invalid network profile settings."""
        invalid_profile = VALID_NETWORK_PROFILE.copy()
        invalid_profile[field] = invalid_value
        with pytest.raises(ValidationError, match=error_message):
            NetworkProfile(**invalid_profile)

    @pytest.mark.parametrize(
        "mac_filter_list,expected_length,error_pattern",
        [
            (None, 0, None),  # Default case
            ([], 0, None),  # Empty list
            (["00:11:22:33:44:55"], 1, None),  # Valid MAC
            (
                ["00:11:22:33:44:55", "AA:BB:CC:DD:EE:FF"],
                2,
                None,
            ),  # Multiple valid MACs
            (["invalid"], None, "Invalid MAC address format"),  # Invalid MAC
            (
                ["00:11:22:33:44:55", "invalid"],
                None,
                "Invalid MAC address format",
            ),  # Mixed valid/invalid
        ],
    )
    def test_mac_filter_validation(
        self,
        mac_filter_list: Optional[List[str]],
        expected_length: Optional[int],
        error_pattern: Optional[str],
    ) -> None:
        """Test MAC filter list validation with various scenarios."""
        profile_data = VALID_NETWORK_PROFILE.copy()
        if mac_filter_list is not None:
            profile_data["mac_filter_list"] = mac_filter_list

        if error_pattern:
            with pytest.raises(ValidationError, match=error_pattern):
                NetworkProfile(**profile_data)
        else:
            profile = NetworkProfile(**profile_data)
            assert len(profile.mac_filter_list or []) == expected_length


class TestWLANConfiguration:
    @pytest.mark.parametrize(
        "radio_settings,network_profile,expected_counts",
        [
            (
                [VALID_RADIO_SETTINGS_2G],
                [VALID_NETWORK_PROFILE],
                {"radio_table": 1, "network_profiles": 1},
            ),
            (
                [VALID_RADIO_SETTINGS_2G, VALID_RADIO_SETTINGS_5G],
                [VALID_NETWORK_PROFILE],
                {"radio_table": 2, "network_profiles": 1},
            ),
            (
                [VALID_RADIO_SETTINGS_2G],
                [VALID_NETWORK_PROFILE, VALID_NETWORK_PROFILE],
                {"radio_table": 1, "network_profiles": 2},
            ),
        ],
    )
    def test_valid_config(
        self,
        radio_settings: List[Dict[str, Any]],
        network_profile: List[Dict[str, Any]],
        expected_counts: Dict[str, int],
    ) -> None:
        """Test various valid WLAN configurations."""
        config = WLANConfiguration(
            radio_table=[RadioSettings(**rs) for rs in radio_settings],
            network_profiles=[NetworkProfile(**np) for np in network_profile],
        )
        assert len(config.radio_table) == expected_counts["radio_table"]
        assert len(config.network_profiles) == expected_counts["network_profiles"]

    @pytest.mark.parametrize(
        "field,invalid_value,error_message",
        [
            ("pmf_mode", "invalid", "Invalid PMF mode"),
            ("minimum_rssi", 100, "RSSI must be between -100 and 0"),
            ("minimum_uplink", -1, "Rate limit must be non-negative"),
            ("max_clients", 0, "Maximum clients must be greater than 0"),
        ],
    )
    def test_invalid_wlan_settings(
        self, field: str, invalid_value: Any, error_message: str
    ) -> None:
        """Test various invalid WLAN configuration settings."""
        with pytest.raises(ValidationError, match=error_message):
            config_data = {
                "radio_table": [RadioSettings(**VALID_RADIO_SETTINGS_2G)],
                "network_profiles": [NetworkProfile(**VALID_NETWORK_PROFILE)],
                field: invalid_value,
            }
            WLANConfiguration(**config_data)
