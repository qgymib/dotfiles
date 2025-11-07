from dotfiles import DotFiles
from dotfiles.package import PackageAPI, PackageInfo

STARTUP_SCRIPT = [
    "#!/bin/bash",
    "python3 {dotfiles_startup_path} \"$@\""
    ""
]
STARTUP_FILE = "dotfiles"


class DotfilesPackage(PackageAPI):
    def __init__(self):
        super().__init__()

    def info(self) -> PackageInfo:
        return PackageInfo(
            name="dotfiles",
            out=[STARTUP_FILE],
            version="0.0.1",
        )

    def install(self) -> None:
        main_path = DotFiles.get_root_dir() / "main.py"

        lines = "\n".join(STARTUP_SCRIPT)
        script = lines.format(dotfiles_startup_path=main_path)

        startup_file = DotFiles.get_bin_dir() / STARTUP_FILE
        if startup_file.exists():
            startup_file.unlink()

        # Create the startup script and make it executable
        startup_file.write_text(script, encoding="utf-8")
        startup_file.chmod(0o755)

    def uninstall(self) -> None:
        startup_file = DotFiles.get_bin_dir() / STARTUP_FILE
        if startup_file.exists():
            startup_file.unlink()
