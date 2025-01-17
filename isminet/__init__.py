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

# Initialize logging with development mode based on environment variable
development_mode = os.getenv("ISMINET_DEV_MODE", "0").lower() in ("1", "true")
log_level = os.getenv("ISMINET_LOG_LEVEL", "INFO")

setup_logging(
    level=log_level,
    development_mode=development_mode,
)

# Log successful initialization
logger.info(
    "package_initialized",
    development_mode=development_mode,
    log_level=log_level,
    environment_variables={
        k: v for k, v in os.environ.items() if k.startswith("ISMINET_")
    },
)
