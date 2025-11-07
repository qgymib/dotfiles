import platform

from dotfiles.package import PackageAPI, PackageInfo, QuickInstallPackage, QuickUninstallPackage

_VERSION = "0.66.1"
_URL = "https://github.com/junegunn/fzf/releases/download/v{version}/fzf-{version}-linux_{arch}.tar.gz"


def _get_arch() -> str:
    """
    Get the current system architecture.

    Returns:
        str: One of: amd64, armv5, armv6, armv7, loong64, ppc64le, s390x

    Raises:
        RuntimeError: If architecture cannot be determined or is not supported
    """
    machine = platform.machine().lower()

    if machine in ['x86_64', 'amd64']:
        return 'amd64'
    elif machine == 'aarch64':
        return 'arm64'
    elif machine.startswith('armv7'):
        return 'armv7'
    elif machine.startswith('armv6'):
        return 'armv6'
    elif machine.startswith('armv5'):
        return 'armv5'
    elif machine == 'loong64':
        return 'loong64'
    elif machine == 'ppc64le':
        return 'ppc64le'
    elif machine == 's390x':
        return 's390x'

    raise RuntimeError(f"Unsupported architecture: {machine}")


class FzfPackage(PackageAPI):
    def __init__(self):
        super().__init__()
        self.arch = _get_arch()

    def info(self) -> PackageInfo:
        return PackageInfo(
            name="fzf",
            out=["fzf"],
            version=_VERSION,
        )

    def install(self) -> None:
        url = _URL.format(version=_VERSION, arch=self.arch)
        QuickInstallPackage(url=url, name="fzf", symbol={'fzf': 'fzf'}).install()

    def uninstall(self) -> None:
        QuickUninstallPackage(name="fzf", symbol=['fzf']).uninstall()
