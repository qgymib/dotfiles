import json
import pathlib
import platform

from dotfiles.package import QuickInstallPackage, QuickUninstallPackage
from dotfiles.path import DotFiles


def _load_json_files(path: pathlib.Path, arch: str) -> dict[str, dict]:
    result = {}
    for json_file in path.glob("*.json"):
        key = json_file.stem
        with open(json_file, 'r') as f:
            data = json.load(f)
            # Check if the current architecture is available
            if ("architecture" not in data) or not isinstance(data["architecture"], dict):
                continue
            if arch not in data["architecture"] or not isinstance(data["architecture"][arch], dict):
                continue
            result[key] = data
    return result


def _get_arch() -> str:
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    if machine in ("arm64", "aarch64"):
        return "aarch64"
    if machine.startswith("arm"):
        return "arm"
    raise RuntimeError(f"Unsupported architecture: {machine}")


class PackageManager:
    def __init__(self):
        package_path = DotFiles.get_root_dir() / "dotfiles" / "package"
        self.arch = _get_arch()
        self.json_data = _load_json_files(package_path, self.arch)

    def search(self, pattern: str) -> None:
        pattern_lower = pattern.lower()
        for name, instance in self.json_data.items():
            if pattern_lower in name.lower():
                print(f"{name}: {instance['version']}")

    def install(self, package_name: str) -> None:
        if package_name in self.json_data:
            self._install_package(package_name, self.json_data[package_name])
            print(f"Package `{package_name}` installed")
        else:
            print(f"Package `{package_name}` not found")

    def uninstall(self, package_name: str) -> None:
        if package_name in self.json_data:
            self._uninstall_package(package_name, self.json_data[package_name])
            print(f"Package `{package_name}` uninstalled")
        else:
            print(f"Package `{package_name}` not found")

    def _install_package(self, name: str, package: dict) -> None:
        arch = package["architecture"][self.arch]
        url = arch["url"]
        if "sha256" in arch:
            sha256 = arch["sha256"]
        else:
            sha256 = None
        symbol = package["bin"]
        if not isinstance(url, str) or not isinstance(symbol, dict):
            raise RuntimeError(f"Invalid package data: {package}")
        QuickInstallPackage(url=url, name=name, sha256=sha256, symbol=symbol).install()

    def _uninstall_package(self, name: str, package: dict) -> None:
        bins = list(package["bin"].keys())
        QuickUninstallPackage(name=name, symbol=bins).uninstall()
        pass
