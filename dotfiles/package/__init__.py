import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
import tarfile
import lzma
import pathlib
from dataclasses import dataclass

from dotfiles import DotFiles


@dataclass
class PackageInfo:
    """
    The name of this application.
    """
    name: str

    """
    The list of file name installed in the bin directory.
    """
    out: list[str]

    """Application version."""
    version: str


class PackageAPI:
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super.__init_subclass__()
        PackageAPI.registry[cls.__name__] = cls

    def __init__(self):
        pass

    def info(self) -> PackageInfo:
        """
        Retrieve information about a specific package.

        Provides concise details about a package, including its name and output
        information. Used to encapsulate and return package-related metadata.

        :return: An instance containing package metadata.
        :rtype: PackageInfo
        """
        return PackageInfo(
            name="dotfiles",
            out=[],
            version="",
        )

    def install(self) -> None:
        """
        Install application. If the application is already installed, update it.
        """
        pass

    def uninstall(self) -> None:
        """
        Uninstall application.
        """
        pass


class QuickInstallPackage:
    supported_extensions = ['.tar.gz', '.tgz', '.tar.xz', '.txz', '.zip']

    def __init__(self, url: str, name: str, symbol: dict[str, str]):
        self.url = url
        self.name = name
        self.symbol = symbol
        self.install_dir = DotFiles.get_app_dir() / name

    def install(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=self.get_extension()) as temp_file:
            opener = urllib.request.build_opener()
            if "http_proxy" in os.environ:
                opener.add_handler(urllib.request.ProxyHandler({
                    "http": os.environ["http_proxy"],
                    "https": os.environ.get("https_proxy", os.environ["http_proxy"])
                }))
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(self.url, temp_file.name)

            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)

            QuickInstallPackage._uncompress(temp_file.name, DotFiles.get_app_dir(), self.name)

            bin_dir = DotFiles.get_bin_dir()
            for src, dst in self.symbol.items():
                src_path = self.install_dir / src
                dst_path = bin_dir / dst
                if dst_path.exists():
                    dst_path.unlink()
                dst_path.symlink_to(src_path)

    @staticmethod
    def _uncompress(file: str, out: pathlib.Path, name: str) -> None:
        """Extract compressed file to output directory with automatic subfolder detection.

        Args:
            file: Path to compressed file
            out: Output directory path
            name: Name for the target directory

        Raises:
            ValueError: If the compressed file is empty
        """
        out_path = out
        temp_dir = pathlib.Path(tempfile.mkdtemp())

        try:
            # Extract based on file extension
            if file.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(file, 'r:gz') as tar:
                    tar.extractall(temp_dir)
            elif file.endswith(('.tar.xz', '.txz')):
                with lzma.open(file) as xz:
                    with tarfile.open(fileobj=xz) as tar:
                        tar.extractall(temp_dir)
            elif file.endswith('.zip'):
                with zipfile.ZipFile(file) as zip_file:
                    zip_file.extractall(temp_dir)

            # Get contents of the temp directory
            contents = list(temp_dir.iterdir())
            if not contents:
                raise ValueError("Compressed file is empty")

            # Clear the target directory if it doesn't exist
            target_dir = out_path / name
            if target_dir.exists():
                shutil.rmtree(target_dir)

            if len(contents) == 1 and contents[0].is_dir():
                # Single directory - rename it
                shutil.move(str(contents[0]), target_dir)
            else:
                target_dir.mkdir(parents=True)
                # Multiple items - move all to the new directory
                for item in contents:
                    shutil.move(str(item), target_dir)
        finally:
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def get_extension(self) -> str:
        """
        Get the file extension from URL.

        Returns:
            str: The file extension including dot(s)

        Raises:
            ValueError: If the URL has an unsupported extension
        """
        for ext in self.supported_extensions:
            if self.url.endswith(ext):
                return ext
        raise ValueError(f"Unsupported compression format for URL: {self.url}")


class QuickUninstallPackage:
    def __init__(self, name: str, symbol: list[str]):
        self.name = name
        self.symbol = symbol
        self.install_dir = DotFiles.get_app_dir() / name

    def uninstall(self) -> None:
        bin_dir = DotFiles.get_bin_dir()
        for item in self.symbol:
            symbol_link = bin_dir / item
            if symbol_link.exists() or symbol_link.is_symlink():
                symbol_link.unlink()

        if self.install_dir.exists():
            shutil.rmtree(self.install_dir)


class Manager:
    def __init__(self):
        self.packages = {}
        self._discover_packages()
        instance = [cls() for cls in PackageAPI.registry.values()]
        for i in instance:
            info = i.info()
            self.packages[info.name.lower()] = i
        pass

    def _discover_packages(self):
        import importlib
        package_dir = pathlib.Path(__file__).resolve().parent

        for file in package_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            module_name = f"dotfiles.package.{file.stem}"
            importlib.import_module(module_name)

    def install(self, package_name: str) -> None:
        name = package_name.lower()
        if name in self.packages:
            print(f"Installing package {name}")
            self.packages[name].install()
            print(f"Package `{name}` installed")
        else:
            print(f"Package `{name}` not found")
            sys.exit(1)

    def uninstall(self, package_name: str) -> None:
        name = package_name.lower()
        if name in self.packages:
            print(f"Uninstalling package `{name}`")
            self.packages[name].uninstall()
            print(f"Package `{name}` uninstalled")
        else:
            print(f"Package `{name}` not found")
            sys.exit(1)

    def search(self, pattern: str) -> None:
        for name, instance in self.packages.items():
            if pattern in name:
                print(f"{name}: {instance.info().version}")
