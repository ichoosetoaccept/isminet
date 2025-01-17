"""System models for UniFi Network API."""

from typing import List, Optional, Any, Dict
from pydantic import Field, field_validator, model_validator

from .base import UnifiBaseModel
from .enums import DeviceType
from .validators import VERSION_PATTERN
from ..logging import get_logger

logger = get_logger(__name__)


class ProcessInfo(UnifiBaseModel):
    """Process information model."""

    pid: int = Field(description="Process ID", ge=1)
    name: str = Field(description="Process name", min_length=1)
    cpu_usage: float = Field(description="CPU usage percentage", ge=0, le=100)
    mem_usage: float = Field(description="Memory usage percentage", ge=0, le=100)
    mem_rss: int = Field(description="Resident set size in bytes", ge=0)
    mem_vsz: int = Field(description="Virtual memory size in bytes", ge=0)
    threads: Optional[int] = Field(None, description="Number of threads", ge=1)
    uptime: Optional[int] = Field(None, description="Process uptime in seconds", ge=0)


class SystemHealth(UnifiBaseModel):
    """System health model."""

    device_type: DeviceType = Field(description="Device type")
    subsystem: str = Field(description="Subsystem name", min_length=1)
    status: str = Field(description="Health status")
    status_code: int = Field(description="Status code", ge=0)
    status_message: str = Field(description="Status message", min_length=1)
    last_check: int = Field(description="Last check timestamp")
    next_check: int = Field(description="Next check timestamp")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status field."""
        valid_statuses = {"ok", "warning", "error"}
        if v not in valid_statuses:
            raise ValueError("Status must be one of: ok, warning, error")
        return v

    @model_validator(mode="after")
    def validate_timestamps(self) -> "SystemHealth":
        """Validate timestamp fields."""
        if self.next_check <= self.last_check:
            raise ValueError("next_check must be after last_check")
        return self


class ServiceStatus(UnifiBaseModel):
    """Service status information."""

    name: str = Field(description="Service name", min_length=1)
    status: str = Field(description="Service status (running, stopped, error)")
    enabled: bool = Field(description="Whether service is enabled")
    last_start: Optional[int] = Field(None, description="Last start timestamp", ge=0)
    last_stop: Optional[int] = Field(None, description="Last stop timestamp", ge=0)
    restart_count: Optional[int] = Field(None, description="Number of restarts", ge=0)
    pid: Optional[int] = Field(None, description="Process ID if running", ge=1)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate service status."""
        valid_statuses = {"running", "stopped", "error"}
        if v not in valid_statuses:
            raise ValueError("Status must be one of: running, stopped, error")
        return v


class SystemStatus(UnifiBaseModel):
    """Model representing the system status of a UniFi Network device."""

    device_type: DeviceType = Field(description="Device type")
    version: str = Field(description="Firmware version")
    uptime: int = Field(description="Uptime in seconds", ge=0)
    health: List[SystemHealth] = Field(description="System health status")
    processes: List[ProcessInfo] = Field(description="Running processes")
    services: List[ServiceStatus] = Field(description="Service status")
    upgradable: bool = Field(description="Whether device is upgradable")
    update_available: bool = Field(description="Whether update is available")
    update_version: Optional[str] = Field(None, description="Available update version")
    storage_usage: int = Field(description="Storage usage in bytes", ge=0)
    storage_available: int = Field(description="Available storage in bytes", ge=0)
    alerts: Optional[List[str]] = Field(None, description="System alerts")

    @field_validator("version", "update_version")
    @classmethod
    def validate_version(cls, v: Optional[str]) -> Optional[str]:
        """Validate version format."""
        if v is not None and not VERSION_PATTERN.match(v):
            raise ValueError("Version must be in format x.y.z")
        return v

    @field_validator("storage_usage")
    @classmethod
    def validate_storage_usage(cls, v: int) -> int:
        """Validate storage usage percentage."""
        if v < 0 or v > 100:
            raise ValueError("Input should be less than or equal to 100")
        return v

    def __init__(self, **data: Any) -> None:
        """Initialize the system status and log initialization details."""
        super().__init__(**data)
        logger.info(
            event="system_status_initialized",
            device_type=self.device_type,
            version=self.version,
            update_available=self.update_available,
            health_checks=len(self.health),
            processes=len(self.processes or []),
            services=len(self.services or []),
            alerts=self.alerts,
            storage_usage=self.storage_usage,
        )

    @field_validator("health")
    @classmethod
    def validate_health(cls, v: List[SystemHealth]) -> List[SystemHealth]:
        """Validate health field."""
        if not v:
            logger.error("system_health_validation_failed", error="empty_health_list")
            raise ValueError("List should have at least 1 item")
        logger.debug("system_health_validated", health_checks=len(v))
        return v

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Dump model to dict and log changes."""
        data = super().model_dump(**kwargs)
        logger.debug(
            "system_status_dumped",
            device_type=self.device_type,
            version=self.version,
            health_status=[h.status for h in self.health],
            service_status={s.name: s.status for s in self.services},
            storage_usage=self.storage_usage,
        )
        return data
