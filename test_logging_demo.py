from isminet.logging import setup_logging, get_logger
from isminet.models.system import SystemHealth, DeviceType

# Setup logging with file output enabled
setup_logging(level="DEBUG", development_mode=True, log_to_file=True)

# Get a logger for this script
logger = get_logger(__name__)

# Demonstrate different log levels
logger.debug("This is a DEBUG message - Very detailed info for debugging")
logger.info("This is an INFO message - General operational info")
logger.warning("This is a WARNING message - Something unexpected")
logger.error("This is an ERROR message - Something failed")
logger.critical("This is a CRITICAL message - Severe error!")

# Create a system health instance to generate some logs
health = SystemHealth(
    device_type=DeviceType.UAP,
    subsystem="test",
    status="ok",
    status_code=0,
    status_message="Test message",
    last_check=1000,
    next_check=2000,
)

# Try an invalid one to see error logging
try:
    SystemHealth(
        device_type=DeviceType.UAP,
        subsystem="test",
        status="invalid_status",  # This will cause a validation error
        status_code=0,
        status_message="Test message",
        last_check=1000,
        next_check=2000,
    )
except Exception as e:
    logger.error("Validation failed", error=str(e))
