"""
REST API Public Fetch
Asynchronously GETs public car part (vehicle variable) data from the
NHTSA vPIC REST API, manages a loading state and errors, and displays only
the items that match a JSON filter object.

Run:  python rest_api_public_fetch.py
Uses only the Python standard library (no installs needed).
"""

from __future__ import annotations

import asyncio
import json
import re
import urllib.error
import urllib.parse
import urllib.request

# REST endpoint and query parameters
BASE_URI = "https://vpic.nhtsa.dot.gov/api/vehicles/GetVehicleVariableList"
QUERY_PARAMS = {"format": "json"}
API_URI = f"{BASE_URI}?{urllib.parse.urlencode(QUERY_PARAMS)}"

# JSON filter object: only items matching ALL of these key/value pairs are shown
FILTER = {
    "GroupName": "Active Safety System"
}


def http_get(uri: str) -> dict:
    """Blocking GET request that returns parsed JSON."""
    request = urllib.request.Request(uri, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP error! Status: {response.status}")
        return json.loads(response.read().decode("utf-8"))


async def show_loading(stop_event: asyncio.Event) -> None:
    """Loading state: animated message while the request is in progress."""
    frames = ["|", "/", "-", "\\"]
    i = 0
    while not stop_event.is_set():
        print(f"\rLoading data... {frames[i % len(frames)]}", end="", flush=True)
        i += 1
        await asyncio.sleep(0.1)
    print("\r" + " " * 30 + "\r", end="")


async def fetch_data(uri: str) -> dict:
    """Asynchronously fetch data while showing a loading indicator."""
    stop_event = asyncio.Event()
    loader = asyncio.create_task(show_loading(stop_event))
    try:
        # Run the blocking GET in a background thread so the loader keeps running
        return await asyncio.to_thread(http_get, uri)
    finally:
        stop_event.set()
        await loader


def matches_filter(item: dict, filter_obj: dict) -> bool:
    """True when the item matches every key/value in the filter object."""
    return all(item.get(key) == value for key, value in filter_obj.items())


def to_plain_text(html: str | None) -> str:
    """Some descriptions contain HTML; strip the tags."""
    if not html:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def display_data(items: list[dict], total: int) -> None:
    """Print the filtered items as a simple table."""
    print(f'Showing {len(items)} of {total} items where GroupName = "{FILTER["GroupName"]}"\n')
    print(f"{'ID':<6}{'Name':<62}{'Data Type'}")
    print("-" * 82)
    for item in items:
        print(f"{item.get('ID', ''):<6}{item.get('Name', ''):<62}{item.get('DataType', '')}")
        description = to_plain_text(item.get("Description"))
        if description:
            print(f"      {description[:150]}{'...' if len(description) > 150 else ''}")
        print()


async def main() -> None:
    try:
        data = await fetch_data(API_URI)

        results = data.get("Results")
        if not isinstance(results, list):
            raise ValueError("Unexpected response format from the API.")

        filtered = [item for item in results if matches_filter(item, FILTER)]
        if not filtered:
            print("No items matched the filter.")
            return

        display_data(filtered, data.get("Count", len(results)))

    except urllib.error.HTTPError as error:
        print(f"Error loading data: HTTP {error.code} {error.reason}")
    except urllib.error.URLError as error:
        print(f"Error loading data: network problem ({error.reason})")
    except json.JSONDecodeError:
        print("Error loading data: response was not valid JSON.")
    except Exception as error:
        print(f"Error loading data: {error}")


if __name__ == "__main__":
    asyncio.run(main())
