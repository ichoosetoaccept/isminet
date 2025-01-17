"""isminet package initialization."""

import os
from .logging import setup_logging, get_logger

# Initialize logging with development mode based on environment variable
setup_logging(
    level=os.getenv("ISMINET_LOG_LEVEL", "INFO"),
    development_mode=os.getenv("ISMINET_DEV_MODE", "0").lower() in ("1", "true"),
)

# Create package-level logger
logger = get_logger(__name__)
