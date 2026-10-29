"""Classifications are reproducible and explicit metadata overrides suggestions."""
import importlib.util
import sys
import tempfile
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from categories import infer_categories
spec = importlib.util.spec_from_file_location('builder', ROOT / 'scripts/build-packages.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class CategoryTests(unittest.TestCase):
    def test_representative_and_ambiguous_descriptions(self):
        cases = {
            'Checks credentials and API keys for leaks.': ['Security'],
            'Plans database schema changes that are reversible and never silently destructive.': ['Database', 'Security'],
            'Writes unit tests for frontend UI components.': ['Frontend', 'Testing'],
            'Assists with an unspecified project task.': [],
            'Helps an AI coding agent handle everyday work.': [],
            'Reviews Git branches and commits.': ['Version Control'],
        }
        for description, expected in cases.items():
            with self.subTest(description=description):
                self.assertEqual(infer_categories(description), expected)

    def test_invalid_overrides_are_rejected_by_validator(self):
        with tempfile.TemporaryDirectory() as temp:
            skills = Path(temp)
            skill = skills / 'demo'
            skill.mkdir()
            path = skill / 'SKILL.md'
            for value, expected in [('Database, Security', 0), ('Database, Imaginary', 1), ('Database, Database', 1), ('Database, Security, Backend, DevOps', 1)]:
                with self.subTest(value=value):
                    path.write_text(f'---\nname: demo\ndescription: Checks documentation for errors and clarity.\nmetadata:\n  categories: {value}\n---\n\nInstructions.\n')
                    result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate-skills.py'), '--skills-dir', str(skills)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_explicit_categories_override_suggestions_and_legacy_category(self):
        with tempfile.TemporaryDirectory() as temp:
            skills = Path(temp)
            skill = skills / 'demo'
            skill.mkdir()
            (skill / 'SKILL.md').write_text('---\nname: demo\ndescription: Checks credentials for accidental exposure.\nmetadata:\n  category: Security\n  categories: Database, Backend\n---\n\nInstructions.\n')
            package = builder.describe_package(skills, 'demo', {})
            self.assertEqual(package['category'], 'Security')
            self.assertEqual(package['categories'], ['Database', 'Backend'])


if __name__ == '__main__':
    unittest.main()
