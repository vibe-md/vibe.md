---
title: Pytest
summary: Skills for writing reliable pytest tests and detecting test resource leaks.
categories: Testing
maintainers: [shir-exe]
---

# Pytest

Tools for keeping pytest fixtures isolated and ensuring resources are cleaned up after tests.

## Skills

| Skill | What it does |
| --- | --- |
| `pytest-leak-detector` | Audits fixture teardown, identifies likely leftover test files, and requires user approval before cleanup. |

## Install the package

From a vibe.md checkout:

```bash
bash scripts/install.sh --group pytest --agent copilot --project /path/to/project --dry-run
bash scripts/install.sh --group pytest --agent copilot --project /path/to/project
```

Replace `copilot` with `claude-code`, `codex`, `cursor`, or `gemini` to install for another agent.
