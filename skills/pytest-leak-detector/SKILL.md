---
name: pytest-leak-detector
description: Use when reviewing pytest fixture teardown or investigating leftover files after a test run; not for routine pytest runs.
license: MIT
metadata:
  collection: vibe.md
  categories: Testing
  maintainers: shir-exe
---

# Pytest Leak Detector

## Purpose

Help prevent pytest fixtures from leaking resources or leaving test artifacts in a project.

## When to Use

Use this skill when:
- Reviewing pytest fixture teardown.
- Investigating files left behind after a test run.

Do not use it for routine pytest runs or as a general-purpose filesystem cleanup tool. A flagged file is only a candidate, not proof of a leak.

## Prerequisites

- Python 3.9 or later to run the bundled artifact scanner.
- Git CLI to exclude tracked files when the workspace is in a Git repository.
- pytest to run the project's tests.
- The scanner's Python dependencies use only the standard library. Without Git, the baseline still filters pre-existing candidates.

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

1. Locate this skill's bundled `scripts/check_leaks.py`, set `--workspace` to the project root, and choose a baseline file outside the workspace.
2. Before running tests, save the current candidates with Python 3.9 or later:

   ```text
   python3 <skill-directory>/scripts/check_leaks.py --workspace <project-root> --save-baseline <baseline-file>
   ```

   Replace the placeholders with the actual paths and keep the baseline file until comparison and any cleanup are complete. In a Git repository, the scanner also excludes files tracked by Git.
3. Run the relevant pytest command from the project root.
4. After the tests, compare the scan with the baseline:

   ```text
   python3 <skill-directory>/scripts/check_leaks.py --workspace <project-root> --baseline <baseline-file>
   ```

   The scanner reports only new paths; it does not detect changes to files that already existed. Without Git, the baseline still filters pre-existing paths. It prunes common environment, cache, dependency, and build directories before scanning. It checks other files for suspicious extensions (`.db`, `.sqlite`, `.log`, `.tmp`) and prefixes (`temp_`, `test_out_`, `dump_`). It exits with status 1 when candidates are found and status 2 for invalid command-line usage.
5. Report each new candidate by its relative path. A match is only a candidate, not proof that the test run created it; it may be intentional.
6. If needed, inspect running processes with read-only commands. First list process IDs, then inspect a specific candidate:

   - Windows PowerShell:

     ```powershell
     Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, CreationDate, Name
     Get-CimInstance Win32_Process -Filter "ProcessId = 1234" | Select-Object ProcessId, ParentProcessId, CreationDate, Name, CommandLine
     ```

   - macOS or Linux:

     ```sh
     ps -eo pid,ppid,lstart,comm
     ps -p 1234 -o pid=,ppid=,lstart=,command=
     ```

   Replace `1234` with the candidate process ID. Verify it belongs to this test run using its start time, command, and parent process; a matching process name alone is not enough. These commands only display process information. Never terminate a process without the user's explicit approval.

### 3. Ask before cleanup

- Never delete detected files automatically. Show the exact candidate paths and ask the user whether they want them cleaned up.
- Only after approval, pass each approved, currently detected relative path with its own `--path` option and `--clean`:

  ```text
  python3 <skill-directory>/scripts/check_leaks.py --workspace <project-root> --baseline <baseline-file> --clean --path path/to/approved.tmp
  ```

- Cleanup requires the same baseline and accepts only new candidates. Use one `--path` option for each approved file. Do not add unapproved paths or broaden the cleanup. If the user approves stopping a process, stop only the specifically identified process and report the result.

## Examples

**User:** "Can you check whether my pytest fixtures close their files?"

**Agent:** Reviews the fixtures for `yield`-based teardown, explicit closure, and use of `tmp_path`; reports any concrete issues and suggests a focused fix.

**User:** "Run the tests and check for leftover files."

**Agent:** Saves a baseline, runs the project's pytest command, compares the project root against the baseline, reports new candidate paths and any relevant processes, then asks before cleaning anything.
