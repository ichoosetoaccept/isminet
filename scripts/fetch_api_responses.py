"""Script to fetch and save example API responses."""

import json
import sys
from pathlib import Path

from isminet.clients.base import BaseAPIClient
from isminet.config import APIConfig

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def save_response(response: dict, filename: str) -> None:
    """Save API response to file."""
    docs_dir = project_root / "docs" / "api_responses"
    docs_dir.mkdir(parents=True, exist_ok=True)

    output_path = docs_dir / filename
    with open(output_path, "w") as f:
        json.dump(response, f, indent=4)
    print(f"Saved response to {output_path}")


def main():
    """Fetch and save API responses."""
    config = APIConfig()  # This will load from .env

    with BaseAPIClient(config) as client:
        # First get sites to find our site name
        sites_response = client.get("self/sites")
        site_name = sites_response["data"][0]["name"]  # Use first site
        print(f"Using site: {site_name}")

        # Get device info for first device
        devices_response = client.get(f"s/{site_name}/stat/device")
        save_response(devices_response, "device_response.json")

        # Get client info
        clients_response = client.get(f"s/{site_name}/stat/sta")
        save_response(clients_response, "client_response.json")

        # Get version info (we already have self_response.json but let's verify)
        version_response = client.get(f"s/{site_name}/self")
        save_response(version_response, "version_response.json")
        print("Saved version response")


if __name__ == "__main__":
    main()
