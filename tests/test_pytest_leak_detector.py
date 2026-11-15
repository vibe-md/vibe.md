import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPOSITORY_ROOT
    / "skills"
    / "pytest-leak-detector"
    / "scripts"
    / "check_leaks.py"
)
SPEC = importlib.util.spec_from_file_location("check_leaks", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load scanner from {SCRIPT_PATH}")
check_leaks = importlib.util.module_from_spec(SPEC)
write_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    SPEC.loader.exec_module(check_leaks)
finally:
    sys.dont_write_bytecode = write_bytecode


class FindLeaksTest(unittest.TestCase):
    def run_scanner(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *map(str, args)],
            capture_output=True,
            check=False,
            text=True,
        )

    def test_prunes_ignored_directories_during_walk(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "visible.log").write_text("candidate", encoding="utf-8")
            for directory in check_leaks.IGNORE_DIRS:
                ignored_dir = root / "nested" / directory
                ignored_dir.mkdir(parents=True, exist_ok=True)
                (ignored_dir / "hidden.log").write_text("candidate", encoding="utf-8")

            visited = []
            original_walk = check_leaks.os.walk

            def recording_walk(*args, **kwargs):
                for entry in original_walk(*args, **kwargs):
                    visited.append(Path(entry[0]))
                    yield entry

            with patch.object(check_leaks.os, "walk", recording_walk):
                leaks = check_leaks.find_leaks(root)

            self.assertEqual([Path("visible.log")], leaks)
            for visited_root in visited:
                relative_parts = visited_root.relative_to(root).parts
                self.assertTrue(check_leaks.IGNORE_DIRS.isdisjoint(relative_parts))

    def test_baseline_reports_only_new_candidates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            workspace = root / "workspace"
            workspace.mkdir()
            baseline = root / "baseline.json"
            (workspace / "preexisting.log").write_text("old", encoding="utf-8")

            saved = self.run_scanner(
                "--workspace", workspace, "--save-baseline", baseline
            )
            self.assertEqual(0, saved.returncode, saved.stderr)

            (workspace / "new.log").write_text("new", encoding="utf-8")
            compared = self.run_scanner(
                "--workspace", workspace, "--baseline", baseline
            )

            self.assertEqual(1, compared.returncode, compared.stderr)
            self.assertIn("new.log", compared.stdout)
            self.assertNotIn("preexisting.log", compared.stdout)

    def test_git_tracked_files_are_excluded(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "tracked.db").write_text("tracked", encoding="utf-8")
            (root / "untracked.log").write_text("untracked", encoding="utf-8")

            with patch.object(
                check_leaks,
                "find_tracked_files",
                return_value={Path("tracked.db")},
            ):
                candidates = check_leaks.find_candidates(root)

            self.assertEqual([Path("untracked.log")], candidates)

    def test_clean_requires_a_baseline(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = root / "candidate.log"
            candidate.write_text("candidate", encoding="utf-8")

            result = self.run_scanner(
                "--workspace", root, "--clean", "--path", "candidate.log"
            )

            self.assertEqual(2, result.returncode)
            self.assertIn("--clean requires --baseline", result.stderr)
            self.assertTrue(candidate.exists())


if __name__ == "__main__":
    unittest.main()
