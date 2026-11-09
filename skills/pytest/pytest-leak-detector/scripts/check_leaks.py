"""Find likely test-artifact files and optionally remove explicitly approved paths."""
import argparse
from pathlib import Path

SUSPICIOUS_EXTENSIONS = {".db", ".sqlite", ".log", ".tmp"}
SUSPICIOUS_PREFIXES = {"temp_", "test_out_", "dump_"}

IGNORE_DIRS = {
    ".git", ".venv", "venv", "__pycache__",
    ".pytest_cache", "node_modules", ".idea", ".vscode"
}


def find_leaks(root_dir: Path) -> list[Path]:
    root_dir = root_dir.resolve()
    leaks = []
    for path in root_dir.rglob("*"):
        relative_path = path.relative_to(root_dir)
        if any(part in IGNORE_DIRS for part in relative_path.parts):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        if (path.suffix.lower() in SUSPICIOUS_EXTENSIONS
                or any(path.name.startswith(prefix) for prefix in SUSPICIOUS_PREFIXES)):
            leaks.append(relative_path)
    return sorted(leaks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                        help="workspace to scan (default: current directory)")
    parser.add_argument("--clean", action="store_true",
                        help="remove only files explicitly listed with --path")
    parser.add_argument("--path", action="append", default=[], metavar="FILE",
                        help="relative path of a detected file approved for removal; repeat as needed")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        parser.error(f"workspace is not a directory: {workspace}")
    if args.clean and not args.path:
        parser.error("--clean requires at least one approved --path")
    if args.path and not args.clean:
        parser.error("--path can only be used with --clean")

    leaks = find_leaks(workspace)
    if not leaks:
        if args.clean:
            parser.error("none of the approved paths is currently detected")
        print("No potential test artifacts detected.")
        return 0

    print(f"Found {len(leaks)} potential test artifact(s):")
    for leak in leaks:
        print(f"  - {leak}")

    if not args.clean:
        return 1

    approved = set()
    for value in args.path:
        requested = Path(value)
        if requested.is_absolute() or requested.drive or ".." in requested.parts:
            parser.error(f"approved paths must be relative to the workspace: {value}")
        candidate = workspace / requested
        relative = candidate.relative_to(workspace)
        if any((workspace / Path(*relative.parts[:index])).is_symlink()
               for index in range(1, len(relative.parts) + 1)):
            parser.error(f"approved path must not use a symbolic link: {value}")
        if relative not in leaks:
            parser.error(f"approved path is not a current detected file: {value}")
        approved.add(relative)

    failed = False
    for leak in sorted(approved):
        target = workspace / leak
        if (target.is_symlink() or not target.is_file()
                or any((workspace / Path(*leak.parts[:index])).is_symlink()
                       for index in range(1, len(leak.parts)))):
            print(f"Skipped (no longer a regular file): {leak}")
            failed = True
            continue
        target.unlink()
        print(f"Removed approved artifact: {leak}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
