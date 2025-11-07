from dotfiles.package import PackageAPI, PackageInfo, QuickInstallPackage, QuickUninstallPackage
import platform

VERSION = "0.45.0"
URL = "https://github.com/sigoden/dufs/releases/download/v{version}/dufs-v{version}-{arch}-unknown-linux-{libc}.tar.gz"


def _get_arch() -> str:
    """
    Get the current system architecture.

    Returns:
        str: One of: aarch64, arm, armv7, i686, x86_64

    Raises:
        RuntimeError: If architecture cannot be determined or is not supported
    """
    machine = platform.machine().lower()

    if machine in ['x86_64', 'amd64']:
        return 'x86_64'
    elif machine == 'aarch64':
        return 'aarch64'
    elif machine.startswith('armv7'):
        return 'armv7'
    elif machine == 'arm':
        return 'arm'
    elif machine in ['i686', 'i386']:
        return 'i686'

    raise RuntimeError(f"Unsupported architecture: {machine}")


class DufsPackage(PackageAPI):
    def __init__(self):
        super().__init__()
        self.arch = _get_arch()
        self.libc = {
            "aarch64": "musl",
            "arm": "musleabihf",
            "armv7": "musleabihf",
            "i686": "musl",
            "x86_64": "musl",
        }

    def info(self) -> PackageInfo:
        return PackageInfo(
            name="dufs",
            out=["dufs"],
            version=VERSION,
        )

    def install(self) -> None:
        url = URL.format(version=VERSION, arch=self.arch, libc=self.libc[self.arch])
        QuickInstallPackage(url=url, name='dufs', symbol={'dufs': 'dufs'}).install()

    def uninstall(self) -> None:
        QuickUninstallPackage(name='dufs', symbol=['dufs']).uninstall()
