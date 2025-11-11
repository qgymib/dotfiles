import pathlib


class DotFiles:
    @staticmethod
    def get_root_dir() -> pathlib.Path:
        """Return the absolute path to this project's root directory."""
        return pathlib.Path(__file__).resolve().parent.parent

    @staticmethod
    def get_bin_dir() -> pathlib.Path:
        """Return the absolute path to this project's bin directory."""
        return DotFiles.get_root_dir() / "bin"

    @staticmethod
    def get_app_dir() -> pathlib.Path:
        """Return the absolute path to this project's apps directory."""
        return DotFiles.get_root_dir() / "apps"
