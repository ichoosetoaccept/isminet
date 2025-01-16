"""System status models for UniFi Network devices."""

from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, model_validator

from .base import (
    UnifiBaseModel,
    ValidationMixin,
    SystemStatsMixin,
    StatisticsMixin,
    TimestampMixin,
)
from .validators import validate_version
from .enums import DeviceType


class SystemHealth(ValidationMixin, SystemStatsMixin, UnifiBaseModel):
    """System health metrics."""

    subsystem: str = Field(description="Subsystem name")
    status: str = Field(description="Health status (ok, warning, error)")
    status_code: Optional[int] = Field(None, description="Status code")
    status_message: Optional[str] = Field(None, description="Status message")
    last_check: Optional[int] = Field(None, description="Last check timestamp")
    next_check: Optional[int] = Field(None, description="Next check timestamp")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate health status."""
        valid_statuses = {"ok", "warning", "error"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @model_validator(mode="after")
    def validate_timestamps(self) -> "SystemHealth":
        """Validate check timestamps."""
        if self.last_check is not None and self.next_check is not None:
            if self.last_check >= self.next_check:
                raise ValueError("next_check must be after last_check")
        return self


class ProcessInfo(ValidationMixin, UnifiBaseModel):
    """Process information."""

    pid: int = Field(description="Process ID", ge=1)
    name: str = Field(description="Process name")
    cpu_usage: float = Field(description="CPU usage percentage", ge=0, le=100)
    mem_usage: float = Field(description="Memory usage percentage", ge=0, le=100)
    mem_rss: Optional[int] = Field(None, description="Resident set size in bytes", ge=0)
    mem_vsz: Optional[int] = Field(
        None, description="Virtual memory size in bytes", ge=0
    )
    threads: Optional[int] = Field(None, description="Number of threads", ge=1)
    uptime: Optional[int] = Field(None, description="Process uptime in seconds", ge=0)


class ServiceStatus(ValidationMixin, UnifiBaseModel):
    """Service status information."""

    name: str = Field(description="Service name")
    status: str = Field(description="Service status (running, stopped, error)")
    enabled: bool = Field(description="Whether service is enabled")
    last_start: Optional[int] = Field(None, description="Last start timestamp")
    last_stop: Optional[int] = Field(None, description="Last stop timestamp")
    restart_count: Optional[int] = Field(None, description="Number of restarts", ge=0)
    pid: Optional[int] = Field(None, description="Process ID if running", ge=1)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate service status."""
        valid_statuses = {"running", "stopped", "error"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class SystemStatus(
    ValidationMixin, SystemStatsMixin, StatisticsMixin, TimestampMixin, UnifiBaseModel
):
    """System status for UniFi devices."""

    device_type: DeviceType = Field(description="Device type")
    version: str = Field(description="Firmware version")
    uptime: int = Field(description="System uptime in seconds", ge=0)
    health: List[SystemHealth] = Field(description="System health checks")
    processes: Optional[List[ProcessInfo]] = Field(
        None, description="Process information"
    )
    services: Optional[List[ServiceStatus]] = Field(None, description="Service status")
    alerts: Optional[List[Dict[str, Any]]] = Field(None, description="Active alerts")
    upgradable: Optional[bool] = Field(None, description="Whether upgrade is available")
    update_available: Optional[bool] = Field(
        None, description="Whether update is available"
    )
    update_version: Optional[str] = Field(None, description="Available update version")
    storage_usage: Optional[float] = Field(
        None, description="Storage usage percentage", ge=0, le=100
    )
    storage_available: Optional[int] = Field(
        None, description="Available storage in bytes", ge=0
    )

    _validate_version = field_validator("version", "update_version")(validate_version)
