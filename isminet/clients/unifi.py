"""UniFi Network API client implementation."""

from typing import List, Any, Type, TypeVar, Dict, cast
from .base import BaseAPIClient
from ..models.devices import Device, Client
from ..models.wireless import NetworkProfile, WLANConfiguration
from ..models.network import NetworkConfiguration, VLANConfiguration, DHCPConfiguration
from ..models.system import SystemHealth, ProcessInfo, ServiceStatus, SystemStatus

T = TypeVar("T")


class UnifiClient(BaseAPIClient):
    """UniFi Network API client implementation."""

    @property
    def site_path(self) -> str:
        """Get site-specific API path."""
        return f"/api/s/{self.config.site}"

    def _get_list_response(
        self, response_data: Dict[str, Any], model: Type[T]
    ) -> List[T]:
        """Handle list responses.

        Args:
            response_data: Response data
            model: Model type for items

        Returns:
            List of model instances
        """
        if "data" not in response_data or not isinstance(response_data["data"], list):
            return []
        return [model(**item) for item in response_data["data"]]

    # Device Management
    def get_device(self, mac: str) -> Device:
        """Get device by MAC address."""
        endpoint = f"{self.site_path}/stat/device/{mac}"
        result = self.get(endpoint, response_model=Device)
        return cast(Device, result)

    def get_devices(self) -> List[Device]:
        """Get all devices."""
        endpoint = f"{self.site_path}/stat/device"
        response = self.get(endpoint)
        return self._get_list_response(response, Device)

    def update_device(self, mac: str, settings: Dict[str, Any]) -> Device:
        """Update device settings."""
        endpoint = f"{self.site_path}/rest/device/{mac}"
        result = self.put(endpoint, json=settings, response_model=Device)
        return cast(Device, result)

    def restart_device(self, mac: str) -> None:
        """Restart device."""
        endpoint = f"{self.site_path}/cmd/devmgr/restart"
        self.post(endpoint, json={"mac": mac})

    # Client Management
    def get_client(self, mac: str) -> Client:
        """Get client by MAC address."""
        endpoint = f"{self.site_path}/stat/sta/{mac}"
        result = self.get(endpoint, response_model=Client)
        return cast(Client, result)

    def get_clients(self) -> List[Client]:
        """Get all clients."""
        endpoint = f"{self.site_path}/stat/sta"
        response = self.get(endpoint)
        return self._get_list_response(response, Client)

    # Wireless Settings
    def get_network_profile(self, profile_id: str) -> NetworkProfile:
        """Get network profile by ID."""
        endpoint = f"{self.site_path}/rest/networkconf/{profile_id}"
        result = self.get(endpoint, response_model=NetworkProfile)
        return cast(NetworkProfile, result)

    def get_network_profiles(self) -> List[NetworkProfile]:
        """Get all network profiles."""
        endpoint = f"{self.site_path}/rest/networkconf"
        response = self.get(endpoint)
        return self._get_list_response(response, NetworkProfile)

    def get_wlan_config(self, device_mac: str) -> WLANConfiguration:
        """Get WLAN configuration for device."""
        endpoint = f"{self.site_path}/rest/wlanconf/{device_mac}"
        result = self.get(endpoint, response_model=WLANConfiguration)
        return cast(WLANConfiguration, result)

    def update_wlan_config(
        self, device_mac: str, config: WLANConfiguration
    ) -> WLANConfiguration:
        """Update WLAN configuration for device."""
        endpoint = f"{self.site_path}/rest/wlanconf/{device_mac}"
        result = self.put(
            endpoint, json=config.model_dump(), response_model=WLANConfiguration
        )
        return cast(WLANConfiguration, result)

    # Network Settings
    def get_network_config(self, network_id: str) -> NetworkConfiguration:
        """Get network configuration by ID."""
        endpoint = f"{self.site_path}/rest/networkconf/{network_id}"
        result = self.get(endpoint, response_model=NetworkConfiguration)
        return cast(NetworkConfiguration, result)

    def update_network_config(
        self, network_id: str, config: NetworkConfiguration
    ) -> NetworkConfiguration:
        """Update network configuration."""
        endpoint = f"{self.site_path}/rest/networkconf/{network_id}"
        result = self.put(
            endpoint, json=config.model_dump(), response_model=NetworkConfiguration
        )
        return cast(NetworkConfiguration, result)

    def get_vlan_config(self, vlan_id: int) -> VLANConfiguration:
        """Get VLAN configuration by ID."""
        endpoint = f"{self.site_path}/rest/vlanconf/{vlan_id}"
        result = self.get(endpoint, response_model=VLANConfiguration)
        return cast(VLANConfiguration, result)

    def get_dhcp_config(self, network_id: str) -> DHCPConfiguration:
        """Get DHCP configuration for network."""
        endpoint = f"{self.site_path}/rest/dhcpconf/{network_id}"
        result = self.get(endpoint, response_model=DHCPConfiguration)
        return cast(DHCPConfiguration, result)

    # System Status
    def get_system_health(self) -> SystemHealth:
        """Get system health status."""
        endpoint = f"{self.site_path}/stat/health"
        result = self.get(endpoint, response_model=SystemHealth)
        return cast(SystemHealth, result)

    def get_process_info(self) -> List[ProcessInfo]:
        """Get process information."""
        endpoint = f"{self.site_path}/stat/process"
        response = self.get(endpoint)
        return self._get_list_response(response, ProcessInfo)

    def get_service_status(self) -> List[ServiceStatus]:
        """Get service status."""
        endpoint = f"{self.site_path}/stat/service"
        response = self.get(endpoint)
        return self._get_list_response(response, ServiceStatus)

    def get_system_status(self) -> SystemStatus:
        """Get system status."""
        endpoint = f"{self.site_path}/stat/sysinfo"
        result = self.get(endpoint, response_model=SystemStatus)
        return cast(SystemStatus, result)
