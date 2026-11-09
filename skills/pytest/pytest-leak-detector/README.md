# Pytest Leak Detector

Review pytest fixtures for reliable teardown, then check for likely leftover test
artifacts after a test run. The agent instructions are in [SKILL.md](SKILL.md);
the bundled scanner is [scripts/check_leaks.py](scripts/check_leaks.py).

## What it checks

The scanner reports regular files whose extensions are `.db`, `.sqlite`, `.log`,
or `.tmp`, and files whose names start with `temp_`, `test_out_`, or `dump_`.
It skips common virtual-environment, cache, and dependency directories.

These are candidates, not proof of a leak. Review each path because a match may
be intentional or pre-existing.

## Scan a project

Run the scanner with Python 3.9 or later and point it at the project root:

```text
python <skill-directory>/scripts/check_leaks.py --workspace <project-root>
```

Replace the placeholders with the actual paths. The script uses only the Python
standard library and exits with status 1 when it finds candidates.

## Cleanup

The scanner never removes files during a normal scan. Ask the user before cleanup,
then pass only the exact, approved, currently detected relative paths:

```text
python <skill-directory>/scripts/check_leaks.py --workspace <project-root> --clean --path path/to/approved.tmp
```

Use one `--path` option for each approved file. See [SKILL.md](SKILL.md) for the
fixture review checklist and process-safety guidance.
