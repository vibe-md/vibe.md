"""AGENTS.md tells coding agents where the contribution check lives. Keep its links working."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)#\s]+)\)")


class AgentsMdTests(unittest.TestCase):
    def test_every_local_link_in_agents_md_exists(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        targets = [target for target in LINK.findall(text) if "://" not in target]
        self.assertIn("docs/skill-contribution-check/SKILL.md", targets)
        for target in targets:
            self.assertTrue((ROOT / target).is_file(), "AGENTS.md links to a missing file: " + target)

    def test_claude_md_imports_agents_md(self):
        self.assertEqual((ROOT / "CLAUDE.md").read_text(encoding="utf-8").strip(), "@AGENTS.md")

    def test_contribution_check_is_not_a_published_skill(self):
        self.assertFalse((ROOT / "skills" / "skill-contribution-check").exists())


if __name__ == "__main__":
    unittest.main()
