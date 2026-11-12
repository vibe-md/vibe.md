---
name: pytest-leak-detector
description: Audits pytest fixtures for reliable resource teardown and finds likely leftover test artifacts. Use when writing or reviewing pytest fixtures, running Python tests, or checking for temporary files after a test run.
license: MIT
metadata:
  categories: Testing
  maintainers: shir-exe
  group: pytest
  title: Pytest Leak Detector
---

# Pytest Leak Detector

## Purpose

Help prevent pytest fixtures from leaking resources or leaving test artifacts in a project.

## When to Use

Use this skill when:
- Writing or reviewing pytest fixtures, especially fixtures that open files or manage external resources.
- Running Python tests with pytest and checking for leftover test artifacts.

Do not use it as a general-purpose filesystem cleanup tool or as proof that a flagged file is a leak.

## Prerequisites

- Python 3.9 or later to run the bundled artifact scanner.
- pytest to run the project's tests.
- The scanner uses only the Python standard library.

## Instructions

### 1. Audit fixtures and resources

- Resource-managing fixtures should use `yield` so teardown runs after the test. For complex setup, use `try...finally` or register `request.addfinalizer()` immediately after acquiring a resource, so cleanup is also covered if later setup fails.
- Use pytest's `tmp_path` fixture for files and directories instead of creating temporary files in the project.
- Explicitly close or stop external resources, such as HTTP sessions, database connections, sockets, and containers, in fixture teardown.
- Prefer function-scoped fixtures for isolation. Use broader scopes only when sharing state is intentional and safe.

For example:

```python
import pytest


@pytest.fixture
def output_file(tmp_path):
    path = tmp_path / "output.txt"
    with path.open("w", encoding="utf-8") as file:
        yield file
```

The context manager closes the file when pytest resumes the fixture after the test.

### 2. Run tests and scan for artifacts

1. Run the relevant pytest command from the project root.
2. Locate this skill's bundled `scripts/check_leaks.py` and run it with Python 3.9 or later, setting `--workspace` to the project root. For example:

   ```text
   python3 <skill-directory>/scripts/check_leaks.py --workspace <project-root>
   ```

   Replace both placeholders with the actual paths. The scanner checks files outside common environment and cache directories for suspicious extensions (`.db`, `.sqlite`, `.log`, `.tmp`) and prefixes (`temp_`, `test_out_`, `dump_`).
3. Report every candidate by its relative path. A match is only a candidate, not proof that the test run created it; it may be intentional or pre-existing. The scanner exits with status 1 when it finds candidates.
4. If needed, separately inspect running processes using read-only process information. Verify a process belongs to this test run before discussing it; never terminate a process without the user's explicit approval.

### 3. Ask before cleanup

- Never delete detected files automatically. Show the exact candidate paths and ask the user whether they want them cleaned up.
- Only after approval, pass each approved, currently detected relative path with its own `--path` option and `--clean`:

  ```text
  python3 <skill-directory>/scripts/check_leaks.py --workspace <project-root> --clean --path path/to/approved.tmp
  ```

- Do not add unapproved paths or broaden the cleanup. If the user approves stopping a process, stop only the specifically identified process and report the result.

## Examples

**User:** "Can you check whether my pytest fixtures close their files?"

**Agent:** Reviews the fixtures for `yield`-based teardown, explicit closure, and use of `tmp_path`; reports any concrete issues and suggests a focused fix.

**User:** "Run the tests and check for leftover files."

**Agent:** Runs the project's pytest command, scans the project root with the bundled script, reports the exact candidate paths and any relevant processes, then asks before cleaning anything.
