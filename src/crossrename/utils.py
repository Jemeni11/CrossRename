from json import load
from typing import Any
from urllib import error, request

from packaging.version import parse


def check_for_update(current_version: str):
    """Checks if a new version of CrossRename is available on PyPI."""
    try:
        url = "https://pypi.org/pypi/CrossRename/json"
        with request.urlopen(url, timeout=5) as response:
            data: Any = load(fp=response)
            latest_version: Any = data["info"]["version"]

        if parse(latest_version) > parse(current_version):
            print(f"Update available: v{latest_version}. You're on v{current_version}.")
            print("Run `pip install --upgrade CrossRename` to update.")
        else:
            print(f"You're on the latest version: v{current_version}.")
            print(
                "Enjoying CrossRename? Have feedback? Send it here: https://tally.so/r/7Rjpgz?project=CrossRename"
            )

    except error.URLError as e:
        print(f"Unable to check for updates: {e}")
