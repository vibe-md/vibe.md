"""Tests for the install, update, and uninstall lifecycle of scripts/install.sh.

These use small generated packages, so they stay valid when real packages gain
or lose skills. They cover ownership tracking: only files that still match what
an installation recorded are ever replaced or removed.

Run with: python3 -m unittest discover -s tests -v
"""

import hashlib
import os
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

    def test_the_record_is_written_even_if_the_output_is_closed_early(self):
        import shlex
        import subprocess
        command = "bash {} --group alpha --agent codex --skills-dir {} --project {} | head -n 1".format(
            shlex.quote(str(base.INSTALLER)), shlex.quote(str(self.skills)), shlex.quote(str(self.project)))
        subprocess.run(["bash", "-c", command], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(self.home)})
        self.assertTrue((self.receipts / "alpha.receipt").is_file())
        self.assertTrue((self.dest / "alpha-save/SKILL.md").is_file())

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

    def test_uninstalling_one_skill_of_a_legacy_installation_keeps_the_shared_documents(self):
        self.legacy_install()
        shutil.copytree(str(self.skills / "alpha"), str(self.dest / "alpha"), ignore=shutil.ignore_patterns("alpha-*"))
        result = self.run_installer(
            "--uninstall", "--skill", "alpha-status", "--agent", "codex", "--skills-dir", str(self.skills),
            "--project", str(self.project),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.dest / "alpha-status").exists())
        self.assertTrue((self.dest / "alpha/README.md").is_file(), "shared group documents were removed")
        self.assertTrue((self.dest / "alpha-save/SKILL.md").is_file())
        self.assertTrue((self.dest / "router/SKILL.md").is_file())
        self.assertIn("shared with other workflows", result.stdout)

    # --- adversarial uninstall --------------------------------------------------

    def outside_copy(self, source):
        """A decoy outside the project holding byte-identical copies of installed files."""
        outside = self.root / "outside"
        shutil.copytree(str(source), str(outside / source.name))
        return outside / source.name

    def test_a_symlinked_skill_directory_is_never_followed_by_uninstall(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        decoy = self.outside_copy(self.dest / "alpha-save")
        shutil.rmtree(str(self.dest / "alpha-save"))
        os.symlink(str(decoy), str(self.dest / "alpha-save"))
        result = self.uninstall("alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((decoy / "SKILL.md").is_file(), "a file outside the project was deleted")
        self.assertTrue((self.dest / "alpha-save").is_symlink())
        self.assertIn("symbolic link", result.stdout)
        self.assertFalse((self.dest / "alpha-status").exists())

    def test_a_symlink_in_the_middle_of_a_path_is_never_followed_by_uninstall(self):
        references = self.skills / "alpha" / "alpha-save" / "references"
        references.mkdir()
        (references / "guide.md").write_text("Guide.\n")
        self.assertEqual(self.package("alpha").returncode, 0)
        decoy = self.outside_copy(self.dest / "alpha-save" / "references")
        shutil.rmtree(str(self.dest / "alpha-save" / "references"))
        os.symlink(str(decoy), str(self.dest / "alpha-save" / "references"))
        result = self.uninstall("alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((decoy / "guide.md").is_file(), "a file outside the project was deleted")

    def test_a_forged_receipt_cannot_reach_files_outside_the_skills_directory(self):
        victim = self.root / "victim.txt"
        victim.write_text("precious\n")
        digest = hashlib.sha256(victim.read_bytes()).hexdigest()
        mine = self.dest / "my-skill" / "notes.md"
        mine.parent.mkdir(parents=True)
        mine.write_text("mine\n")
        own = hashlib.sha256(mine.read_bytes()).hexdigest()
        self.receipts.mkdir(parents=True)
        (self.receipts / "forged.receipt").write_text(
            "# vibe.md install receipt v1\n"
            "{d}  ../../../../victim.txt\n{d}  {abs}\n{d}  my-skill/../../../victim.txt\n"
            "{d}  ./../../victim.txt\n{o}  my-skill/notes.md\n".format(d=digest, abs=victim, o=own)
        )
        result = self.uninstall("forged")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(victim.read_text(), "precious\n")
        self.assertFalse(mine.exists())  # a genuine entry inside the skills directory is still honored
        self.assertIn("Removed 1 file(s)", result.stdout)
        self.assertIn("Kept 4", result.stdout)

    def test_the_dry_run_counts_only_files_that_would_really_be_removed(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        decoy = self.outside_copy(self.dest / "alpha-save")
        shutil.rmtree(str(self.dest / "alpha-save"))
        os.symlink(str(decoy), str(self.dest / "alpha-save"))
        result = self.uninstall("alpha", "--dry-run")
        self.assertNotIn("alpha-save/SKILL.md", [line.split(": ")[-1].replace(".agents/skills/", "") for line in result.stdout.splitlines() if "Would remove" in line])
        self.assertTrue((decoy / "SKILL.md").is_file())

    # --- round trip -----------------------------------------------------------

    def test_install_uninstall_install_round_trip(self):
        self.assertEqual(self.package("alpha").returncode, 0)
        first = tree(self.project)
        self.assertEqual(self.uninstall("alpha").returncode, 0)
        self.assertEqual(self.package("alpha").returncode, 0)
        self.assertEqual(tree(self.project), first)


class StandaloneLifecycleTests(base.InstallerTestCase):
    """A standalone skill is a package of one: removing it ends the package, including the
    shared router it brought along, unless another installed package still uses that."""

    def setUp(self):
        super().setUp()
        self.skills = self.root / "packages"
        for name in ("solo-tool", "solo-other"):
            LifecycleTests.write_skill(self.skills / name, name, "first version")
        LifecycleTests.write_skill(self.skills / "_shared" / "router", "router", "first version")
        (self.skills / "alpha").mkdir()
        (self.skills / "alpha" / "README.md").write_text("# alpha\n")
        LifecycleTests.write_skill(self.skills / "alpha" / "alpha-save", "alpha-save", "first version")
        self.dest = self.project / ".agents/skills"
        self.receipts = self.project / ".agents/.vibe-md"

    def add(self, selector, name, agent="codex", skills=None):
        return self.run_installer(
            selector, name, "--agent", agent, "--skills-dir", str(skills or self.skills),
            "--project", str(self.project),
        )

    def remove(self, name, *extra, agent="codex", skills=None):
        return self.run_installer(
            "--uninstall", "--skill", name, "--agent", agent, "--skills-dir", str(skills or self.skills),
            "--project", str(self.project), *extra,
        )

    def test_a_standalone_skill_uninstalls_completely_by_name(self):
        self.assertEqual(self.add("--skill", "solo-tool").returncode, 0)
        self.assertTrue((self.dest / "router/SKILL.md").is_file())
        self.assertTrue((self.receipts / "solo-tool.receipt").is_file())
        result = self.remove("solo-tool")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(tree(self.project), {})
        self.assertFalse(self.receipts.exists(), "an orphan receipt was left behind")

    def test_the_shared_router_stays_while_another_standalone_skill_needs_it(self):
        self.assertEqual(self.add("--skill", "solo-tool").returncode, 0)
        self.assertEqual(self.add("--skill", "solo-other").returncode, 0)
        result = self.remove("solo-tool")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Keeping 'router': it is also used by 'solo-other'.", result.stdout)
        self.assertFalse((self.dest / "solo-tool").exists())
        self.assertTrue((self.dest / "solo-other/SKILL.md").is_file())
        self.assertTrue((self.dest / "router/SKILL.md").is_file())
        self.assertFalse((self.receipts / "solo-tool.receipt").exists())
        self.assertIn("router/SKILL.md", (self.receipts / "solo-other.receipt").read_text())
        self.assertEqual(self.remove("solo-other").returncode, 0)
        self.assertEqual(tree(self.project), {})
        self.assertFalse(self.receipts.exists())

    def test_removing_a_standalone_skill_leaves_a_group_intact_and_the_group_cleans_up_after(self):
        self.assertEqual(self.add("--group", "alpha").returncode, 0)
        self.assertEqual(self.add("--skill", "solo-tool").returncode, 0)
        grouped = {path: data for path, data in tree(self.project).items() if "solo-tool" not in path}
        result = self.remove("solo-tool")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(tree(self.project), grouped)
        self.assertTrue((self.receipts / "alpha.receipt").is_file())
        self.assertFalse((self.receipts / "solo-tool.receipt").exists())
        uninstall = self.run_installer(
            "--uninstall", "--group", "alpha", "--agent", "codex", "--skills-dir", str(self.skills),
            "--project", str(self.project),
        )
        self.assertEqual(uninstall.returncode, 0, uninstall.stderr)
        self.assertEqual(tree(self.project), {})
        self.assertFalse(self.receipts.exists())

    def test_removing_a_group_first_keeps_the_router_for_the_standalone_skill(self):
        self.assertEqual(self.add("--group", "alpha").returncode, 0)
        self.assertEqual(self.add("--skill", "solo-tool").returncode, 0)
        uninstall = self.run_installer(
            "--uninstall", "--group", "alpha", "--agent", "codex", "--skills-dir", str(self.skills),
            "--project", str(self.project),
        )
        self.assertEqual(uninstall.returncode, 0, uninstall.stderr)
        self.assertIn("Keeping 'router': it is also used by 'solo-tool'.", uninstall.stdout)
        self.assertFalse((self.dest / "alpha-save").exists())
        self.assertFalse((self.receipts / "alpha.receipt").exists())
        self.assertTrue((self.dest / "router/SKILL.md").is_file())
        self.assertTrue((self.dest / "solo-tool/SKILL.md").is_file())
        self.assertTrue((self.receipts / "solo-tool.receipt").is_file())
        self.assertEqual(self.remove("solo-tool").returncode, 0)
        self.assertEqual(tree(self.project), {})
        self.assertFalse(self.receipts.exists())

    def test_real_gitly_is_untouched_by_installing_and_removing_a_standalone_skill(self):
        collection = self.root / "collection"
        shutil.copytree(str(base.REPO_ROOT / "skills"), str(collection))
        LifecycleTests.write_skill(collection / "solo-tool", "solo-tool", "first version")
        gitly = self.run_installer(
            "--group", "gitly", "--agent", "codex", "--skills-dir", str(collection), "--project", str(self.project),
        )
        self.assertEqual(gitly.returncode, 0, gitly.stderr)
        before = tree(self.project)
        self.assertEqual(self.add("--skill", "solo-tool", skills=collection).returncode, 0)
        self.assertEqual(self.remove("solo-tool", skills=collection).returncode, 0)
        self.assertEqual(tree(self.project), before)
        removed = self.run_installer(
            "--uninstall", "--group", "gitly", "--agent", "codex", "--skills-dir", str(collection),
            "--project", str(self.project),
        )
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(tree(self.project), {})
        self.assertFalse(self.receipts.exists())

    def test_edited_files_survive_removal_and_an_edited_router_is_kept(self):
        self.assertEqual(self.add("--skill", "solo-tool").returncode, 0)
        (self.dest / "solo-tool/SKILL.md").write_text("my edit\n")
        (self.dest / "router/SKILL.md").write_text("my router edit\n")
        result = self.remove("solo-tool")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("modified after installation", result.stdout)
        self.assertEqual((self.dest / "solo-tool/SKILL.md").read_text(), "my edit\n")
        self.assertEqual((self.dest / "router/SKILL.md").read_text(), "my router edit\n")

    def test_unmodified_router_files_go_even_when_the_skill_was_edited(self):
        self.assertEqual(self.add("--skill", "solo-tool").returncode, 0)
        (self.dest / "solo-tool/SKILL.md").write_text("my edit\n")
        self.assertEqual(self.remove("solo-tool").returncode, 0)
        self.assertFalse((self.dest / "router").exists())
        self.assertEqual((self.dest / "solo-tool/SKILL.md").read_text(), "my edit\n")

    def test_the_dry_run_reports_the_router_and_changes_nothing(self):
        self.assertEqual(self.add("--skill", "solo-tool").returncode, 0)
        before = tree(self.project)
        result = self.remove("solo-tool", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Would remove: .agents/skills/solo-tool/SKILL.md", result.stdout)
        self.assertIn("Would remove: .agents/skills/router/SKILL.md", result.stdout)
        self.assertEqual(tree(self.project), before)

    def test_a_forged_receipt_for_a_standalone_skill_cannot_reach_files_outside(self):
        victim = self.root / "victim.txt"
        victim.write_text("precious\n")
        digest = hashlib.sha256(victim.read_bytes()).hexdigest()
        self.assertEqual(self.add("--skill", "solo-tool").returncode, 0)
        receipt = self.receipts / "solo-tool.receipt"
        receipt.write_text(receipt.read_text() + "{d}  ../../../../victim.txt\n{d}  {abs}\n{d}  router/../../../../victim.txt\n".format(d=digest, abs=victim))
        result = self.remove("solo-tool")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(victim.read_text(), "precious\n")
        self.assertFalse((self.dest / "solo-tool").exists())
        self.assertFalse((self.dest / "router").exists())
        self.assertIn("Removed 2 file(s)", result.stdout)
        self.assertIn("Kept 3", result.stdout)

    def test_a_symlinked_standalone_skill_directory_is_never_followed(self):
        self.assertEqual(self.add("--skill", "solo-tool").returncode, 0)
        decoy = self.root / "outside" / "solo-tool"
        shutil.copytree(str(self.dest / "solo-tool"), str(decoy))
        shutil.rmtree(str(self.dest / "solo-tool"))
        os.symlink(str(decoy), str(self.dest / "solo-tool"))
        result = self.remove("solo-tool")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((decoy / "SKILL.md").is_file(), "a file outside the project was deleted")
        self.assertTrue((self.dest / "solo-tool").is_symlink())
        self.assertIn("symbolic link", result.stdout)

    def test_every_supported_agent_directory_is_cleaned_up(self):
        for agent in base.AGENT_DIRS:
            self.assertEqual(self.add("--skill", "solo-tool", agent=agent).returncode, 0, agent)
        for agent, directory in base.AGENT_DIRS.items():
            self.assertTrue((self.project / directory / "solo-tool/SKILL.md").is_file(), agent)
            self.assertTrue((self.project / directory / "router/SKILL.md").is_file(), agent)
        for agent in base.AGENT_DIRS:
            result = self.remove("solo-tool", agent=agent)
            self.assertEqual(result.returncode, 0, "{}: {}".format(agent, result.stderr))
        self.assertEqual(tree(self.project), {})


if __name__ == "__main__":
    unittest.main()
