"""isminet package initialization."""

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

# Initialize logging using centralized settings
setup_logging()

# Log successful initialization
logger.info(
    "package_initialized",
)
