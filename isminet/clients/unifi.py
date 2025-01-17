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
        self.logger.info(
            "initialized_unifi_client",
            site=config.site,
            site_path=self.site_path,
            host=config.host,
            port=config.port,
            verify_ssl=config.verify_ssl,
        )

    def _get_site_path(self, endpoint: str) -> str:
        """Get site-specific API endpoint path."""
        path = f"{self.site_path}/{endpoint}"
        self.logger.debug(
            "constructed_site_path",
            endpoint=endpoint,
            path=path,
            site=self.site_path,
        )
        return path

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
            self.logger.error(
                "invalid_response_structure",
                expected="dictionary",
                received=type(response).__name__,
                response=str(response)[:200],  # Log first 200 chars of response
            )
            raise ResponseValidationError(
                "Invalid response structure: expected dictionary", None
            )

        if "data" not in response:
            self.logger.error(
                "missing_data_field",
                response_keys=list(response.keys()),
                response=str(response)[:200],  # Log first 200 chars of response
            )
            raise ResponseValidationError(
                "Invalid response structure: missing 'data' field", None
            )

        data = response["data"]
        if not isinstance(data, list):
            self.logger.error(
                "invalid_data_type",
                expected="list",
                received=type(data).__name__,
                data_preview=str(data)[:200],  # Log first 200 chars of data
            )
            raise ResponseValidationError(
                "Invalid response structure: 'data' field must be a list", None
            )

        try:
            items = [model_class(**item) for item in data]
            self.logger.debug(
                "validated_list_response",
                model=model_class.__name__,
                items_count=len(items),
                fields=list(items[0].model_fields.keys()) if items else [],
            )
            return items
        except ValidationError as e:
            self.logger.error(
                "response_validation_failed",
                model=model_class.__name__,
                error=str(e),
                error_type=type(e).__name__,
                validation_errors=e.errors(),
            )
            raise ResponseValidationError("Failed to validate response items", e)

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
        self.logger.debug(
            "fetching_list",
            endpoint=endpoint,
            model=model_class.__name__,
            method="GET",
        )
        try:
            response: Dict[str, Any] = self.get(endpoint)  # type: ignore
            self.logger.debug(
                "received_response",
                endpoint=endpoint,
                response_type=type(response).__name__,
                response_keys=list(response.keys())
                if isinstance(response, dict)
                else None,
            )
            if not isinstance(response, dict):
                self.logger.error(
                    "invalid_response_structure",
                    expected="dictionary",
                    received=type(response).__name__,
                    response=str(response)[:200],  # Log first 200 chars of response
                )
                raise ResponseValidationError("Invalid response structure", None)
            return self._get_list_response(response, model_class)
        except APIError as e:
            self.logger.error(
                "api_request_failed",
                endpoint=endpoint,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

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
        self.logger.debug(
            "searching_by_mac",
            mac=mac,
            item_type=item_type,
            items_count=len(items),
            available_macs=[item.mac for item in items],  # type: ignore
        )
        for item in items:
            if item.mac == mac:  # type: ignore
                self.logger.debug(
                    "found_item_by_mac",
                    mac=mac,
                    item_type=item_type,
                    item_fields=list(item.model_fields.keys()),
                )
                return item
        self.logger.error(
            "item_not_found",
            mac=mac,
            item_type=item_type,
            available_macs=[item.mac for item in items],  # type: ignore
        )
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
        self.logger.info("fetching_devices")
        endpoint = self._get_site_path("stat/device")
        try:
            devices = self._get_list_by_endpoint(endpoint, Device)
            self.logger.info(
                "fetched_devices",
                count=len(devices),
                device_types=list(set(d.type for d in devices)),
                models=list(set(d.model for d in devices)),
            )
            return devices
        except (APIError, ResponseValidationError) as e:
            self.logger.error(
                "failed_to_fetch_devices",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def get_clients(self) -> List[Client]:
        """
        Get list of network clients.

        Returns:
            List[Client]: List of network clients

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        self.logger.info("fetching_clients")
        endpoint = self._get_site_path("stat/sta")
        try:
            clients = self._get_list_by_endpoint(endpoint, Client)
            # Calculate statistics
            active_count = sum(
                1 for c in clients if c.last_seen is not None and c.last_seen > 0
            )
            guest_count = sum(1 for c in clients if c.is_guest is True)
            wired_count = sum(1 for c in clients if c.is_wired is True)
            self.logger.info(
                "fetched_clients",
                count=len(clients),
                active_count=active_count,
                guest_count=guest_count,
                wired_count=wired_count,
            )
            return clients
        except (APIError, ResponseValidationError) as e:
            self.logger.error(
                "failed_to_fetch_clients",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

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
        self.logger.info("fetching_device", mac=mac)
        try:
            devices = self.get_devices()
            device = self._get_by_mac(devices, mac, "Device")
            self.logger.info(
                "fetched_device",
                mac=mac,
                model=device.model,
                type=device.type,
                version=device.version,
                ip=device.ip,
                status=device.status,
                uptime=device.uptime,
            )
            return device
        except (APIError, ResponseValidationError) as e:
            self.logger.error(
                "failed_to_fetch_device",
                mac=mac,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

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
        self.logger.info("fetching_client", mac=mac)
        try:
            clients = self.get_clients()
            client = self._get_by_mac(clients, mac, "Client")
            # Calculate online status based on last_seen
            is_online = client.last_seen is not None and client.last_seen > 0
            self.logger.info(
                "fetched_client",
                mac=mac,
                hostname=client.hostname,
                ip=client.ip,
                is_online=is_online,
                is_guest=client.is_guest,
                is_wired=client.is_wired,
                first_seen=client.first_seen,
                last_seen=client.last_seen,
            )
            return client
        except (APIError, ResponseValidationError) as e:
            self.logger.error(
                "failed_to_fetch_client",
                mac=mac,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

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
            self.logger.error(
                "invalid_response_structure",
                expected="dictionary",
                received=type(response).__name__,
            )
            raise ResponseValidationError(
                "Invalid response structure: expected dictionary", None
            )

        if "data" not in response:
            self.logger.error("missing_data_field", response_keys=list(response.keys()))
            raise ResponseValidationError(
                "Invalid response structure: missing 'data' field", None
            )

        try:
            data = response["data"][0]
            item = model_class(**data)
            self.logger.debug(
                "validated_single_response",
                model=model_class.__name__,
            )
            return item
        except IndexError:
            self.logger.error("empty_response_data")
            raise ResponseValidationError("Response data is empty", None)
        except ValidationError as e:
            self.logger.error(
                "response_validation_failed",
                model=model_class.__name__,
                error=str(e),
            )
            raise ResponseValidationError(
                f"Failed to validate {model_class.__name__}", e
            )

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
        self.logger.debug(
            "fetching_single",
            endpoint=endpoint,
            model=model_class.__name__,
        )
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
        self.logger.info("fetching_network_config", network_id=network_id)
        endpoint = self._get_site_path(f"rest/networkconf/{network_id}")
        config = self._get_single_by_endpoint(endpoint, NetworkConfiguration)
        self.logger.info(
            "fetched_network_config",
            network_id=network_id,
            name=config.name,
            purpose=config.purpose,
        )
        return config

    def get_system_health(self) -> SystemStatus:
        """
        Get system health status.

        Returns:
            SystemStatus: System health status

        Raises:
            ResponseValidationError: If response validation fails
            APIError: If API request fails
        """
        self.logger.info("fetching_system_health")
        endpoint = self._get_site_path("stat/health")
        status = self._get_single_by_endpoint(endpoint, SystemStatus)
        self.logger.info(
            "fetched_system_health",
            health_checks=len(status.health),
            processes=len(status.processes),
            services=len(status.services),
        )
        return status
