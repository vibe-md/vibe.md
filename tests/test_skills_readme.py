"""The README index reflects packages without requiring contributors to edit it."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('skills_readme', ROOT / 'scripts/update-skills-readme.py')
index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(index)


class SkillsReadmeTests(unittest.TestCase):
    def test_index_tracks_standalone_and_group_and_preserves_other_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp)
            readme = skills / 'README.md'
            readme.write_text('Before\n' + index.START + '\nold\n' + index.END + '\nAfter\n')
            for path, name, description in [
                ('solo', 'solo', 'A standalone skill for testing.'),
                ('group/group-demo', 'group-demo', 'A grouped skill for testing.'),
                ('_shared/router', 'router', 'The shared router for testing.'),
            ]:
                directory = skills / path
                directory.mkdir(parents=True)
                (directory / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: {description}\n---\nBody\n')
            self.assertTrue(index.update_readme(skills))
            content = readme.read_text()
            self.assertTrue(content.startswith('Before\n'))
            self.assertTrue(content.endswith('\nAfter\n'))
            self.assertIn('[solo](solo/SKILL.md) — A standalone skill for testing.', content)
            self.assertIn('[group-demo](group/group-demo/SKILL.md) — A grouped skill for testing.', content)
            self.assertNotIn('_shared', content)
            self.assertFalse(index.update_readme(skills))
            (skills / 'solo/SKILL.md').unlink()
            self.assertTrue(index.update_readme(skills))
            self.assertNotIn('[solo]', readme.read_text())

    def test_metadata_is_rendered_as_text_and_bad_markers_fail(self):
        self.assertEqual(index.text('<img src=x> [link](https://example.com)'), '&lt;img src=x&gt; \\[link\\](https://example.com)')
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp)
            readme = skills / 'README.md'
            readme.write_text('Missing markers')
            with self.assertRaises(ValueError):
                index.update_readme(skills)
            self.assertEqual(readme.read_text(), 'Missing markers')


if __name__ == '__main__':
    unittest.main()
