#!/usr/bin/env python3
"""Refresh the generated skill index in skills/README.md."""

import argparse
import html
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_packages", ROOT / "scripts/build-packages.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

START = "<!-- skills-index:start -->"
END = "<!-- skills-index:end -->"


def text(value):
    """Render metadata as plain text, not contributor-supplied Markdown or HTML."""
    return re.sub(r"([\\`*_\[\]~])", r"\\\1", html.escape(" ".join(str(value).split()), quote=False))


def render_index(skills_dir):
    groups, standalone = [], []
    for name in builder.discover_packages(skills_dir):
        package = builder.describe_package(skills_dir, name, {})
        if package["kind"] == "standalone":
            standalone.append(f'- [{name}]({name}/SKILL.md) — {text(package["summary"])}')
        else:
            group = [f'### [{name}]({name}/)', '']
            if package['summary']:
                group.extend([text(package['summary']), ''])
            for skill in package['skills']:
                group.append(f'- [{skill["name"]}]({name}/{skill["name"]}/SKILL.md) — {text(skill["description"])}')
            groups.append('\n'.join(group))
    sections = groups
    if standalone:
        sections.append('### Standalone skills\n\n' + '\n'.join(standalone))
    return '\n\n'.join(sections) if sections else 'No skills have been published yet.'


def update_readme(skills_dir):
    path = skills_dir / 'README.md'
    content = path.read_text(encoding='utf-8')
    if content.count(START) != 1 or content.count(END) != 1 or content.index(START) > content.index(END):
        raise ValueError('README must contain exactly one ordered pair of skills-index markers')
    before, remaining = content.split(START, 1)
    _, after = remaining.split(END, 1)
    updated = before + START + '\n\n' + render_index(skills_dir) + '\n\n' + END + after
    if updated != content:
        path.write_text(updated, encoding='utf-8')
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-dir', type=Path, default=ROOT / 'skills')
    args = parser.parse_args()
    print('Updated skill index.' if update_readme(args.skills_dir) else 'Skill index is up to date.')


if __name__ == '__main__':
    main()
