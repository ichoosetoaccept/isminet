# test_api.py
import os
from dotenv import load_dotenv
import requests

def make_request(session: requests.Session, host: str, endpoint: str) -> None:
    """Make a request to the UniFi API and print response."""
    url = f"https://{host}/proxy/network/api/{endpoint}"
    print(f"\nTrying endpoint: {url}")

    try:
        response = session.get(url, verify=False)
        response.raise_for_status()
        data = response.json()
        print("Success! Response:")
        print(data)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e, "response"):
            print(f"Status code: {e.response.status_code}")
            print("Response:", e.response.text)

def main():
    # Load environment variables
    load_dotenv()

    # Get configuration
    api_key = os.getenv("UNIFI_API_KEY")
    host = os.getenv("UNIFI_HOST", "192.168.1.1")

    if not api_key:
        print("ERROR: UNIFI_API_KEY not found in .env file")
        return

    # Setup basic session
    session = requests.Session()
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    })

    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Test different endpoints
    endpoints = [
        "s/default/self",  # Get self info
        "self/sites",      # List sites
    ]

    for endpoint in endpoints:
        make_request(session, host, endpoint)

if __name__ == "__main__":
    main()
