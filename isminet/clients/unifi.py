"""UniFi Network API client."""

from typing import List, Dict, Any, Type, TypeVar
from pydantic import ValidationError

from ..config import APIConfig
from ..models.base import UnifiBaseModel
from ..models.devices import Device, Client
from ..models.network import NetworkConfiguration
from ..models.system import SystemStatus
from .base import BaseAPIClient as BaseClient, APIError, ResponseValidationError

T = TypeVar("T", bound=UnifiBaseModel)


class UnifiClient(BaseClient):
    """UniFi Network API client."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize UniFi Network API client."""
        super().__init__(config)
        self.site_path = f"/api/s/{config.site}"

    def _get_site_path(self, endpoint: str) -> str:
        """Get site-specific API endpoint path."""
        return f"{self.site_path}/{endpoint}"

    def _get_list_response(
        self,
        response: Dict[str, Any],
        model_class: Type[T],
    ) -> List[T]:
        """
        Extract and validate a list response from the UniFi API.

        Args:
            response: Raw API response dictionary
            model_class: Pydantic model class to validate items against

        Returns:
            List of validated model instances

        Raises:
            ResponseValidationError: If response structure is invalid or validation fails
        """
        if not isinstance(response, dict):
            raise ResponseValidationError(
                "Invalid response structure: expected dictionary", None
            )

        if "data" not in response:
            raise ResponseValidationError(
                "Invalid response structure: missing 'data' field", None
            )

        data = response["data"]
        if not isinstance(data, list):
            raise ResponseValidationError(
                "Invalid response structure: 'data' field must be a list", None
            )

        try:
            return [model_class(**item) for item in data]
        except ValidationError as e:
            raise ResponseValidationError("Failed to validate response items", e)

    def _get_single_response(
        self,
        response: Dict[str, Any],
        model_class: Type[T],
    ) -> T:
        """
        Extract and validate a single item response from the UniFi API.

        Args:
            response: Raw API response dictionary
            model_class: Pydantic model class to validate item against

        Returns:
            Validated model instance

        Raises:
            ResponseValidationError: If response structure is invalid or validation fails
        """
        if not isinstance(response, dict):
            raise ResponseValidationError(
                "Invalid response structure: expected dictionary", None
            )

        if "data" not in response:
            raise ResponseValidationError(
                "Invalid response structure: missing 'data' field", None
            )

        try:
            data = response["data"][0]
        except IndexError:
            raise ResponseValidationError("Response data is empty", None)

        try:
            return model_class(**data)
        except ValidationError as e:
            raise ResponseValidationError(
                f"Failed to validate {model_class.__name__}", e
            )

    def _get_list_by_endpoint(
        self,
        endpoint: str,
        model_class: Type[T],
    ) -> List[T]:
        """
        Get and validate a list response from an endpoint.

        Args:
            endpoint: API endpoint path
            model_class: Pydantic model class to validate items against

        Returns:
            List of validated model instances

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        response: Dict[str, Any] = self.get(endpoint)  # type: ignore
        if not isinstance(response, dict):
            raise ResponseValidationError("Invalid response structure", None)
        return self._get_list_response(response, model_class)

    def _get_by_mac(
        self,
        items: List[T],
        mac: str,
        item_type: str,
    ) -> T:
        """
        Find an item in a list by MAC address.

        Args:
            items: List of items to search
            mac: MAC address to find
            item_type: Type of item for error message

        Returns:
            Matching item

        Raises:
            APIError: If no item with matching MAC is found
        """
        for item in items:
            if item.mac == mac:  # type: ignore
                return item
        raise APIError(f"{item_type} with MAC {mac} not found")

    def get_devices(self) -> List[Device]:
        """
        Get list of network devices.

        Returns:
            List[Device]: List of network devices

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        endpoint = self._get_site_path("stat/device")
        return self._get_list_by_endpoint(endpoint, Device)

    def get_clients(self) -> List[Client]:
        """
        Get list of network clients.

        Returns:
            List[Client]: List of network clients

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        endpoint = self._get_site_path("stat/sta")
        return self._get_list_by_endpoint(endpoint, Client)

    def get_device(self, mac: str) -> Device:
        """
        Get a specific network device by MAC address.

        Args:
            mac: MAC address of the device

        Returns:
            Device: Network device

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        devices = self.get_devices()
        return self._get_by_mac(devices, mac, "Device")

    def get_client(self, mac: str) -> Client:
        """
        Get a specific network client by MAC address.

        Args:
            mac: MAC address of the client

        Returns:
            Client: Network client

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        clients = self.get_clients()
        return self._get_by_mac(clients, mac, "Client")

    def _get_single_by_endpoint(
        self,
        endpoint: str,
        model_class: Type[T],
    ) -> T:
        """
        Get and validate a single response from an endpoint.

        Args:
            endpoint: API endpoint path
            model_class: Pydantic model class to validate against

        Returns:
            Validated model instance

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        response: Dict[str, Any] = self.get(endpoint)  # type: ignore
        return self._get_single_response(response, model_class)

    def get_network_config(self, network_id: str) -> NetworkConfiguration:
        """
        Get network configuration.

        Args:
            network_id: Network ID

        Returns:
            NetworkConfiguration: Network configuration

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        endpoint = self._get_site_path(f"rest/networkconf/{network_id}")
        return self._get_single_by_endpoint(endpoint, NetworkConfiguration)

    def get_system_health(self) -> SystemStatus:
        """
        Get system health status.

        Returns:
            SystemStatus: System health status

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        endpoint = self._get_site_path("stat/health")
        return self._get_single_by_endpoint(endpoint, SystemStatus)
