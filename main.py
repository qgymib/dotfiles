from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, List
from dotfiles import DotFiles
from dotfiles.package import Manager

MARK_START = "# >>> dotfiles PATH >>>"
MARK_END = "# <<< dotfiles PATH <<<"

def get_candidate_profile_files() -> List[Path]:
    """Return a prioritized list of shell profile files to edit on Linux.

    We try shell-specific files if present, and fall back to the more generic profile.
    """
    home = Path.home()
    candidates = [
        home / ".bashrc",
        home / ".zshrc",
    ]
    # Keep only unique paths preserving order
    seen = set()
    result: List[Path] = []
    for p in candidates:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


def build_export_block(bin_dir: Path) -> str:
    bin_posix = bin_dir.as_posix()
    lines = [
        "",
        MARK_START,
        f'# Added by "dotfiles" on install. Do not edit between markers.',
        f'export PATH="{bin_posix}:$PATH"',
        MARK_END,
        "",
    ]
    return "\n".join(lines)


def remove_marked_block(text: str) -> str:
    """Remove our managed PATH block from the given profile text, if present."""
    if MARK_START not in text:
        return text
    out_lines: List[str] = []
    in_block = False
    for line in text.splitlines():
        if line.strip() == MARK_START:
            in_block = True
            continue
        if in_block and line.strip() == MARK_END:
            in_block = False
            continue
        if not in_block:
            out_lines.append(line)
    # Ensure trailing newline
    return "\n".join(out_lines).rstrip("\n") + "\n"


def install_path(bin_dir: Path) -> None:
    """Install by adding the project's bin directory to PATH in shell profiles."""

    block = build_export_block(bin_dir)
    updated_any = False
    created_in: List[Path] = []

    for profile in get_candidate_profile_files():
        try:
            if profile.exists():
                original = profile.read_text(encoding="utf-8")
                without = remove_marked_block(original)
                new_text = without
                if block.strip() not in without:
                    new_text = without.rstrip("\n") + "\n" + block
                if new_text != original:
                    profile.write_text(new_text, encoding="utf-8")
                    updated_any = True
                print(f"[dotfiles] Updated {profile}")
        except OSError as e:
            print(f"[dotfiles] Warning: Could not update {profile}: {e}", file=sys.stderr)

    # Update current process PATH so immediate child processes can use it
    current_path = os.environ.get("PATH", "")
    bin_posix = bin_dir.as_posix()
    if bin_posix not in current_path.split(":"):
        os.environ["PATH"] = f"{bin_posix}:{current_path}" if current_path else bin_posix

    if updated_any:
        print(f"[dotfiles] Installed: added {bin_posix} to PATH in your shell profile(s).")
        if created_in:
            created_list = ", ".join(str(p) for p in created_in)
            print(f"[dotfiles] Created profile file(s): {created_list}")
        print("[dotfiles] To apply now, run: source ~/.bashrc (or ~/.zshrc), or open a new terminal.")
    else:
        print("[dotfiles] Already installed: PATH block already present.")


def uninstall_path() -> None:
    """Uninstall by removing our PATH block from known profiles."""
    removed_any = False
    for profile in get_candidate_profile_files():
        if not profile.exists():
            continue
        try:
            original = profile.read_text(encoding="utf-8")
            new_text = remove_marked_block(original)
            if new_text != original:
                profile.write_text(new_text, encoding="utf-8")
                removed_any = True
            print(f"[dotfiles] Uninstalled PATH block from {profile}")
        except OSError as e:
            print(f"[dotfiles] Warning: Could not modify {profile}: {e}", file=sys.stderr)

    if removed_any:
        print("[dotfiles] Uninstalled: removed PATH block from shell profile(s).")
        print("[dotfiles] Open a new terminal or run: source ~/.bashrc (or ~/.zshrc) to apply.")
    else:
        print("[dotfiles] Nothing to uninstall: no PATH block found in known profiles.")


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
        Manager().search(args.pattern)
        return
    # Default behavior
    print("Hello from dotfiles! Usage: ./main.py search PATTERN | --install | --uninstall")


if __name__ == "__main__":
    main()
