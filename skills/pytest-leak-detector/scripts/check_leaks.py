"""Find new likely test-artifact files and optionally remove approved paths."""

import argparse
import json
import os
import subprocess
from pathlib import Path

SUSPICIOUS_EXTENSIONS = {".db", ".sqlite", ".log", ".tmp"}
SUSPICIOUS_PREFIXES = {"temp_", "test_out_", "dump_"}

IGNORE_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__",
    ".pytest_cache", ".tox", ".nox", ".mypy_cache", ".ruff_cache",
    "node_modules", ".idea", ".vscode", "build", "dist",
}


def find_leaks(root_dir: Path) -> list[Path]:
    """Return suspicious regular files relative to the workspace root."""
    root_dir = root_dir.resolve()
    leaks = []

    def raise_walk_error(error: OSError) -> None:
        raise error

    for current_root, dirnames, filenames in os.walk(
            root_dir, topdown=True, onerror=raise_walk_error):
        current_path = Path(current_root)
        dirnames[:] = sorted(
            dirname for dirname in dirnames
            if dirname not in IGNORE_DIRS
            and not (current_path / dirname).is_symlink()
        )
        for filename in filenames:
            path = current_path / filename
            if path.is_symlink() or not path.is_file():
                continue
            if (path.suffix.lower() in SUSPICIOUS_EXTENSIONS
                    or any(path.name.startswith(prefix) for prefix in SUSPICIOUS_PREFIXES)):
                leaks.append(path.relative_to(root_dir))
    return sorted(leaks)


def find_tracked_files(root_dir: Path) -> set[Path]:
    """Return Git-tracked files under the workspace, or an empty set outside Git."""
    root_dir = root_dir.resolve()
    git_root = next(
        (parent for parent in (root_dir, *root_dir.parents) if (parent / ".git").exists()),
        None,
    )
    if git_root is None:
        return set()

    try:
        result = subprocess.run(
            ["git", "-C", str(git_root), "ls-files", "-z", "--cached"],
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise RuntimeError(f"could not run Git to check tracked files: {error}") from error
    if result.returncode:
        error = os.fsdecode(result.stderr).strip()
        raise RuntimeError(f"git ls-files failed: {error}")

    tracked = set()
    for entry in result.stdout.split(b"\0"):
        if not entry:
            continue
        path = git_root / os.fsdecode(entry)
        try:
            tracked.add(path.relative_to(root_dir))
        except ValueError:
            continue
    return tracked


def find_candidates(root_dir: Path) -> list[Path]:
    """Return suspicious files that are not tracked by Git."""
    return sorted(set(find_leaks(root_dir)) - find_tracked_files(root_dir))


def _validate_baseline_location(parser: argparse.ArgumentParser, workspace: Path,
                                baseline_path: Path) -> Path:
    baseline_path = baseline_path.resolve()
    if baseline_path == workspace or workspace in baseline_path.parents:
        parser.error("baseline file must be outside the workspace")
    return baseline_path


def _read_baseline(parser: argparse.ArgumentParser, path: Path) -> set[Path]:
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        parser.error(f"could not read baseline {path!r}: {error}")
    if not isinstance(entries, list) or any(not isinstance(entry, str) for entry in entries):
        parser.error(f"baseline must contain a JSON list of relative paths: {path!r}")

    baseline = set()
    for entry in entries:
        relative = Path(entry)
        if relative.is_absolute() or relative.drive or ".." in relative.parts:
            parser.error(f"baseline contains an invalid relative path: {entry!r}")
        baseline.add(relative)
    return baseline


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                        help="workspace to scan (default: current directory)")
    baseline_group = parser.add_mutually_exclusive_group()
    baseline_group.add_argument("--save-baseline", type=Path, metavar="FILE",
                                help="save current candidates before running tests")
    baseline_group.add_argument("--baseline", type=Path, metavar="FILE",
                                help="report only candidates not present in this baseline")
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
    if args.clean and not args.baseline:
        parser.error("--clean requires --baseline so only new candidates can be removed")
    if args.path and not args.clean:
        parser.error("--path can only be used with --clean")
    if args.save_baseline and (args.clean or args.path):
        parser.error("--save-baseline cannot be combined with --clean or --path")

    if args.save_baseline:
        baseline_path = _validate_baseline_location(parser, workspace, args.save_baseline)
        try:
            candidates = find_candidates(workspace)
        except RuntimeError as error:
            parser.error(str(error))
        try:
            baseline_path.write_text(
                json.dumps([path.as_posix() for path in candidates], indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError as error:
            parser.error(f"could not write baseline {baseline_path!r}: {error}")
        print(f"Saved baseline with {len(candidates)} candidate(s) to {baseline_path!r}.")
        return 0

    try:
        leaks = find_candidates(workspace)
    except RuntimeError as error:
        parser.error(str(error))
    if args.baseline:
        baseline_path = _validate_baseline_location(parser, workspace, args.baseline)
        baseline = _read_baseline(parser, baseline_path)
        leaks = [leak for leak in leaks if leak not in baseline]

    if not leaks:
        if args.clean:
            parser.error("none of the approved paths is currently detected")
        if args.baseline:
            print("No new potential test artifacts detected.")
        else:
            print("No potential test artifacts detected.")
        return 0

    label = "new potential test artifact(s)" if args.baseline else "potential test artifact(s)"
    print(f"Found {len(leaks)} {label}:")
    for leak in leaks:
        print(f"  - {leak!r}")

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
            print(f"Skipped (no longer a regular file): {leak!r}")
            failed = True
            continue
        target.unlink()
        print(f"Removed approved artifact: {leak!r}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
