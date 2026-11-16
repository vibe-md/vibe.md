# Pytest Leak Detector

Review pytest fixtures for reliable teardown, then check for likely leftover test
artifacts after a test run. The agent instructions are in [SKILL.md](SKILL.md);
the bundled scanner is [scripts/check_leaks.py](scripts/check_leaks.py).

## What it checks

The scanner reports regular files whose extensions are `.db`, `.sqlite`, `.log`,
or `.tmp`, and files whose names start with `temp_`, `test_out_`, or `dump_`.
It prunes directories named `.git`, `.venv`, `venv`, `env`, `__pycache__`,
`.pytest_cache`, `.tox`, `.nox`, `.mypy_cache`, `.ruff_cache`, `node_modules`,
`.idea`, `.vscode`, `build`, or `dist` anywhere under the workspace.

These are candidates, not proof of a leak. Review each path because a match may
be intentional or pre-existing.

## Scan a project

Use Python 3.9 or later. Choose a baseline file outside the project workspace.
Before running tests, save the current candidates:

```text
python3 <skill-directory>/scripts/check_leaks.py --workspace <project-root> --save-baseline <baseline-file>
```

After the tests, compare against that baseline:

```text
python3 <skill-directory>/scripts/check_leaks.py --workspace <project-root> --baseline <baseline-file>
```

Replace the placeholders with the actual paths and keep the baseline file until
the comparison and any cleanup are complete. In a Git repository, the scanner
also excludes tracked files; outside Git, the baseline comparison still excludes
pre-existing candidates. Baselines compare paths, so they do not detect changes
to files that already existed. A scan without `--baseline` reports current
untracked candidates, which may have existed before the tests. The script uses
only the Python standard library plus the Git CLI when run inside a Git
repository. It exits with status 1 when it finds candidates and status 2 for
invalid command-line usage.

## Cleanup

The scanner never removes files during a normal scan. Ask the user before cleanup,
then pass only the exact, approved, currently detected relative paths:

```text
python3 <skill-directory>/scripts/check_leaks.py --workspace <project-root> --baseline <baseline-file> --clean --path path/to/approved.tmp
```

Use one `--path` option for each approved new file. Cleanup requires the same
baseline so pre-existing files cannot be selected. See [SKILL.md](SKILL.md)
for the fixture review checklist and process-safety guidance.
