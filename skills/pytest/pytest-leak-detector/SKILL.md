---
name: pytest-leak-detector
description: Use when writing, refactoring, or running pytest tests to audit fixture teardown and identify leftover test files or processes.
metadata:
  categories: Testing
  maintainers: shir-exe
  group: pytest
---

# Pytest Leak Detector

## When to Use
Use this skill whenever writing, refactoring, or running Python tests with `pytest`, or when creating test fixtures and mock setups.

## Prerequisites
- Python 3.9 or later to run the bundled leak-check script.

## Instructions

### 1. Fixture & Resource Audit
When creating or reviewing fixtures, enforce the following patterns:
- **Teardown Guarantee**: Ensure resource-managing fixtures use `yield` instead of `return`. For complex setups, prefer `try...finally` or `request.addfinalizer()` to guarantee cleanup execution even if setup steps fail mid-process.
- **Built-in Temp Storage**: Enforce using pytest's built-in `tmp_path` fixture for filesystem operations instead of creating ad-hoc local files or directories within the project root.
- **Explicit Closure**: Verify that external resources (HTTP sessions, DB connections, sockets, Docker containers) have explicit termination calls (`.close()`, `.stop()`) in their teardown block following `yield`.
- **Scope Verification**: Choose fixture scope intentionally. Prefer function scope for isolation; use broader scopes only when sharing state is safe and intended.

### 2. Post-Test Leak Detection & Script Execution
- After executing `pytest`, run the [bundled leak-check script](scripts/check_leaks.py) from the project directory. It reports files that match common temporary-artifact names; these are candidates, not proof of a leak.
- Check for leftover test processes separately. Confirm that a process belongs to this test run before considering it for termination.

### 3. Interactive Clean-up & Approval
- Present a concise, itemized report of detected file candidates and any test-related processes to the user.
- **Never auto-delete files or terminate processes without explicit permission.** Always ask:
  > *"The test run left behind the following artifacts: [List]. Would you like me to clean them up?"*
- Upon receiving approval, pass only the exact file paths the user approved to the script, using one `--path` option per file:
  `python3 /path/to/pytest-leak-detector/scripts/check_leaks.py --workspace . --clean --path path/to/approved.tmp`
- If the user approves stopping a process, stop only the specifically identified process and report the result. Never stop processes based only on their name.

## Examples

### User Prompt:
"Write a pytest fixture that creates a temporary config file and connects to a test DB."

### Agent Action (Using this skill):
```python
import pytest

@pytest.fixture
def db_config(tmp_path):
    # Uses built-in tmp_path instead of creating files in the project root
    config_file = tmp_path / "config.json"
    config_file.write_text('{"db": "test"}')

    db_conn = start_test_db()

    yield db_conn, config_file

    # Teardown: explicitly close connection
    db_conn.close()
```
