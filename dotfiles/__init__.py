import pathlib


class DotFiles:
    @staticmethod
    def get_bin_dir() -> pathlib.Path:
        """Return the absolute path to this project's bin directory."""
        return pathlib.Path(__file__).resolve().parent.parent / "bin"

    @staticmethod
    def get_app_dir() -> pathlib.Path:
        """Return the absolute path to this project's apps directory."""
        return DotFiles.get_bin_dir() / "apps"
