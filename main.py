from __future__ import annotations

import argparse

import sys
from typing import Iterable
from dotfiles.path import DotFiles
from dotfiles.package_manager import PackageManager
from dotfiles.setup import install_path, uninstall_path


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="dotfiles utility")
    # Flags for install/uninstall dotfiles $PATH environment
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--install", action="store_true", help="Install: add ./bin to PATH in your shell profile(s)")
    group.add_argument("--uninstall", action="store_true",
                       help="Uninstall: remove the PATH block from your shell profile(s)")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command")

    # search subcommand
    search_parser = subparsers.add_parser("search", help="Search available packages")
    search_parser.add_argument("pattern", metavar="PATTERN", help="Search available packages matching PATTERN")

    # install subcommand
    install_parser = subparsers.add_parser("install", help="Install a package by name")
    install_parser.add_argument("package_name", metavar="NAME", help="Name of the package to install")

    # uninstall subcommand
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a package by name")
    uninstall_parser.add_argument("package_name", metavar="NAME", help="Name of the package to uninstall")

    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.install:
        install_path(DotFiles.get_bin_dir())
        return
    if args.uninstall:
        uninstall_path()
        return
    if getattr(args, "command", None) == "search":
        PackageManager().search(args.pattern)
        return
    if getattr(args, "command", None) == "install":
        PackageManager().install(args.package_name)
        return
    if getattr(args, "command", None) == "uninstall":
        PackageManager().uninstall(args.package_name)
        return
    # Default behavior
    print(
        "Hello from dotfiles! Usage: dotfiles search PATTERN | install NAME | uninstall NAME | --install | --uninstall")


if __name__ == "__main__":
    main()
