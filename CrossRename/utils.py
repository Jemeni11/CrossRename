from urllib import request, error
from packaging.version import parse
from json import load


def check_for_update(current_version: str):
    """Checks if a new version of CrossRename is available on PyPI."""
    try:
        url = "https://pypi.org/pypi/CrossRename/json"
        with request.urlopen(url, timeout=5) as response:
            data = load(response)
            latest_version = data["info"]["version"]

        if parse(latest_version) > parse(current_version):
            print(f"Update available: v{latest_version}. You're on v{current_version}.")
            print("Run `pip install --upgrade CrossRename` to update.")
        else:
            print(f"You're on the latest version: v{current_version}.")
            print("♥ Enjoying CrossRename? Check out `crossrename --credits`")

    except error.URLError as e:
        print(f"Unable to check for updates: {e}")
