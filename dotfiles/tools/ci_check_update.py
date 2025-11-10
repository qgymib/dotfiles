import pathlib
import json
import re
import urllib.request
import hashlib

PACKAGE_PATH = pathlib.Path(__file__).resolve().parent.parent / "package"


def _get_version(url: str, pattern: str) -> str:
    """Get version from URL using regex pattern.

    Args:
        url: URL to fetch content from
        pattern: Regex pattern with one capture group

    Returns:
        Captured version string

    Raises:
        Exception: If regex pattern doesn't match or request fails
    """
    with urllib.request.urlopen(url) as response:
        content = response.read().decode('utf-8')
        match = re.search(pattern, content)
        if not match:
            raise Exception(f"No version match found for pattern: {pattern}")
        return match.group(1)


def _get_hash256(url: str) -> str:
    """Get SHA-256 hash of file from URL.

    Args:
        url: URL to download file from

    Returns:
        SHA-256 hash string of downloaded file

    Raises:
        Exception: If download or hash calculation fails
    """
    sha256_hash = hashlib.sha256()
    with urllib.request.urlopen(url) as response:
        while True:
            data = response.read(8192)  # Read in 8KB chunks
            if not data:
                break
            sha256_hash.update(data)
    return sha256_hash.hexdigest()


def _check_architecture(config: dict, arch: str) -> bool:
    if ("update" not in config) or not isinstance(config["update"], dict):
        return False
    if ("architecture" not in config["update"]) or not isinstance(config["update"]["architecture"], dict):
        return False
    if (arch not in config["update"]["architecture"]) or not isinstance(config["update"]["architecture"][arch], dict):
        return False
    return True

def _update_new_url_sha256(config:dict, arch: str, version: str):
    url = config["update"]["architecture"][arch]["url"].format(version=version)
    print(f"Downloading {url} for {arch} architecture")
    config["architecture"][arch]["url"] = url
    sha256 = _get_hash256(url)
    config["architecture"][arch]["sha256"] = sha256
    print(f"sha256({url})={sha256}")

def _update_package_config(path: pathlib.Path) -> bool:
    # Load configuration
    config = json.loads(path.read_text())
    if config["update"] is None or config["update"]["check"] is None:
        return False
    if config["update"]["check"]["url"] is None or config["update"]["check"]["regex"] is None:
        return False
    if config["update"]["architecture"] is None:
        return False
    # Check for new version
    print(f"Checking for update for {path.stem}")
    new_version = _get_version(config["update"]["check"]["url"], config["update"]["check"]["regex"])
    if new_version == config["version"]:
        return False
    # Update configuration
    print(f"Updating {path.stem} to version {new_version}")
    config["version"] = new_version
    if _check_architecture(config, "x86_64"):
        _update_new_url_sha256(config, "x86_64", new_version)
    if _check_architecture(config, "i686"):
        _update_new_url_sha256(config, "i686", new_version)
    if _check_architecture(config, "aarch64"):
        _update_new_url_sha256(config, "aarch64", new_version)
    if _check_architecture(config, "arm"):
        _update_new_url_sha256(config, "arm", new_version)
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)
    return True


def update_all():
    for json_file in PACKAGE_PATH.glob("*.json"):
        if _update_package_config(json_file):
            print(f"Updated {json_file}")
        else:
            print(f"No update needed for {json_file}")


def update_package(pattern: str):
    pattern_lower = pattern.lower()
    for json_file in PACKAGE_PATH.glob("*.json"):
        if pattern_lower in json_file.stem.lower():
            if _update_package_config(json_file):
                print(f"Updated {json_file}")
            else:
                print(f"No update needed for {json_file}")
            return


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Update package versions')
    parser.add_argument('packages', nargs='*', help='package names to update (updates all if none specified)')
    args = parser.parse_args()

    if not args.packages:
        update_all()
    else:
        for package in args.packages:
            update_package(package)
