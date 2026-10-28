"""The catalog is generated from the source tree and must work for any package.

These tests use generated packages instead of Gitly, so they describe platform
behavior: adding a skill or a package needs no code changes anywhere.
"""

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_packages", ROOT / "scripts/build-packages.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
INSTALLER = ROOT / "scripts/install.sh"


def write_skill(path, name, description="A skill used to test catalog generation. Use it when testing."):
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text("---\nname: {}\ndescription: {}\n---\n\nInstructions.\n".format(name, description))


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="vibe-md-catalog-"))
        self.skills = self.root / "skills"
        self.out = self.root / "dist" / "downloads"
        write_skill(self.skills / "_shared" / "router", "router")
        (self.skills / "alpha").mkdir(parents=True)
        (self.skills / "alpha" / "README.md").write_text(
            "---\ntitle: Alpha Tools\nsummary: Everything for the alpha domain.\ncategory: Testing\n"
            "maintainers: [octocat]\n---\n\n# Alpha\n\nIgnored because a summary is set.\n")
        write_skill(self.skills / "alpha" / "alpha-save", "alpha-save")
        write_skill(self.skills / "alpha" / "alpha-status", "alpha-status")

    def tearDown(self):
        shutil.rmtree(str(self.root))

    def build(self, *args):
        return subprocess.run(
            ["python3", str(ROOT / "scripts/build-packages.py"), "--skills-dir", str(self.skills),
             "--output-dir", str(self.out), "--ref", "test-ref", *args],
            capture_output=True, text=True,
        )

    def catalog(self):
        return json.loads((self.out / "catalog.json").read_text())

    def package(self, package_id):
        return next(p for p in self.catalog()["packages"] if p["id"] == package_id)

    # --- discovery ------------------------------------------------------------

    def test_every_package_is_discovered_and_described_from_the_source(self):
        result = self.build("--all")
        self.assertEqual(result.returncode, 0, result.stderr)
        catalog = self.catalog()
        self.assertEqual(catalog["source_ref"], "test-ref")
        self.assertEqual([p["id"] for p in catalog["packages"]], ["alpha"])
        alpha = self.package("alpha")
        self.assertEqual(alpha["title"], "Alpha Tools")
        self.assertEqual(alpha["summary"], "Everything for the alpha domain.")
        self.assertEqual(alpha["category"], "Testing")
        self.assertEqual(alpha["maintainers"], ["octocat"])
        self.assertEqual([s["name"] for s in alpha["skills"]], ["alpha-save", "alpha-status"])
        self.assertEqual(alpha["shared_skills"], ["router"])
        self.assertEqual(sorted(alpha["artifacts"]), sorted(builder.AGENTS))

    def test_metadata_falls_back_to_the_directory_and_readme(self):
        (self.skills / "alpha" / "README.md").write_text("# Alpha\n\nA plain README paragraph.\n\n## More\n")
        self.assertEqual(self.build("--all").returncode, 0)
        alpha = self.package("alpha")
        self.assertEqual(alpha["title"], "Alpha")
        self.assertEqual(alpha["summary"], "A plain README paragraph.")
        self.assertEqual(alpha["maintainers"], [])
        self.assertNotIn("category", alpha)

    def test_adding_a_skill_to_a_package_needs_no_code_change(self):
        self.assertEqual(self.build("--all").returncode, 0)
        write_skill(self.skills / "alpha" / "alpha-compare", "alpha-compare")
        self.assertEqual(self.build("--all").returncode, 0)
        self.assertEqual([s["name"] for s in self.package("alpha")["skills"]],
                         ["alpha-compare", "alpha-save", "alpha-status"])

    def test_adding_a_new_package_needs_no_code_change(self):
        (self.skills / "security").mkdir()
        (self.skills / "security" / "README.md").write_text("# Security\n\nAudit and harden a project.\n")
        for name in ("security-audit", "security-secrets", "security-dependencies"):
            write_skill(self.skills / "security" / name, name)
        self.assertEqual(self.build("--all").returncode, 0)
        self.assertEqual([p["id"] for p in self.catalog()["packages"]], ["alpha", "security"])
        security = self.package("security")
        self.assertEqual(len(security["skills"]), 3)
        with zipfile.ZipFile(self.out / security["artifacts"]["claude-code"]["file"]) as archive:
            names = archive.namelist()
        self.assertIn("security-install/skills/security-audit/SKILL.md", names)
        self.assertIn("security-install/skills/router/SKILL.md", names)
        self.assertFalse(any("alpha" in name for name in names))

    # --- standalone skills are packages of one ------------------------------------

    def test_a_standalone_skill_is_published_as_a_package_of_one(self):
        write_skill(self.skills / "lonely", "lonely", "Does one thing for the user. Use it when testing standalone skills.")
        self.assertEqual(builder.discover_packages(self.skills), ["alpha", "lonely"])
        self.assertEqual(self.build("--all").returncode, 0)
        lonely = self.package("lonely")
        self.assertEqual(lonely["kind"], "standalone")
        self.assertEqual(self.package("alpha")["kind"], "group")
        self.assertEqual([s["name"] for s in lonely["skills"]], ["lonely"])
        self.assertEqual(lonely["summary"], "Does one thing for the user. Use it when testing standalone skills.")
        self.assertEqual(lonely["title"], "Lonely")
        self.assertEqual(lonely["documentation"], "skills/lonely/SKILL.md")
        self.assertEqual(sorted(lonely["artifacts"]), sorted(builder.AGENTS))
        with zipfile.ZipFile(self.out / lonely["artifacts"]["codex"]["file"]) as archive:
            names = archive.namelist()
            guide = archive.read("lonely-install/INSTALL.md").decode()
        self.assertIn("lonely-install/skills/lonely/SKILL.md", names)
        self.assertIn("lonely-install/skills/router/SKILL.md", names)
        self.assertFalse(any("alpha" in name for name in names))
        self.assertIn("no group resources directory", guide)
        self.assertEqual(self.build("--verify", str(self.out)).returncode, 0)

    def test_a_standalone_package_installs_by_skill_name_next_to_a_group(self):
        write_skill(self.skills / "lonely", "lonely")
        self.assertEqual(self.build("--all").returncode, 0)
        project = self.root / "project"
        project.mkdir()
        for flag, name in (("--group", "alpha"), ("--skill", "lonely")):
            result = subprocess.run(
                ["bash", str(INSTALLER), flag, name, "--agent", "cursor", "--skills-dir", str(self.skills), "--project", str(project)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name for p in (project / ".cursor/skills").iterdir()}, {"alpha", "alpha-save", "alpha-status", "lonely", "router"})
        self.assertTrue((project / ".cursor/.vibe-md/lonely.receipt").is_file())

    def test_group_archives_do_not_change_when_standalone_support_exists(self):
        # The group "how to install" text and layout are what existing Gitly downloads contain.
        self.assertEqual(self.build("--all").returncode, 0)
        with zipfile.ZipFile(self.out / self.package("alpha")["artifacts"]["codex"]["file"]) as archive:
            guide = archive.read("alpha-install/INSTALL.md").decode()
        self.assertIn("including the group resources directory `.agents/skills/alpha/` when present", guide)

    def test_unlisted_files_in_the_output_directory_are_detected(self):
        self.assertEqual(self.build("--all").returncode, 0)
        (self.out / "retired-codex.zip").write_bytes(b"old")
        result = self.build("--verify", str(self.out))
        self.assertEqual(result.returncode, 1)
        self.assertIn("unlisted file", result.stdout)

    # --- consistency ----------------------------------------------------------

    def test_a_fresh_build_verifies_against_its_source(self):
        self.assertEqual(self.build("--all").returncode, 0)
        result = self.build("--verify", str(self.out))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_tampered_archives_are_detected(self):
        self.assertEqual(self.build("--all").returncode, 0)
        archive = self.out / self.package("alpha")["artifacts"]["codex"]["file"]
        archive.write_bytes(archive.read_bytes() + b"x")
        result = self.build("--verify", str(self.out))
        self.assertEqual(result.returncode, 1)
        self.assertIn("checksum mismatch", result.stdout)

    def test_a_catalog_that_no_longer_matches_the_source_is_detected(self):
        self.assertEqual(self.build("--all").returncode, 0)
        write_skill(self.skills / "alpha" / "alpha-extra", "alpha-extra")
        result = self.build("--verify", str(self.out))
        self.assertEqual(result.returncode, 1)
        self.assertIn("differ from the source", result.stdout)

    def test_the_catalog_and_every_manifest_name_the_same_revision(self):
        self.assertEqual(self.build("--all").returncode, 0)
        manifest = json.loads((self.out / "alpha-manifest.json").read_text())
        self.assertEqual(manifest["source_ref"], self.catalog()["source_ref"])
        for agent, artifact in self.package("alpha")["artifacts"].items():
            digest = hashlib.sha256((self.out / artifact["file"]).read_bytes()).hexdigest()
            self.assertEqual(digest, artifact["sha256"])
            self.assertEqual(digest, manifest["agents"][agent]["sha256"])

    def test_identical_sources_give_identical_catalogs(self):
        self.assertEqual(self.build("--all").returncode, 0)
        first = (self.out / "catalog.json").read_bytes()
        shutil.rmtree(str(self.out))
        self.assertEqual(self.build("--all").returncode, 0)
        self.assertEqual((self.out / "catalog.json").read_bytes(), first)

    def test_a_failed_build_leaves_no_partial_output(self):
        write_skill(self.skills / "broken" / "Not_A_Valid_Name", "broken-one")
        result = self.build("--all")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.out.exists())
        self.assertEqual([p.name for p in (self.root / "dist").iterdir()], [])

    def test_a_failed_rebuild_keeps_the_previous_published_files(self):
        self.assertEqual(self.build("--all").returncode, 0)
        before = {p.name: p.read_bytes() for p in self.out.iterdir()}
        write_skill(self.skills / "alpha" / "Not_A_Valid_Name", "alpha-broken")
        self.assertNotEqual(self.build("--all").returncode, 0)
        self.assertEqual({p.name: p.read_bytes() for p in self.out.iterdir()}, before)

    # --- installing what was built --------------------------------------------

    def test_packages_from_the_catalog_install_side_by_side(self):
        (self.skills / "security").mkdir()
        (self.skills / "security" / "README.md").write_text("# Security\n\nAudit a project.\n")
        write_skill(self.skills / "security" / "security-audit", "security-audit")
        self.assertEqual(self.build("--all").returncode, 0)
        project = self.root / "project"
        project.mkdir()
        for package in ("alpha", "security"):
            result = subprocess.run(
                ["bash", str(INSTALLER), "--group", package, "--agent", "claude-code",
                 "--skills-dir", str(self.skills), "--project", str(project)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        installed = {p.name for p in (project / ".claude/skills").iterdir()}
        self.assertEqual(installed, {"alpha", "alpha-save", "alpha-status", "security", "security-audit", "router"})

    # --- one agent table, not three ---------------------------------------------

    def test_the_installer_and_the_builder_agree_about_agents(self):
        help_text = subprocess.run(["bash", str(INSTALLER), "--help"], capture_output=True, text=True).stdout
        installer = dict(re.findall(r"^\s{2}(\S+)\s+.+?\s+(\.\S+?)/<skill>/$", help_text, re.M))
        self.assertEqual(installer, {agent: destination for agent, (_, destination) in builder.AGENTS.items()})

    def test_the_real_repository_catalog_is_consistent(self):
        output = self.root / "real"
        result = subprocess.run(
            ["python3", str(ROOT / "scripts/build-packages.py"), "--all", "--output-dir", str(output), "--ref", "test-ref"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        verify = subprocess.run(
            ["python3", str(ROOT / "scripts/build-packages.py"), "--verify", str(output)], capture_output=True, text=True)
        self.assertEqual(verify.returncode, 0, verify.stdout)
        ids = [p["id"] for p in json.loads((output / "catalog.json").read_text())["packages"]]
        self.assertIn("gitly", ids)


if __name__ == "__main__":
    unittest.main()
