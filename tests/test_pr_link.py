"""Tests for docs/skill-contribution-check/pr_link.py, the Pull Request link builder."""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs/skill-contribution-check/pr_link.py"
spec = importlib.util.spec_from_file_location("pr_link", SCRIPT)
pr_link = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr_link)


class ParseRemoteTests(unittest.TestCase):
    def test_github_remote_forms(self):
        for url in ("https://github.com/octo/vibe.md.git", "https://github.com/octo/vibe.md",
                    "git@github.com:octo/vibe.md.git", "ssh://git@github.com/octo/vibe.md.git",
                    "https://octo:token@github.com/octo/vibe.md.git"):
            self.assertEqual(pr_link.parse_remote(url), ("octo", "vibe.md"), url)

    def test_other_hosts_are_refused(self):
        for url in ("https://gitlab.com/octo/vibe.md.git", "https://github.com.evil.example/octo/vibe.md",
                    "https://github.com/octo/vibe.md/../../x", "/local/path", "",
                    "https://evil.example#@github.com/octo/vibe.md", "https://evil.example?x@github.com/octo/vibe.md",
                    "https://github.com/octo/..", "https://github.com/octo/a..b", "https://github.com:8443/octo/vibe.md"):
            self.assertIsNone(pr_link.parse_remote(url), url)


class BuildUrlTests(unittest.TestCase):
    def test_special_characters_cannot_change_the_link(self):
        body = "## Summary\n\nA & B #1 ?x=1 100% done + more\n- [x] ok"
        url = pr_link.build_url("octo", "my-fork", "feat/a&b#c", body)
        parts = urlsplit(url)
        self.assertEqual(parts.netloc, "github.com")
        self.assertEqual(parts.fragment, "")
        self.assertEqual(unquote(parts.path), "/vibe-md/vibe.md/compare/main...octo:my-fork:feat/a&b#c")
        query = parse_qs(parts.query)
        self.assertEqual(sorted(query), ["body", "quick_pull"])
        self.assertEqual(query["body"], [body])

    def test_clone_of_vibe_md_uses_the_plain_branch(self):
        url = pr_link.build_url("vibe-md", "vibe.md", "add-x", "b")
        self.assertIn("/compare/main...add-x?", url)


class GhCommandTests(unittest.TestCase):
    def test_values_are_checked_and_quoted(self):
        command = pr_link.gh_command("octo", "fork", "add-x", "hello-notes", "/tmp/a b/vibe-md-pr-body.md")
        self.assertEqual(command, "gh pr create --repo vibe-md/vibe.md --base main --head octo:add-x "
                                  "--title 'Add hello-notes skill' --body-file '/tmp/a b/vibe-md-pr-body.md'")

    def test_unexpected_characters_give_no_command(self):
        self.assertIsNone(pr_link.gh_command("octo", "fork", "add-x", "x'; rm -rf ~; '", "f"))
        self.assertIsNone(pr_link.gh_command("octo", "fork", "a$(id)", "ok-name", "f"))


@unittest.skipIf(shutil.which("git") is None, "git is not installed")
class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, str(self.tmp))
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.env = env
        self.git("init", "-q", "-b", "add-demo")
        self.git("-c", "user.name=t", "-c", "user.email=t@example.test", "commit", "-q", "--allow-empty", "-m", "x")
        self.git("remote", "add", "origin", "https://octo:ghp_secrettoken@github.com/octo/vibe.md.git")

    def git(self, *args):
        subprocess.run(["git"] + list(args), cwd=str(self.tmp), env=self.env, check=True)

    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT)] + list(args), cwd=str(self.tmp), env=self.env,
                              capture_output=True, text=True)

    def test_prints_link_from_default_file_and_warns_when_not_pushed(self):
        (self.tmp / ".git/vibe-md-pr-body.md").write_text("## Summary\n\nHi & bye\n", encoding="utf-8")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("is not on 'origin' yet", result.stdout)
        self.assertIn("https://github.com/vibe-md/vibe.md/compare/main...octo:vibe.md:add-demo?quick_pull=1&body=",
                      result.stdout)
        self.assertIn("Hi%20%26%20bye", result.stdout)
        self.assertNotIn("ghp_secrettoken", result.stdout + result.stderr)

    def test_missing_file_and_long_body_give_no_link(self):
        self.assertEqual(self.run_script().returncode, 1)
        (self.tmp / ".git/vibe-md-pr-body.md").write_text("x" * 9000, encoding="utf-8")
        result = self.run_script()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Too long for a link", result.stdout)
        self.assertNotIn("https://", result.stdout)

    def test_non_github_remote_gives_no_link(self):
        (self.tmp / ".git/vibe-md-pr-body.md").write_text("b", encoding="utf-8")
        self.git("remote", "set-url", "origin", "https://gitlab.com/octo/vibe.md.git")
        result = self.run_script()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("https://github.com/vibe-md", result.stdout)


if __name__ == "__main__":
    unittest.main()
