import platform

from dotfiles.package import PackageAPI, PackageInfo, QuickInstallPackage, QuickUninstallPackage

VERSION = "0.11.5"
NAME = "neovim"
URL = "https://github.com/neovim/neovim/releases/download/v{version}/nvim-linux-{arch}.tar.gz"


def get_arch() -> str:
    """Return the current platform architecture (arm64 or x86_64)."""
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    if machine in ("arm64", "aarch64"):
        return "arm64"
    raise RuntimeError(f"Unsupported architecture: {machine}")


class NeovimPackage(PackageAPI):
    def __init__(self):
        super().__init__()

    def info(self) -> PackageInfo:
        return PackageInfo(
            name=NAME,
            out=["nvim"],
            version=VERSION,
        )

    def install(self) -> None:
        url = URL.format(version=VERSION, arch=get_arch())
        QuickInstallPackage(url=url, name=NAME, symbol={'bin/nvim': 'nvim'}).install()

    def uninstall(self) -> None:
        QuickUninstallPackage(name=NAME, symbol=['nvim']).uninstall()
