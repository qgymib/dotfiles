import platform

from dotfiles.package import PackageAPI, PackageInfo, QuickInstallPackage, QuickUninstallPackage

VERSION = "0.26.0"
URL = "https://github.com/sharkdp/bat/releases/download/v{version}/bat-v{version}-{arch}-unknown-linux-{libc}.tar.gz"


def _get_arch() -> str:
    """
    Get the current system architecture.

    Returns:
        str: One of: aarch64, arm, i686, x86_64

    Raises:
        RuntimeError: If architecture cannot be determined or is not supported
    """
    machine = platform.machine().lower()

    if machine in ['x86_64', 'amd64']:
        return 'x86_64'
    elif machine == 'aarch64':
        return 'aarch64'
    elif machine == 'arm':
        return 'arm'
    elif machine in ['i686', 'i386']:
        return 'i686'

    raise RuntimeError(f"Unsupported architecture: {machine}")


class BatPackage(PackageAPI):
    def __init__(self):
        super().__init__()
        self.arch = _get_arch()
        self.libc = {
            "aarch64": "musl",
            "arm": "gnueabihf",
            "i686": "musl",
            "x86_64": "musl",
        }

    def info(self) -> PackageInfo:
        return PackageInfo(
            name="bat",
            out=["bat"],
            version=VERSION,
        )

    def install(self) -> None:
        url = URL.format(version=VERSION, arch=self.arch, libc=self.libc[self.arch])
        QuickInstallPackage(url=url, name='bat', symbol={'bat': 'bat'}).install()

    def uninstall(self) -> None:
        QuickUninstallPackage(name='bat', symbol=['bat']).uninstall()
