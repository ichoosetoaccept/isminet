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
        """
        Returns the site-specific API path for the UniFi Network API.
        
        This method constructs the base API endpoint path using the site name from the client's configuration. The site path is a crucial component for making API requests to a specific UniFi network site.
        
        Returns:
            str: A URL path segment representing the site-specific API endpoint, formatted as "/api/s/{site_name}".
        
        Example:
            If the client's configuration has a site named "default", the method will return "/api/s/default".
        """
        return f"/api/s/{self.config.site}"

    def _get_list_response(
        self, response_data: Dict[str, Any], model: Type[T]
    ) -> List[T]:
        """
        Process API response data and convert it into a list of model instances.
        
        This method handles UniFi API responses that return a list of items, ensuring type-safe conversion to the specified model. If the response lacks a valid 'data' key or the data is not a list, an empty list is returned.
        
        Parameters:
            response_data (Dict[str, Any]): The raw API response dictionary
            model (Type[T]): The model class to instantiate for each item in the response
        
        Returns:
            List[T]: A list of model instances created from the response data
        
        Raises:
            TypeError: If an item cannot be instantiated with the given model
        """
        if "data" not in response_data or not isinstance(response_data["data"], list):
            return []
        return [model(**item) for item in response_data["data"]]

    # Device Management
    def get_device(self, mac: str) -> Device:
        """
        Retrieve a specific network device by its MAC address.
        
        Parameters:
            mac (str): The MAC address of the device to retrieve.
        
        Returns:
            Device: A Device object containing detailed information about the specified network device.
        
        Raises:
            HTTPError: If the device cannot be found or there is an API request error.
            ValueError: If an invalid MAC address is provided.
        
        Example:
            client = UnifiClient(...)
            device = client.get_device('00:11:22:33:44:55')
        """
        endpoint = f"{self.site_path}/stat/device/{mac}"
        result = self.get(endpoint, response_model=Device)
        return cast(Device, result)

    def get_devices(self) -> List[Device]:
        """
        Retrieve all devices from the UniFi Network.
        
        Sends a GET request to the device statistics endpoint for the current site and returns a list of Device objects.
        
        Returns:
            List[Device]: A list of all devices registered in the UniFi Network site.
        
        Raises:
            APIError: If the request to the UniFi API fails or returns an invalid response.
        """
        endpoint = f"{self.site_path}/stat/device"
        response = self.get(endpoint)
        return self._get_list_response(response, Device)

    def update_device(self, mac: str, settings: Dict[str, Any]) -> Device:
        """
        Update settings for a specific network device.
        
        Parameters:
            mac (str): The MAC address of the device to update
            settings (Dict[str, Any]): A dictionary containing the device settings to modify
        
        Returns:
            Device: The updated device configuration after applying the specified settings
        
        Raises:
            APIError: If the device update request fails or the device cannot be found
            ValueError: If an invalid MAC address or settings are provided
        """
        endpoint = f"{self.site_path}/rest/device/{mac}"
        result = self.put(endpoint, json=settings, response_model=Device)
        return cast(Device, result)

    def restart_device(self, mac: str) -> None:
        """
        Restart a specific network device by its MAC address.
        
        Parameters:
            mac (str): The MAC address of the device to restart.
        
        Raises:
            APIError: If the restart command fails or the device cannot be reached.
        
        Example:
            client.restart_device("00:11:22:33:44:55")
        """
        endpoint = f"{self.site_path}/cmd/devmgr/restart"
        self.post(endpoint, json={"mac": mac})

    # Client Management
    def get_client(self, mac: str) -> Client:
        """
        Retrieve a specific network client by its MAC address.
        
        Parameters:
            mac (str): The MAC address of the client to retrieve.
        
        Returns:
            Client: A Client object containing detailed information about the specified network client.
        
        Raises:
            HTTPError: If the client cannot be found or there is an API request error.
            ValueError: If an invalid MAC address is provided.
        
        Example:
            client = unifi_client.get_client("00:11:22:33:44:55")
        """
        endpoint = f"{self.site_path}/stat/sta/{mac}"
        result = self.get(endpoint, response_model=Client)
        return cast(Client, result)

    def get_clients(self) -> List[Client]:
        """
        Retrieve all network clients connected to the UniFi network.
        
        This method fetches a list of all clients (stations) from the UniFi network by querying
        the site-specific statistics endpoint. Each client is instantiated as a Client object.
        
        Returns:
            List[Client]: A list of Client objects representing all connected network clients.
        
        Raises:
            APIError: If there is an error retrieving the client information from the UniFi API.
        """
        endpoint = f"{self.site_path}/stat/sta"
        response = self.get(endpoint)
        return self._get_list_response(response, Client)

    # Wireless Settings
    def get_network_profile(self, profile_id: str) -> NetworkProfile:
        """
        Retrieve a specific network profile by its unique identifier.
        
        Parameters:
            profile_id (str): The unique identifier of the network profile to retrieve.
        
        Returns:
            NetworkProfile: The network profile configuration matching the provided profile ID.
        
        Raises:
            HTTPError: If the network profile cannot be retrieved from the UniFi API.
            ValueError: If an invalid profile ID is provided.
        
        Example:
            client = UnifiClient(...)
            profile = client.get_network_profile('5f3a1b2c3d4e5f')
        """
        endpoint = f"{self.site_path}/rest/networkconf/{profile_id}"
        result = self.get(endpoint, response_model=NetworkProfile)
        return cast(NetworkProfile, result)

    def get_network_profiles(self) -> List[NetworkProfile]:
        """
        Retrieve all network profiles from the UniFi Network API.
        
        This method fetches network configurations for the current site by making a GET request
        to the network configuration endpoint and converting the response into a list of NetworkProfile instances.
        
        Returns:
            List[NetworkProfile]: A list of network profile configurations for the current site.
        
        Raises:
            APIError: If there is an error retrieving network profiles from the UniFi API.
        """
        endpoint = f"{self.site_path}/rest/networkconf"
        response = self.get(endpoint)
        return self._get_list_response(response, NetworkProfile)

    def get_wlan_config(self, device_mac: str) -> WLANConfiguration:
        """
        Retrieve the wireless network (WLAN) configuration for a specific device.
        
        Parameters:
            device_mac (str): The MAC address of the device to retrieve WLAN configuration for.
        
        Returns:
            WLANConfiguration: The wireless network configuration details for the specified device.
        
        Raises:
            HTTPError: If the API request fails or the device is not found.
            ValueError: If the response cannot be parsed into a WLANConfiguration object.
        
        Example:
            client = UnifiClient(...)
            wlan_config = client.get_wlan_config("00:11:22:33:44:55")
        """
        endpoint = f"{self.site_path}/rest/wlanconf/{device_mac}"
        result = self.get(endpoint, response_model=WLANConfiguration)
        return cast(WLANConfiguration, result)

    def update_wlan_config(
        self, device_mac: str, config: WLANConfiguration
    ) -> WLANConfiguration:
        """
        Update the WLAN configuration for a specific device.
        
        Parameters:
            device_mac (str): The MAC address of the device to update
            config (WLANConfiguration): The new WLAN configuration settings to apply
        
        Returns:
            WLANConfiguration: The updated WLAN configuration after applying the changes
        
        Raises:
            APIError: If the configuration update fails or the device is not found
        """
        endpoint = f"{self.site_path}/rest/wlanconf/{device_mac}"
        result = self.put(
            endpoint, json=config.model_dump(), response_model=WLANConfiguration
        )
        return cast(WLANConfiguration, result)

    # Network Settings
    def get_network_config(self, network_id: str) -> NetworkConfiguration:
        """
        Retrieve the network configuration for a specific network by its unique identifier.
        
        Parameters:
            network_id (str): The unique identifier of the network configuration to retrieve.
        
        Returns:
            NetworkConfiguration: A configuration object containing details of the specified network.
        
        Raises:
            HTTPError: If the network configuration cannot be retrieved from the UniFi API.
            ValueError: If an invalid network ID is provided.
        
        Example:
            client = UnifiClient(...)
            network_config = client.get_network_config("5f3a1b2c3d4e5f")
        """
        endpoint = f"{self.site_path}/rest/networkconf/{network_id}"
        result = self.get(endpoint, response_model=NetworkConfiguration)
        return cast(NetworkConfiguration, result)

    def update_network_config(
        self, network_id: str, config: NetworkConfiguration
    ) -> NetworkConfiguration:
        """
        Update the configuration for a specific network.
        
        Parameters:
            network_id (str): The unique identifier of the network to be updated.
            config (NetworkConfiguration): The updated network configuration details.
        
        Returns:
            NetworkConfiguration: The updated network configuration after applying the changes.
        
        Raises:
            HTTPError: If the network configuration update fails due to API or network issues.
            ValueError: If the provided network configuration is invalid.
        
        Example:
            client = UnifiClient(...)
            network_config = NetworkConfiguration(...)
            updated_config = client.update_network_config('network123', network_config)
        """
        endpoint = f"{self.site_path}/rest/networkconf/{network_id}"
        result = self.put(
            endpoint, json=config.model_dump(), response_model=NetworkConfiguration
        )
        return cast(NetworkConfiguration, result)

    def get_vlan_config(self, vlan_id: int) -> VLANConfiguration:
        """
        Retrieve the configuration for a specific VLAN by its identifier.
        
        Parameters:
            vlan_id (int): The unique identifier of the VLAN configuration to retrieve.
        
        Returns:
            VLANConfiguration: The detailed configuration settings for the specified VLAN.
        
        Raises:
            HTTPError: If the API request fails or the VLAN configuration cannot be found.
            ValueError: If an invalid VLAN ID is provided.
        
        Example:
            client = UnifiClient(...)
            vlan_config = client.get_vlan_config(10)  # Retrieves configuration for VLAN 10
        """
        endpoint = f"{self.site_path}/rest/vlanconf/{vlan_id}"
        result = self.get(endpoint, response_model=VLANConfiguration)
        return cast(VLANConfiguration, result)

    def get_dhcp_config(self, network_id: str) -> DHCPConfiguration:
        """
        Retrieve the DHCP configuration for a specific network.
        
        Parameters:
            network_id (str): The unique identifier of the network for which DHCP configuration is requested.
        
        Returns:
            DHCPConfiguration: A configuration object containing DHCP settings for the specified network.
        
        Raises:
            APIError: If the network ID is invalid or the configuration cannot be retrieved.
            RequestException: If there are network-related issues during the API request.
        
        Example:
            client = UnifiClient(...)
            dhcp_config = client.get_dhcp_config("default")
        """
        endpoint = f"{self.site_path}/rest/dhcpconf/{network_id}"
        result = self.get(endpoint, response_model=DHCPConfiguration)
        return cast(DHCPConfiguration, result)

    # System Status
    def get_system_health(self) -> SystemHealth:
        """
        Retrieve the current system health status from the UniFi Network API.
        
        This method fetches comprehensive health metrics for the UniFi network system, providing an overview of the network's operational condition.
        
        Returns:
            SystemHealth: An object containing detailed system health information, including status of various network components and performance indicators.
        
        Raises:
            APIError: If there is an error retrieving the system health status from the API.
        """
        endpoint = f"{self.site_path}/stat/health"
        result = self.get(endpoint, response_model=SystemHealth)
        return cast(SystemHealth, result)

    def get_process_info(self) -> List[ProcessInfo]:
        """
        Retrieve detailed information about system processes from the UniFi Network API.
        
        This method fetches a list of running processes by making a GET request to the process statistics endpoint for the current site.
        
        Returns:
            List[ProcessInfo]: A list of process information objects, each containing details about a running system process.
        
        Raises:
            APIError: If there is an error retrieving process information from the UniFi Network API.
        """
        endpoint = f"{self.site_path}/stat/process"
        response = self.get(endpoint)
        return self._get_list_response(response, ProcessInfo)

    def get_service_status(self) -> List[ServiceStatus]:
        """
        Retrieve the status of services in the UniFi network.
        
        Sends a GET request to the service status endpoint and returns a list of ServiceStatus objects.
        
        Returns:
            List[ServiceStatus]: A list of service status details for the UniFi network.
        
        Raises:
            APIError: If there is an error retrieving the service status from the API.
        """
        endpoint = f"{self.site_path}/stat/service"
        response = self.get(endpoint)
        return self._get_list_response(response, ServiceStatus)

    def get_system_status(self) -> SystemStatus:
        """
        Retrieve the overall system status from the UniFi Network API.
        
        This method fetches system information by making a GET request to the system information endpoint for the configured site.
        
        Returns:
            SystemStatus: A comprehensive object containing the current system status details.
        
        Raises:
            APIError: If there is an error retrieving the system status from the API.
        """
        endpoint = f"{self.site_path}/stat/sysinfo"
        result = self.get(endpoint, response_model=SystemStatus)
        return cast(SystemStatus, result)
