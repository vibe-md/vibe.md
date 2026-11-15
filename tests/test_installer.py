"""Tests for scripts/install.sh.

Every test runs inside its own temporary directory with HOME and TMPDIR pointed
there, so nothing is ever installed into a real agent configuration. Local
tests need no network access. Set VIBE_MD_INTEGRATION=1 to also run the tests
that download the real repository from GitHub.

Run with: python3 -m unittest discover -s tests -v
"""

import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = REPO_ROOT / "scripts" / "install.sh"
VALID = REPO_ROOT / "tests" / "fixtures" / "valid"

AGENT_DIRS = {
    "claude-code": ".claude/skills",
    "codex": ".agents/skills",
    "cursor": ".cursor/skills",
    "gemini": ".gemini/skills",
    "copilot": ".github/skills",
}


def snapshot(root):
    """Every path under root, relative to root."""
    paths = set()
    for current, dirs, files in os.walk(str(root)):
        for name in dirs + files:
            paths.add(os.path.relpath(os.path.join(current, name), str(root)))
    return paths


def tree(root):
    """Map of relative file path -> bytes, for comparing directory contents."""
    root = Path(root)
    return {
        str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()
    }


class InstallerTestCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="vibe md test "))  # contains spaces on purpose
        self.home = self.root / "home"
        self.tmpdir = self.root / "tmp"
        self.project = self.root / "my project"
        for path in (self.home, self.tmpdir, self.project):
            path.mkdir()

    def tearDown(self):
        for current, dirs, _ in os.walk(str(self.root)):
            for name in dirs:
                os.chmod(os.path.join(current, name), 0o755)
        shutil.rmtree(str(self.root))

    def run_installer(self, *args, script=INSTALLER, cwd=None, env_extra=None, stdin_script=False):
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.home),
            "TMPDIR": str(self.tmpdir),
            "LC_ALL": "C",
        }
        if env_extra:
            env.update(env_extra)
        if stdin_script:
            command = ["bash", "-s", "--"] + list(args)
            stdin = Path(script).read_text()
        else:
            command = ["bash", str(script)] + list(args)
            stdin = None
        return subprocess.run(
            command,
            input=stdin,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(cwd or self.project),
        )

    def install(self, skill="basic-skill", agent="claude-code", *extra, skills_dir=VALID):
        return self.run_installer(
            "--skill", skill, "--agent", agent, "--project", str(self.project),
            "--skills-dir", str(skills_dir), *extra
        )


