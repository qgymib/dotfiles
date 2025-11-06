from dotfiles.package import PackageAPI, PackageInfo, QuickInstallPackage, QuickUninstallPackage
import platform

VERSION = "15.1.0"
URL = "https://github.com/BurntSushi/ripgrep/releases/download/${version}/ripgrep-${version}-${arch}-unknown-linux-${libc}.tar.gz"


def get_arch() -> str:
    """
    Get the current system architecture.

    Returns:
        str: One of: aarch64, armv7, i686, s390x, x86_64

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
    elif machine in ['i686', 'i386']:
        return 'i686'
    elif machine == 's390x':
        return 's390x'

    raise RuntimeError(f"Unsupported architecture: {machine}")


class RipgrepPackage(PackageAPI):
    def __init__(self):
        super().__init__()
        self.arch = get_arch()
        self.libc = {
            "aarch64": "gnu",
            "armv7": "musleabihf",
            "i686": "gnu",
            "s390x": "gnu",
            "x86_64": "musl",
        }

    def info(self) -> PackageInfo:
        return PackageInfo(
            name="ripgrep",
            out=["rg"],
            version=VERSION,
        )

    def install(self) -> None:
        url = URL.format(version=VERSION, arch=self.arch, libc=self.libc[self.arch])
        QuickInstallPackage(url=url, name='ripgrep', symbol={'rg': 'rg'}).install()

    def uninstall(self) -> None:
        QuickUninstallPackage(name='ripgrep', symbol=['rg']).uninstall()
