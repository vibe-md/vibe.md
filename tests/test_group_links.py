"""Grouped resource links behave identically in installed skills and ZIPs."""

import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GroupLinkTests(unittest.TestCase):
    def test_install_and_zip_preserve_code_and_resolve_shared_links(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skills = root / 'skills'
            skill = skills / 'docs' / 'docs-demo'
            skill.mkdir(parents=True)
            (skill.parent / 'CONTRACT.md').write_text('Shared rules.\n')
            (skill.parent / 'README.md').write_text('---\ncategories: Testing\n---\n')
            project = root / 'project'
            project.mkdir()
            source = ('---\nname: docs-demo\ndescription: Demonstrates shared documentation links.\n---\n'
                      '\n[direct](../CONTRACT.md)\n[reference][ref]\n[ref]: <../CONTRACT.md> "Rules"\n'
                      '`[inline](../CONTRACT.md)` and ``[long](../CONTRACT.md) ` code``\n'
                      '````markdown\n[example](../CONTRACT.md)\n```\n[still-code](../CONTRACT.md)\n````\n'
                      '~~~\n[ref]: ../CONTRACT.md\n~~~\n')
            (skill / 'SKILL.md').write_text(source)
            validation = subprocess.run([sys.executable, str(ROOT / 'scripts/validate-skills.py'), '--skills-dir', str(skills)], capture_output=True, text=True)
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
            result = subprocess.run(['bash', str(ROOT / 'scripts/install.sh'), '--skill', 'docs-demo', '--agent', 'codex', '--skills-dir', str(skills), '--project', str(project)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = (project / '.agents/skills/docs-demo/SKILL.md').read_text()
            expected = source.replace('[direct](../CONTRACT.md)', '[direct](../docs/CONTRACT.md)').replace('[ref]: <../CONTRACT.md> "Rules"', '[ref]: <../docs/CONTRACT.md> "Rules"')
            self.assertEqual(installed, expected)
            self.assertTrue((project / '.agents/skills/docs/CONTRACT.md').exists())
            output = root / 'downloads'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/build-packages.py'), '--group', 'docs', '--skills-dir', str(skills), '--output-dir', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(output / 'docs-codex.zip') as archive:
                self.assertEqual(archive.read('docs-install/skills/docs-demo/SKILL.md').decode(), expected)
                self.assertEqual(archive.read('docs-install/skills/docs/CONTRACT.md'), b'Shared rules.\n')
            (skill / 'SKILL.md').write_text('---\nname: docs-demo\ndescription: Demonstrates shared documentation links.\n---\n\n[ref]: ../CONTRACT.md\n')
            (skill.parent / 'CONTRACT.md').unlink()
            validation = subprocess.run([sys.executable, str(ROOT / 'scripts/validate-skills.py'), '--skills-dir', str(skills)], capture_output=True, text=True)
            self.assertEqual(validation.returncode, 1)
            self.assertIn('../CONTRACT.md', validation.stdout)
            self.assertIn('does not exist', validation.stdout)

    def test_reference_paths_outside_group_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            skills = Path(temp) / 'skills'
            skill = skills / 'docs' / 'docs-demo'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('---\nname: docs-demo\ndescription: Demonstrates shared documentation links.\n---\n\n[ref]: ../../outside.md\n')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate-skills.py'), '--skills-dir', str(skills)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('points outside the skill directory', result.stdout)


if __name__ == '__main__':
    unittest.main()