class CommandLineTests(InstallerTestCase):
    def test_help(self):
        result = self.run_installer("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)
        for agent, directory in AGENT_DIRS.items():
            self.assertIn(agent, result.stdout)
            self.assertIn(directory, result.stdout)

    def test_unknown_option(self):
        result = self.run_installer("--bogus")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown option", result.stderr)

    def test_missing_skill_and_agent(self):
        result = self.run_installer("--agent", "codex")
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing --skill", result.stderr)
        result = self.run_installer("--skill", "basic-skill")
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing --agent", result.stderr)

    def test_option_without_value(self):
        result = self.run_installer("--skill")
        self.assertEqual(result.returncode, 2)
        self.assertIn("needs a value", result.stderr)

    def test_equals_syntax(self):
        result = self.run_installer(
            "--skill=basic-skill", "--agent=codex", "--project=" + str(self.project),
            "--skills-dir=" + str(VALID),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / ".agents/skills/basic-skill/SKILL.md").is_file())

    def test_unknown_agent(self):
        result = self.install(agent="notepad")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown agent 'notepad'", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_unknown_skill(self):
        result = self.install(skill="does-not-exist")
        self.assertEqual(result.returncode, 1)
        self.assertIn("skill 'does-not-exist' was not found", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_path_traversal_in_skill_name_is_rejected(self):
        for name in ["../basic-skill", "basic-skill/..", "/etc", "Basic-Skill", "a b", ".hidden"]:
            with self.subTest(name=name):
                result = self.install(skill=name)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("invalid skill name", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_invalid_ref_is_rejected(self):
        result = self.run_installer("--list", "--ref", "../../evil")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid --ref", result.stderr)

    def test_missing_project_directory(self):
        result = self.run_installer(
            "--skill", "basic-skill", "--agent", "codex", "--skills-dir", str(VALID),
            "--project", str(self.root / "nope"),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("project directory not found", result.stderr)


    def test_force_with_uninstall_is_a_usage_error(self):
        result = self.run_installer(
            "--uninstall", "--force", "--skill", "basic-skill", "--agent", "codex", "--project", str(self.project),
            "--skills-dir", str(VALID),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--force cannot be combined with --uninstall", result.stderr)

    def test_list_validates_the_agent(self):
        result = self.run_installer("--list", "--agent", "notepad", "--skills-dir", str(VALID))
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown agent 'notepad'", result.stderr)
        result = self.run_installer("--list", "--agent", "codex", "--skills-dir", str(VALID))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("basic-skill", result.stdout)

    def test_copilot_next_steps_name_the_skills_directory(self):
        result = self.install("basic-skill", "copilot")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Commit and push .github/skills to make", result.stdout)
        self.assertNotIn(".github/skills/basic-skill to make", result.stdout)


class ListTests(InstallerTestCase):
    def test_list_empty_collection(self):
        empty = self.root / "empty skills"
        empty.mkdir()
        (empty / "README.md").write_text("# Skills\n")
        result = self.run_installer("--list", "--skills-dir", str(empty))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No skills are available yet.", result.stdout)

    def test_list_shows_skills_and_descriptions(self):
        result = self.run_installer("--list", "--skills-dir", str(VALID))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("basic-skill", result.stdout)
        self.assertIn("A minimal test skill", result.stdout)
        # Folded YAML description (description: >) is read too.
        self.assertIn("A test skill with bundled scripts", result.stdout)

    def test_repository_catalog_never_lists_test_fixtures(self):
        result = self.run_installer("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        for fixture in ("basic-skill", "bundled-resources"):
            self.assertNotIn(fixture, result.stdout)


class InstallTests(InstallerTestCase):
    def test_every_agent_destination(self):
        for agent, directory in AGENT_DIRS.items():
            with self.subTest(agent=agent):
                result = self.install("basic-skill", agent)
                self.assertEqual(result.returncode, 0, result.stderr)
                dest = self.project / directory / "basic-skill"
                self.assertEqual(tree(dest), tree(VALID / "basic-skill"))
                self.assertIn(str(dest), result.stdout)

    def test_runs_in_current_directory_by_default(self):
        result = self.run_installer(
            "--skill", "basic-skill", "--agent", "cursor", "--skills-dir", str(VALID),
            cwd=self.project,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / ".cursor/skills/basic-skill/SKILL.md").is_file())

    def test_bundled_resources_are_installed_but_not_executed(self):
        skills = self.root / "skills"
        skill = skills / "runs-nothing"
        shutil.copytree(str(VALID / "bundled-resources"), str(skill))
        text = (skill / "SKILL.md").read_text().replace("name: bundled-resources", "name: runs-nothing")
        (skill / "SKILL.md").write_text(text)
        marker = self.root / "script-was-executed"
        script = skill / "scripts" / "hello.sh"
        script.write_text("#!/usr/bin/env bash\ntouch '{}'\n".format(marker))
        script.chmod(0o755)

        result = self.install("runs-nothing", "codex", skills_dir=skills)
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.project / ".agents/skills/runs-nothing"
        self.assertEqual(tree(dest), tree(skill))
        self.assertTrue(os.access(str(dest / "scripts/hello.sh"), os.X_OK))
        self.assertTrue((dest / "references/guide.md").is_file())
        self.assertTrue((dest / "assets/template.txt").is_file())
        self.assertFalse(marker.exists(), "the installer must never run bundled scripts")

    def test_identical_reinstall_is_a_no_op(self):
        self.assertEqual(self.install().returncode, 0)
        before = tree(self.project)
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("already installed", result.stdout)
        self.assertEqual(tree(self.project), before)

    def test_conflicting_skill_is_not_overwritten(self):
        dest = self.project / ".claude/skills/basic-skill"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("my own skill\n")
        (dest / "notes.txt").write_text("keep me\n")
        result = self.install()
        self.assertEqual(result.returncode, 1)
        self.assertIn("already exists and differs", result.stderr)
        self.assertIn("--force", result.stderr)
        self.assertEqual((dest / "SKILL.md").read_text(), "my own skill\n")
        self.assertEqual((dest / "notes.txt").read_text(), "keep me\n")

    def test_force_replaces_conflicting_skill(self):
        dest = self.project / ".claude/skills/basic-skill"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("old\n")
        (dest / "stale.txt").write_text("stale\n")
        result = self.install("basic-skill", "claude-code", "--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Replaced", result.stdout)
        self.assertEqual(tree(dest), tree(VALID / "basic-skill"))

    def test_existing_file_at_destination_is_a_conflict(self):
        skills_root = self.project / ".claude/skills"
        skills_root.mkdir(parents=True)
        (skills_root / "basic-skill").write_text("a file, not a skill\n")
        result = self.install()
        self.assertEqual(result.returncode, 1)
        self.assertEqual((skills_root / "basic-skill").read_text(), "a file, not a skill\n")

    def test_other_skills_are_untouched(self):
        other = self.project / ".claude/skills/someone-elses-skill"
        other.mkdir(parents=True)
        (other / "SKILL.md").write_text("theirs\n")
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual((other / "SKILL.md").read_text(), "theirs\n")

    def test_dry_run_writes_nothing(self):
        result = self.install("bundled-resources", "gemini", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Dry run", result.stdout)
        self.assertIn("scripts/hello.sh", result.stdout)
        self.assertIn(".gemini/skills/bundled-resources", result.stdout)
        self.assertEqual(snapshot(self.project), set())

    def test_dry_run_reports_conflicts(self):
        dest = self.project / ".github/skills/basic-skill"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("different\n")
        result = self.install("basic-skill", "copilot", "--dry-run")
        self.assertEqual(result.returncode, 1)
        self.assertIn("already exists", result.stderr)

    def test_paths_with_spaces(self):
        skills = self.root / "skills with spaces"
        shutil.copytree(str(VALID / "basic-skill"), str(skills / "basic-skill"))
        project = self.root / "project with   spaces"
        project.mkdir()
        result = self.run_installer(
            "--skill", "basic-skill", "--agent", "claude-code",
            "--project", str(project), "--skills-dir", str(skills),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / ".claude/skills/basic-skill/SKILL.md").is_file())

    def test_no_writes_outside_destination(self):
        before = snapshot(self.root)
        self.assertEqual(self.install("bundled-resources", "codex").returncode, 0)
        created = snapshot(self.root) - before
        project = os.path.relpath(str(self.project), str(self.root))
        expected_prefix = os.path.join(project, ".agents")
        for path in created:
            self.assertTrue(path.startswith(expected_prefix), "unexpected write: " + path)
        self.assertEqual(snapshot(self.home), set())
        self.assertEqual(snapshot(self.tmpdir), set())

    def test_symlinked_agent_directory_outside_project_is_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        os.symlink(str(outside), str(self.project / ".claude"))
        result = self.install()
        self.assertEqual(result.returncode, 1)
        self.assertIn("outside the project", result.stderr)
        self.assertEqual(snapshot(outside), set())

    def test_skill_containing_symlink_is_refused(self):
        skills = self.root / "skills"
        shutil.copytree(str(VALID / "basic-skill"), str(skills / "basic-skill"))
        os.symlink("/etc/hosts", str(skills / "basic-skill" / "hosts"))
        result = self.install(skills_dir=skills)
        self.assertEqual(result.returncode, 1)
        self.assertIn("symbolic links", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "permissions are not enforced for root")
    def test_failed_installation_leaves_nothing_behind(self):
        agent_dir = self.project / ".claude"
        skills_root = agent_dir / "skills"
        skills_root.mkdir(parents=True)
        agent_dir.chmod(0o555)  # staging directory cannot be created
        result = self.install()
        agent_dir.chmod(0o755)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(snapshot(agent_dir), {"skills"})

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "permissions are not enforced for root")
    def test_failed_move_leaves_no_partial_skill(self):
        skills_root = self.project / ".claude/skills"
        skills_root.mkdir(parents=True)
        skills_root.chmod(0o555)  # final move into place fails
        result = self.install()
        skills_root.chmod(0o755)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(snapshot(skills_root), set())
        self.assertEqual(snapshot(self.project / ".claude"), {"skills"})


class GroupInstallTests(InstallerTestCase):
    def setUp(self):
        super().setUp()
        self.skills = self.root / "grouped skills"
        for group, name in (("_shared", "router"), ("versions", "save"),
                            ("versions", "status"), ("docs", "write-docs")):
            skill = self.skills / group / name
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: {}\ndescription: A workflow for testing grouped installations.\n"
                "---\n\nRead [the contract](references/contract.md).\n".format(name)
            )
            (skill / "references/contract.md").write_text("Local workflow contract.\n")

    def install_group(self, group="versions", agent="codex", *extra):
        return self.run_installer(
            "--group", group, "--agent", agent, "--skills-dir", str(self.skills),
            "--project", str(self.project), *extra,
        )

    def add_group_documents(self, group="versions", names=("save", "status")):
        (self.skills / group / "CONTRACT.md").write_text(group + " shared operating rules.\n")
        (self.skills / group / "LICENSE").write_text(group + " license.\n")
        for name in names:
            path = self.skills / group / name / "SKILL.md"
            path.write_text(path.read_text().replace("references/contract.md", "../CONTRACT.md") + '\nRead [rules]( <../CONTRACT.md> "Shared rules").\n')
            shutil.rmtree(path.parent / "references")

    def test_upgrading_old_gitly_layout_preserves_preferences_and_unrelated_work(self):
        source = REPO_ROOT / "skills/gitly"
        dest = self.project / ".agents/skills/gitly-status"
        (dest / "references").mkdir(parents=True)
        (dest / "SKILL.md").write_text((source / "gitly-status/SKILL.md").read_text().replace("(../GITLY.md)", "(references/GITLY.md)"))
        shutil.copy(source / "GITLY.md", dest / "references/GITLY.md")
        shutil.copy(source / "LICENSE", dest / "LICENSE")
        preferences = self.project / ".gitly/config.md"
        preferences.parent.mkdir()
        preferences.write_text("language: he\nhistory_length: 10\n")
        (self.project / "app.txt").write_text("My current work.\n")
        before = tree(self.project)
        result = self.install("gitly-status", "codex", skills_dir=REPO_ROOT / "skills")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(tree(self.project), before)
        result = self.install("gitly-status", "codex", "--force", skills_dir=REPO_ROOT / "skills")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name for p in dest.iterdir()}, {"SKILL.md"})
        self.assertEqual((dest.parent / "gitly/GITLY.md").read_bytes(), (source / "GITLY.md").read_bytes())
        self.assertEqual(preferences.read_text(), "language: he\nhistory_length: 10\n")
        self.assertEqual((self.project / "app.txt").read_text(), "My current work.\n")

    def test_single_member_installs_one_contract_and_license_for_every_agent(self):
        self.add_group_documents()
        for agent, directory in AGENT_DIRS.items():
            with self.subTest(agent=agent):
                result = self.install("save", agent, skills_dir=self.skills)
                self.assertEqual(result.returncode, 0, result.stderr)
                dest = self.project / directory
                self.assertEqual({p.name for p in dest.iterdir()}, {"save", "router", "versions"})
                self.assertEqual(tree(dest / "versions"), {
                    "CONTRACT.md": b"versions shared operating rules.\n", "LICENSE": b"versions license.\n",
                })
                self.assertIn("(../versions/CONTRACT.md)", (dest / "save/SKILL.md").read_text())
                self.assertIn('( <../versions/CONTRACT.md> "Shared rules")', (dest / "save/SKILL.md").read_text())
                self.assertEqual(sum(p.name == "CONTRACT.md" for p in dest.rglob("*.md")), 1)
                before = {p: p.stat().st_mtime_ns for p in dest.rglob("*") if p.is_file()}
                result = self.install("save", agent, skills_dir=self.skills)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(before, {p: p.stat().st_mtime_ns for p in dest.rglob("*") if p.is_file()})

    def test_second_group_keeps_its_documents_separate_and_conflicts_stop_all_writes(self):
        self.add_group_documents()
        self.add_group_documents("docs", ("write-docs",))
        self.assertEqual(self.install_group().returncode, 0)
        before = tree(self.project)
        result = self.install_group("docs")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = tree(self.project)
        for path, content in before.items():
            self.assertEqual(after[path], content)
        self.assertEqual((self.project / ".agents/skills/docs/CONTRACT.md").read_text(), "docs shared operating rules.\n")
        (self.project / ".agents/skills/docs/LICENSE").write_text("My custom license.\n")
        before = tree(self.project)
        result = self.install_group("docs")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Nothing was changed", result.stderr)
        self.assertEqual(tree(self.project), before)

    def test_failure_installing_group_documents_restores_updated_skills_and_documents(self):
        self.add_group_documents()
        self.assertEqual(self.install_group().returncode, 0)
        before = tree(self.project)
        path = self.skills / "versions/save/SKILL.md"
        path.write_text(path.read_text() + "\nNew workflow guidance.\n")
        (self.skills / "versions/CONTRACT.md").write_text("Updated rules.\n")
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "mv"
        wrapper.write_text('#!/bin/sh\ncase "$1" in */new/versions) exit 1;; esac\nexec "$VIBE_TEST_REAL_MV" "$@"\n')
        wrapper.chmod(0o755)
        result = self.run_installer(
            "--group", "versions", "--agent", "codex", "--force", "--skills-dir", str(self.skills),
            "--project", str(self.project), env_extra={
                "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"], "VIBE_TEST_REAL_MV": shutil.which("mv"),
            },
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(tree(self.project), before)

    def test_symlinked_group_document_and_resource_name_collision_are_refused(self):
        self.add_group_documents()
        (self.skills / "versions/CONTRACT.md").unlink()
        os.symlink("/etc/hosts", self.skills / "versions/CONTRACT.md")
        result = self.install_group()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("symbolic links", result.stderr)
        self.assertEqual(snapshot(self.project), set())
        (self.skills / "versions/CONTRACT.md").unlink()
        (self.skills / "versions/CONTRACT.md").write_text("Rules.\n")
        shutil.copytree(self.skills / "_shared/router", self.skills / "_shared/versions")
        result = self.install_group()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("conflict", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_group_and_shared_skills_are_flat_and_complete_for_every_agent(self):
        for agent, directory in AGENT_DIRS.items():
            with self.subTest(agent=agent):
                result = self.install_group(agent=agent)
                self.assertEqual(result.returncode, 0, result.stderr)
                dest = self.project / directory
                self.assertEqual({p.name for p in dest.iterdir()}, {"save", "status", "router"})
                for group, name in (("versions", "save"), ("versions", "status"),
                                    ("_shared", "router")):
                    self.assertEqual(tree(dest / name), tree(self.skills / group / name))
        self.assertFalse((self.project / "AGENTS.md").exists())
        self.assertFalse((self.project / ".gitly").exists())

    def test_a_second_group_reuses_shared_skills_and_preserves_the_first(self):
        self.assertEqual(self.install_group().returncode, 0)
        before = tree(self.project)
        result = self.install_group("docs")
        self.assertEqual(result.returncode, 0, result.stderr)
        after = tree(self.project)
        for path, content in before.items():
            self.assertEqual(after[path], content)
        self.assertTrue((self.project / ".agents/skills/write-docs/SKILL.md").is_file())
        self.assertIn("'router' is already installed", result.stdout)

    def test_individual_group_member_includes_only_it_and_shared_skills(self):
        result = self.install("save", "codex", skills_dir=self.skills)
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.project / ".agents/skills"
        self.assertEqual({p.name for p in dest.iterdir()}, {"save", "router"})

    def test_group_dry_run_lists_every_destination_without_writing(self):
        result = self.install_group("versions", "codex", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("save", "status", "router"):
            self.assertIn(".agents/skills/" + name, result.stdout)
        self.assertEqual(snapshot(self.project), set())

    def test_late_conflict_prevents_all_writes_including_shared_conflicts(self):
        for name in ("status", "router"):
            with self.subTest(name=name):
                dest = self.project / ".agents/skills" / name
                dest.mkdir(parents=True)
                (dest / "SKILL.md").write_text("My existing instructions.\n")
                before = tree(self.project)
                result = self.install_group()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("Nothing was changed", result.stderr)
                self.assertEqual(tree(self.project), before)
                shutil.rmtree(self.project / ".agents")

    def test_force_replaces_conflicting_members_and_keeps_unselected_groups(self):
        self.assertEqual(self.install_group("docs").returncode, 0)
        other = tree(self.project / ".agents/skills/write-docs")
        stale = self.project / ".agents/skills/status"
        stale.mkdir()
        (stale / "SKILL.md").write_text("Old version.\n")
        result = self.install_group("versions", "codex", "--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(tree(stale), tree(self.skills / "versions/status"))
        self.assertEqual(tree(self.project / ".agents/skills/write-docs"), other)

    def test_symlink_in_late_member_prevents_all_writes(self):
        os.symlink("/etc/hosts", str(self.skills / "versions/status/hosts"))
        result = self.install_group()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("symbolic links", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_failed_late_move_rolls_back_earlier_new_and_replaced_skills(self):
        dest = self.project / ".agents/skills/save"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("My existing save workflow.\n")
        before = tree(self.project)
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "mv"
        wrapper.write_text(
            '#!/bin/sh\ncase "$1" in */new/router) exit 1;; esac\n'
            'exec "$VIBE_TEST_REAL_MV" "$@"\n'
        )
        wrapper.chmod(0o755)
        result = self.run_installer(
            "--group", "versions", "--agent", "codex", "--force",
            "--skills-dir", str(self.skills), "--project", str(self.project),
            env_extra={"PATH": str(fake_bin) + os.pathsep + os.environ["PATH"],
                       "VIBE_TEST_REAL_MV": shutil.which("mv")},
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Previous copies were restored", result.stderr)
        self.assertEqual(tree(self.project), before)
        self.assertEqual(snapshot(self.tmpdir), set())
        self.assertFalse(list((self.project / ".agents").glob(".vibe-md-install.*")))

    def test_duplicate_names_across_groups_are_rejected(self):
        shutil.copytree(self.skills / "versions/save", self.skills / "docs/save")
        result = self.install_group()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("duplicate skill name", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_failed_recovery_preserves_backups_instead_of_cleaning_them_up(self):
        dest = self.project / ".agents/skills/save"
        dest.mkdir(parents=True)
        original = "My existing save workflow.\n"
        (dest / "SKILL.md").write_text(original)
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "mv"
        wrapper.write_text(
            '#!/bin/sh\ncase "$1" in */new/status|*/previous/save) exit 1;; esac\n'
            'exec "$VIBE_TEST_REAL_MV" "$@"\n'
        )
        wrapper.chmod(0o755)
        result = self.run_installer(
            "--group", "versions", "--agent", "codex", "--force",
            "--skills-dir", str(self.skills), "--project", str(self.project),
            env_extra={"PATH": str(fake_bin) + os.pathsep + os.environ["PATH"],
                       "VIBE_TEST_REAL_MV": shutil.which("mv")},
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("recovery is incomplete", result.stderr)
        backups = list((self.project / ".agents").glob(".vibe-md-install.*/previous/save/SKILL.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), original)

    def test_group_arguments_are_validated(self):
        for name in ("../versions", "/versions", "_shared", "Versions"):
            with self.subTest(name=name):
                result = self.install_group(name)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("invalid group name", result.stderr)
        result = self.install_group("missing")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("group 'missing' was not found", result.stderr)
        result = self.install_group("versions", "codex", "--skill", "save")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("choose --skill or --group", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_group_name_passed_to_skill_points_to_group_flag(self):
        result = self.install("versions", "codex", skills_dir=self.skills)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("skill 'versions' was not found, but there is a group with that name", result.stderr)
        self.assertIn("--group versions", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_skill_name_passed_to_group_points_to_skill_flag(self):
        result = self.install_group("save")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("group 'save' was not found, but there is a skill with that name", result.stderr)
        self.assertIn("--skill save", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_shared_skill_name_passed_to_group_gets_plain_message(self):
        result = self.install_group("router")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("group 'router' was not found.", result.stderr)
        self.assertNotIn("--skill router", result.stderr)
        self.assertEqual(snapshot(self.project), set())

    def test_uninstall_hint_does_not_suggest_installing(self):
        (self.project / ".agents/skills").mkdir(parents=True)
        before = snapshot(self.project)
        result = self.install_group("save", "codex", "--uninstall")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Use --skill save instead.", result.stderr)
        self.assertNotIn("Install", result.stderr)
        self.assertEqual(snapshot(self.project), before)

    def test_group_install_from_downloaded_archive(self):
        archive = self.root / "grouped.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(self.skills, arcname="vibe.md-main/skills")
        script = self.root / "downloaded/install.sh"
        script.parent.mkdir()
        shutil.copy(INSTALLER, script)
        result = self.run_installer(
            "--group=versions", "--agent=codex", script=script,
            env_extra={"VIBE_MD_ARCHIVE_URL": archive.as_uri()}, stdin_script=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.project / ".agents/skills"
        self.assertEqual({p.name for p in dest.iterdir()}, {"save", "status", "router"})
        self.assertEqual(snapshot(self.tmpdir), set())


class RemoteInstallTests(InstallerTestCase):
    """The installer run on its own downloads the collection. A local archive stands in for GitHub."""

    def setUp(self):
        super().setUp()
        self.lonely_script = self.root / "downloaded" / "install.sh"
        self.lonely_script.parent.mkdir()
        shutil.copy(str(INSTALLER), str(self.lonely_script))
        self.archive = self.root / "vibe.md-main.tar.gz"
        source = self.root / "archive-src" / "vibe.md-main"
        shutil.copytree(str(VALID), str(source / "skills"))
        with tarfile.open(str(self.archive), "w:gz") as tar:
            tar.add(str(source), arcname="vibe.md-main")
        self.env = {"VIBE_MD_ARCHIVE_URL": self.archive.as_uri()}

    def test_remote_list(self):
        result = self.run_installer("--list", script=self.lonely_script, env_extra=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("bundled-resources", result.stdout)
        self.assertEqual(snapshot(self.tmpdir), set(), "temporary download was not cleaned up")

    def test_remote_install_copies_complete_skill(self):
        result = self.run_installer(
            "--skill", "bundled-resources", "--agent", "codex", "--project", str(self.project),
            script=self.lonely_script, env_extra=self.env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.project / ".agents/skills/bundled-resources"
        self.assertEqual(tree(dest), tree(VALID / "bundled-resources"))
        self.assertEqual(snapshot(self.tmpdir), set())

    def test_piped_install(self):
        """Equivalent of: curl -fsSL .../install.sh | bash -s -- --skill ... --agent ..."""
        result = self.run_installer(
            "--skill", "basic-skill", "--agent", "cursor",
            script=self.lonely_script, env_extra=self.env, stdin_script=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / ".cursor/skills/basic-skill/SKILL.md").is_file())
        self.assertEqual(snapshot(self.tmpdir), set())

    def test_failed_download(self):
        env = {"VIBE_MD_ARCHIVE_URL": (self.root / "missing.tar.gz").as_uri()}
        result = self.run_installer(
            "--skill", "basic-skill", "--agent", "codex", script=self.lonely_script, env_extra=env,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("could not download", result.stderr)
        self.assertEqual(snapshot(self.project), set())
        self.assertEqual(snapshot(self.tmpdir), set())

    def test_corrupt_download(self):
        bad = self.root / "bad.tar.gz"
        bad.write_text("this is not an archive")
        result = self.run_installer(
            "--list", script=self.lonely_script, env_extra={"VIBE_MD_ARCHIVE_URL": bad.as_uri()},
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("could not be unpacked", result.stderr)
        self.assertEqual(snapshot(self.tmpdir), set())

    def test_archive_without_skills_directory(self):
        other = self.root / "other.tar.gz"
        src = self.root / "other-src" / "something-else"
        src.mkdir(parents=True)
        (src / "README.md").write_text("not vibe.md\n")
        with tarfile.open(str(other), "w:gz") as tar:
            tar.add(str(src), arcname="something-else")
        result = self.run_installer(
            "--list", script=self.lonely_script, env_extra={"VIBE_MD_ARCHIVE_URL": other.as_uri()},
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not look like the vibe.md repository", result.stderr)


@unittest.skipUnless(os.environ.get("VIBE_MD_INTEGRATION") == "1", "set VIBE_MD_INTEGRATION=1 to run")
class GitHubIntegrationTests(InstallerTestCase):
    """Downloads the real repository from GitHub. Requires network access."""

    def test_remote_list_from_github(self):
        lonely = self.root / "install.sh"
        shutil.copy(str(INSTALLER), str(lonely))
        result = self.run_installer("--list", script=lonely)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.tmpdir), set())

    def test_remote_unknown_skill_from_github(self):
        lonely = self.root / "install.sh"
        shutil.copy(str(INSTALLER), str(lonely))
        result = self.run_installer("--skill", "no-such-skill-xyz", "--agent", "codex", script=lonely)
        self.assertEqual(result.returncode, 1)
        self.assertIn("was not found", result.stderr)
        self.assertEqual(snapshot(self.project), set())


if __name__ == "__main__":
    unittest.main()
