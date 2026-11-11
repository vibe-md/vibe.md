"""Tests for scripts/validate-skills.py.

Run with: python3 -m unittest discover -s tests -v
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate-skills.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures"


def run_validator(*args, env_extra=None, cwd=None):
    env = dict(os.environ)
    env.pop("GITHUB_ACTIONS", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(VALIDATOR)] + list(args),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd or REPO_ROOT),
    )


class ValidCollectionTests(unittest.TestCase):
    def test_valid_fixtures_pass(self):
        result = run_validator("--skills-dir", str(FIXTURES / "valid"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("All 2 skill(s) are valid.", result.stdout)

    def test_repository_skills_directory_is_valid(self):
        result = run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_empty_collection_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_validator("--skills-dir", tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("No skills found", result.stdout)

    def test_readme_and_hidden_entries_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "README.md").write_text("# Skills\n")
            Path(tmp, ".DS_Store").write_text("")
            result = run_validator("--skills-dir", tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_skills_directory_is_a_usage_error(self):
        result = run_validator("--skills-dir", str(FIXTURES / "does-not-exist"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("skills directory not found", result.stderr)


class InvalidCollectionTests(unittest.TestCase):
    """Each fixture under tests/fixtures/invalid/ must fail with a specific message."""

    CASES = {
        "missing-skill-md": "missing SKILL.md",
        "invalid-yaml": "YAML frontmatter is invalid",
        "no-frontmatter": "must start with YAML frontmatter",
        "missing-name": "missing required field 'name'",
        "missing-description": "missing required field 'description'",
        "short-description": "'description' is too short",
        "invalid-name": "is not lowercase kebab-case",
        "name-mismatch": "does not match the directory name 'folder-name'",
        "duplicate-names": "duplicate skill name 'alpha'",
        "missing-resource": "points to a file that does not exist",
        "unsafe-path": "points outside the skill directory",
        "stray-file": "unexpected file",
        "empty-body": "has no instructions after the frontmatter",
    }

    def test_every_invalid_fixture_has_a_case(self):
        fixtures = {p.name for p in (FIXTURES / "invalid").iterdir() if p.is_dir()}
        self.assertEqual(fixtures, set(self.CASES))

    def test_invalid_fixtures_fail(self):
        for case, expected in self.CASES.items():
            with self.subTest(case=case):
                result = run_validator("--skills-dir", str(FIXTURES / "invalid" / case))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(expected, result.stdout)
                self.assertIn("Validation failed", result.stdout)

    def test_absolute_link_is_rejected(self):
        result = run_validator("--skills-dir", str(FIXTURES / "invalid" / "unsafe-path"))
        self.assertIn("uses an absolute path", result.stdout)

    def test_errors_include_line_numbers_for_links(self):
        result = run_validator("--skills-dir", str(FIXTURES / "invalid" / "missing-resource"))
        self.assertIn("missing-resource/SKILL.md:8:", result.stdout)


class GeneratedCaseTests(unittest.TestCase):
    """Cases that are easier to build at test time than to store in Git."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.skills = Path(self.tmp, "skills")
        self.skills.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write_skill(self, name, frontmatter=None, body="# Skill\n\nInstructions.\n"):
        skill_dir = self.skills / name
        skill_dir.mkdir(parents=True)
        if "/" not in name and frontmatter is not None and "metadata:" not in frontmatter:
            frontmatter += "metadata:\n  categories: Testing\n"
        group = skill_dir.parent
        if group != self.skills and group.name != "_shared" and not (group / "README.md").exists():
            (group / "README.md").write_text("---\ncategories: Testing\n---\n\n# {}\n".format(group.name))
        if frontmatter is None:
            frontmatter = (
                "name: {}\ndescription: A generated skill used by the vibe.md validator tests.\nmetadata:\n  categories: Testing\n".format(name)
            )
        (skill_dir / "SKILL.md").write_text("---\n{}---\n\n{}".format(frontmatter, body))
        return skill_dir

    def test_symlink_inside_skill_is_rejected(self):
        skill_dir = self.write_skill("has-symlink")
        os.symlink("/etc/hosts", str(skill_dir / "hosts"))
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("symbolic links are not allowed", result.stdout)

    def test_wrong_case_skill_file_gets_a_hint(self):
        skill_dir = self.skills / "lower-case-file"
        skill_dir.mkdir()
        (skill_dir / "skill.md").write_text("---\nname: x\n---\n")
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing SKILL.md", result.stdout)

    def test_name_rules(self):
        bad_names = ["-leading", "trailing-", "double--hyphen", "UPPER", "under_score", "a" * 65]
        for name in bad_names:
            with self.subTest(name=name):
                shutil.rmtree(str(self.skills))
                self.skills.mkdir()
                frontmatter = "name: {}\ndescription: A generated skill used by the vibe.md validator tests.\nmetadata:\n  categories: Testing\n".format(name)
                self.write_skill("some-dir", frontmatter=frontmatter)
                result = run_validator("--skills-dir", str(self.skills))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertTrue(
                    "not lowercase kebab-case" in result.stdout or "the maximum is 64" in result.stdout,
                    result.stdout,
                )

    def test_optional_field_types_are_checked(self):
        frontmatter = (
            "name: typed-fields\n"
            "description: A generated skill used by the vibe.md validator tests.\n"
            "metadata: not-a-mapping\n"
            "license: 42\n"
        )
        self.write_skill("typed-fields", frontmatter=frontmatter)
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("'metadata' must be a mapping", result.stdout)
        self.assertIn("'license' must be a string", result.stdout)

    def test_unknown_fields_are_allowed(self):
        frontmatter = (
            "name: agent-specific\n"
            "description: A generated skill used by the vibe.md validator tests.\n"
            "disable-model-invocation: true\n"
        )
        self.write_skill("agent-specific", frontmatter=frontmatter)
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_long_skill_produces_warning_not_error(self):
        self.write_skill("long-skill", body="line\n" * 600)
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("warning:", result.stdout)

    def test_github_annotations_in_ci(self):
        self.write_skill("bad-name-dir", frontmatter="name: Bad\ndescription: x\n")
        result = run_validator("--skills-dir", str(self.skills), env_extra={"GITHUB_ACTIONS": "true"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("::error file=", result.stdout)

    def test_new_contribution_is_discovered_without_configuration(self):
        """A contributor adds skills/<new-skill>/ to a copy of the repo; nothing else changes."""
        repo = Path(self.tmp, "repo copy")
        shutil.copytree(str(REPO_ROOT / "scripts"), str(repo / "scripts"))
        shutil.copytree(str(REPO_ROOT / "skills"), str(repo / "skills"))
        shutil.copytree(str(FIXTURES / "valid" / "basic-skill"), str(repo / "skills" / "basic-skill"))
        result = subprocess.run(
            [sys.executable, str(repo / "scripts" / "validate-skills.py")],
            capture_output=True,
            text=True,
            cwd=str(repo),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("skill(s) are valid", result.stdout)

    def test_groups_shared_skills_and_standalone_skills_are_all_validated(self):
        for path in ("_shared/router", "versions/save", "versions/status", "docs/write-docs", "standalone"):
            self.write_skill(path, frontmatter="name: {}\ndescription: A grouped workflow used for validation tests.\n".format(Path(path).name))
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("All 5 skill(s) are valid", result.stdout)

    def test_duplicate_names_across_groups_are_rejected(self):
        for group in ("first", "second"):
            self.write_skill(group + "/same", frontmatter="name: same\ndescription: A grouped workflow used for validation tests.\n")
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate skill name 'same'", result.stdout)

    def test_group_does_not_hide_malformed_members_or_unsafe_links(self):
        skill = self.write_skill("versions/good", frontmatter="name: good\ndescription: A grouped workflow used for validation tests.\n",
                                 body="Read [another skill](../broken/SKILL.md).\n")
        (skill.parent / "broken").mkdir()
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing SKILL.md", result.stdout)
        self.assertIn("points outside the skill directory", result.stdout)

    def test_symlinked_group_is_rejected(self):
        target = Path(self.tmp, "outside")
        shutil.copytree(FIXTURES / "valid", target)
        os.symlink(target, self.skills / "linked")
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("symbolic links are not allowed", result.stdout)

    def test_invalid_group_name_is_rejected(self):
        self.write_skill("Bad_Group/good", frontmatter="name: good\ndescription: A grouped workflow used for validation tests.\n")
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("group names must use lowercase kebab-case", result.stdout)

    def test_group_contract_and_license_links_are_valid_but_missing_documents_fail(self):
        skill = self.write_skill("versions/good", frontmatter="name: good\ndescription: A grouped workflow used for validation tests.\n",
                                 body="Read [rules](../CONTRACT.md) and [license](../LICENSE).\n")
        (skill.parent / "CONTRACT.md").write_text("Shared rules.\n")
        (skill.parent / "LICENSE").write_text("License.\n")
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 0, result.stdout)
        (skill.parent / "CONTRACT.md").unlink()
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not exist", result.stdout)

    def test_shared_documents_cannot_be_symlinks_or_collide_with_skill_names(self):
        skill = self.write_skill("versions/good", frontmatter="name: good\ndescription: A grouped workflow used for validation tests.\n",
                                 body="Read [rules](../CONTRACT.md).\n")
        os.symlink("/etc/hosts", skill.parent / "CONTRACT.md")
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("symbolic links", result.stdout)
        (skill.parent / "CONTRACT.md").unlink()
        (skill.parent / "CONTRACT.md").write_text("Rules.\n")
        self.write_skill("other/versions", frontmatter="name: versions\ndescription: A grouped workflow used for validation tests.\n")
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("conflicts with a group resources directory", result.stdout)

    def test_common_router_stays_self_contained(self):
        skill = self.write_skill("_shared/router", frontmatter="name: router\ndescription: A common router used for validation tests.\n",
                                 body="Read [rules](../CONTRACT.md).\n")
        (skill.parent / "CONTRACT.md").write_text("Rules.\n")
        result = run_validator("--skills-dir", str(self.skills))
        self.assertEqual(result.returncode, 1)
        self.assertIn("points outside the skill directory", result.stdout)


if __name__ == "__main__":
    unittest.main()
