"""The selection scenarios in evals/ must be well-formed and refer to real skills.

This does not evaluate a model. It only keeps the scenario file honest as skills
are added, renamed, or removed.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"positive", "ambiguous", "negative"}


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "evals/scenarios.json").read_text(encoding="utf-8"))
        self.scenarios = self.data["scenarios"]
        self.skills = {p.parent.name for p in (ROOT / "skills").glob("**/SKILL.md")}

    def test_every_scenario_is_complete(self):
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario["id"]):
                self.assertTrue(scenario["prompt"].strip())
                self.assertIn(scenario["kind"], KINDS)
                self.assertRegex(scenario["language"], r"^[a-z]{2}$")
                self.assertIsInstance(scenario["expected"], list)

    def test_ids_and_prompts_are_unique(self):
        self.assertEqual(len({s["id"] for s in self.scenarios}), len(self.scenarios))
        self.assertEqual(len({s["prompt"] for s in self.scenarios}), len(self.scenarios))

    def test_expected_skills_exist(self):
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario["id"]):
                self.assertTrue(set(scenario["expected"]) <= self.skills, scenario["expected"])

    def test_the_kinds_have_the_right_expectations(self):
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario["id"]):
                if scenario["kind"] == "negative":
                    self.assertEqual(scenario["expected"], [])
                elif scenario["kind"] == "positive":
                    self.assertEqual(len(scenario["expected"]), 1)
                else:
                    self.assertGreaterEqual(len(scenario["expected"]), 2)

    def test_the_suite_includes_every_kind_and_hebrew(self):
        self.assertEqual({s["kind"] for s in self.scenarios}, KINDS)
        self.assertIn("he", {s["language"] for s in self.scenarios})


if __name__ == "__main__":
    unittest.main()
