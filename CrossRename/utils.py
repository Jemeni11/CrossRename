from urllib import request, error
import json


def parse_version(version: str):
    """Converts a version string (e.g., '1.2.3') into a tuple of integers (1, 2, 3)."""
    return tuple([int(part) for part in version.split(".")])


def check_for_update(current_version: str):
    """Checks if a new version of CrossRename is available on PyPI."""
    try:
        url = "https://pypi.org/pypi/CrossRename/json"
        with request.urlopen(url, timeout=5) as response:
            data = json.load(response)
            latest_version = data["info"]["version"]

        if parse_version(latest_version) > parse_version(current_version):
            print(f"Update available: v{latest_version}. You're on v{current_version}.")
            print(f"Run `pip install --upgrade CrossRename` to update.")
        else:
            print(f"You're on the latest version: v{current_version}.")

    except error.URLError as e:
        print(f"Unable to check for updates: {e}")
