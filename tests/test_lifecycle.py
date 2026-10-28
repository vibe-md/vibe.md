"""Tests for the install, update, and uninstall lifecycle of scripts/install.sh.

These use small generated packages, so they stay valid when real packages gain
or lose skills. They cover ownership tracking: only files that still match what
an installation recorded are ever replaced or removed.

Run with: python3 -m unittest discover -s tests -v
"""

import shutil
import unittest
from pathlib import Path

import test_installer as base

tree = base.tree
snapshot = base.snapshot


class LifecycleTests(base.InstallerTestCase):
    def setUp(self):
        super().setUp()
        self.skills = self.root / "packages"
        for package, names in (("alpha", ("alpha-save", "alpha-status")), ("beta", ("beta-audit",))):
            (self.skills / package).mkdir(parents=True)
            (self.skills / package / "README.md").write_text("# {}\n".format(package))
            for name in names:
                self.write_skill(self.skills / package / name, name, "first version")
        self.write_skill(self.skills / "_shared" / "router", "router", "first version")
        self.dest = self.project / ".agents/skills"
        self.receipts = self.project / ".agents/.vibe-md"

    @staticmethod
    def write_skill(path, name, body):
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(
            "---\nname: {}\ndescription: A skill used to test the package lifecycle.\n---\n\n{}\n".format(name, body)
        )

    def package(self, package, *extra, agent="codex"):
        return self.run_installer(
            "--group", package, "--agent", agent, "--skills-dir", str(self.skills),
            "--project", str(self.project), *extra,
        )

    def uninstall(self, package, *extra, agent="codex"):
        return self.run_installer(
            "--uninstall", "--group", package, "--agent", agent, "--skills-dir", str(self.skills),
            "--project", str(self.project), *extra,
        )

    def bump(self, name, body="second version", package="alpha"):
        self.write_skill(self.skills / package / name, name, body)

    # --- installation records -------------------------------------------------

    def test_installing_a_package_records_what_it_installed(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        receipt = (self.receipts / "alpha.receipt").read_text()
        self.assertIn("# package: alpha", receipt)
        for path in ("alpha-save/SKILL.md", "alpha-status/SKILL.md", "router/SKILL.md", "alpha/README.md"):
            self.assertIn("  " + path, receipt)
        self.assertNotIn("beta-audit", receipt)

    def test_receipts_live_beside_the_skills_not_inside_them(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        self.assertEqual({p.name for p in self.dest.iterdir()}, {"alpha-save", "alpha-status", "alpha", "router"})

    def test_reinstalling_is_a_no_op(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        before = tree(self.project)
        result = self.package("alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("already installed", result.stdout)
        self.assertEqual(tree(self.project), before)

    # --- updates --------------------------------------------------------------

    def test_an_unmodified_package_is_updated_without_force(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        self.bump("alpha-save")
        result = self.package("alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Updated 'alpha-save'", result.stdout)
        self.assertIn("second version", (self.dest / "alpha-save/SKILL.md").read_text())

    def test_a_locally_modified_skill_blocks_the_update_and_nothing_changes(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        mine = self.dest / "alpha-save/SKILL.md"
        mine.write_text(mine.read_text() + "\nMy own note.\n")
        self.bump("alpha-save")
        self.bump("alpha-status")
        before = tree(self.project)
        result = self.package("alpha")
        self.assertEqual(result.returncode, 1)
        self.assertIn("already exists and differs", result.stderr)
        self.assertEqual(tree(self.project), before)

    def test_force_replaces_a_modified_skill(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        mine = self.dest / "alpha-save/SKILL.md"
        mine.write_text("my edit\n")
        self.bump("alpha-save")
        self.assertEqual(self.package("alpha", "--force").returncode, 0)
        self.assertIn("second version", mine.read_text())

    def test_an_extra_file_in_a_skill_counts_as_a_modification(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        (self.dest / "alpha-save/notes.md").write_text("mine\n")
        self.bump("alpha-save")
        result = self.package("alpha")
        self.assertEqual(result.returncode, 1)
        self.assertEqual((self.dest / "alpha-save/notes.md").read_text(), "mine\n")

    # --- uninstall ------------------------------------------------------------

    def test_uninstall_removes_the_package_and_its_record(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        result = self.uninstall("alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.project), set(
            p for p in snapshot(self.project) if p in (".agents", ".agents/skills")))
        self.assertFalse(self.receipts.exists())

    def test_uninstall_keeps_modified_files_and_user_files(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        edited = self.dest / "alpha-save/SKILL.md"
        edited.write_text("my edit\n")
        (self.dest / "alpha-status/notes.md").write_text("mine\n")
        unrelated = self.dest / "my-own-skill"
        self.write_skill(unrelated, "my-own-skill", "not from vibe.md")
        result = self.uninstall("alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("modified after installation", result.stdout)
        self.assertEqual(edited.read_text(), "my edit\n")
        self.assertEqual((self.dest / "alpha-status/notes.md").read_text(), "mine\n")
        self.assertFalse((self.dest / "alpha-status/SKILL.md").exists())
        self.assertTrue((unrelated / "SKILL.md").is_file())

    def test_uninstall_dry_run_writes_nothing(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        before = tree(self.project)
        result = self.uninstall("alpha", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Would remove", result.stdout)
        self.assertEqual(tree(self.project), before)

    def test_uninstalling_one_skill_leaves_the_rest_of_the_package(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        result = self.run_installer(
            "--uninstall", "--skill", "alpha-status", "--agent", "codex", "--skills-dir", str(self.skills),
            "--project", str(self.project),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.dest / "alpha-status").exists())
        self.assertTrue((self.dest / "alpha-save/SKILL.md").is_file())
        self.assertNotIn("alpha-status", (self.receipts / "alpha.receipt").read_text())

    def test_uninstall_refuses_an_agent_with_nothing_installed(self):
        result = self.uninstall("alpha")
        self.assertEqual(result.returncode, 1)
        self.assertIn("nothing is installed", result.stderr)

    # --- several packages -----------------------------------------------------

    def test_two_packages_coexist_and_share_the_router(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        self.assertEqual(self.package("beta").returncode, 0)
        self.assertEqual({p.name for p in self.dest.iterdir()},
                         {"alpha-save", "alpha-status", "alpha", "beta-audit", "beta", "router"})
        self.assertEqual({p.name for p in self.receipts.iterdir()}, {"alpha.receipt", "beta.receipt"})

    def test_a_shared_skill_stays_until_its_last_package_is_removed(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        self.assertEqual(self.package("beta").returncode, 0)
        result = self.uninstall("alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("also used by 'beta'", result.stdout)
        self.assertTrue((self.dest / "router/SKILL.md").is_file())
        self.assertTrue((self.dest / "beta-audit/SKILL.md").is_file())
        self.assertFalse((self.dest / "alpha-save").exists())
        self.assertEqual(self.uninstall("beta").returncode, 0)
        self.assertFalse((self.dest / "router").exists())
        self.assertFalse(self.receipts.exists())

    def test_removing_one_package_does_not_change_the_other(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        self.assertEqual(self.package("beta").returncode, 0)
        beta_before = tree(self.dest / "beta-audit")
        self.assertEqual(self.uninstall("alpha").returncode, 0)
        self.assertEqual(tree(self.dest / "beta-audit"), beta_before)

    # --- installations made before receipts existed ----------------------------

    def legacy_install(self):
        for name in ("alpha-save", "alpha-status"):
            shutil.copytree(str(self.skills / "alpha" / name), str(self.dest / name))
        shutil.copytree(str(self.skills / "_shared/router"), str(self.dest / "router"))

    def test_a_legacy_installation_is_adopted_by_installing_again(self):
        self.legacy_install()
        before = tree(self.dest)
        result = self.package("alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        for path, content in before.items():
            self.assertEqual(tree(self.dest)[path], content)
        self.assertTrue((self.receipts / "alpha.receipt").is_file())

    def test_uninstalling_a_legacy_installation_removes_only_identical_copies(self):
        self.legacy_install()
        edited = self.dest / "alpha-status/SKILL.md"
        edited.write_text("my edit\n")
        result = self.uninstall("alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.dest / "alpha-save").exists())
        self.assertEqual(edited.read_text(), "my edit\n")
        self.assertTrue((self.dest / "router/SKILL.md").is_file())
        self.assertIn("shared skills are only removed with ownership records", result.stdout)

    # --- round trip -----------------------------------------------------------

    def test_install_uninstall_install_round_trip(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        first = tree(self.project)
        self.assertEqual(self.uninstall("alpha").returncode, 0)
        self.assertEqual(self.package("alpha").returncode, 0)
        self.assertEqual(tree(self.project), first)


if __name__ == "__main__":
    unittest.main()
