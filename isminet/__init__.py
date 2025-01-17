"""isminet package initialization."""

import os
import sys
from pathlib import Path
from .logging import setup_logging, get_logger

# Create package-level logger
logger = get_logger(__name__)

# Log package initialization
logger.info(
    "package_initializing",
    package_name="isminet",
    python_version=sys.version,
    platform=sys.platform,
    workspace_path=str(Path(__file__).parent.parent),
)

# Initialize logging with environment variables
development_mode = os.getenv("ISMINET_DEV_MODE", "0").lower() in ("1", "true")
log_level = os.getenv("ISMINET_LOG_LEVEL", "INFO")
log_to_file = os.getenv("ISMINET_LOG_TO_FILE", "1").lower() in ("1", "true")

setup_logging(
    level=log_level,
    development_mode=development_mode,
    log_to_file=log_to_file,
)

# Log successful initialization
logger.info(
    "package_initialized",
    development_mode=development_mode,
    log_level=log_level,
    environment_variables=dict(
        ISMINET_DEV_MODE=os.getenv("ISMINET_DEV_MODE"),
        ISMINET_LOG_LEVEL=os.getenv("ISMINET_LOG_LEVEL"),
        ISMINET_LOG_TO_FILE=os.getenv("ISMINET_LOG_TO_FILE"),
    ),
)
