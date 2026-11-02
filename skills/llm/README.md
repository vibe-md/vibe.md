---
title: LLM Engineering
summary: Practical skills for building and checking features that use language models.
categories: AI / Agents, Testing
maintainers: [NirGeron98]
---

# LLM Engineering

Skills that help a coding agent build, measure, and maintain features that call language models.

## Skills

| Skill | What it does |
| --- | --- |
| `llm-eval-builder` | Builds a small, repeatable evaluation set and runner for an LLM feature, with deterministic checks, optional rubric grading, and baseline comparison for regressions. Asks before any paid model call. |

## Related skills

- `security-agent-guard` reviews AI features for security risks, such as prompt injection and unsafe tool use.
- `security-access-regression` writes local tests that prove who can read or change which data.

## Install the package

From a vibe.md checkout:

```bash
bash scripts/install.sh --group llm --agent claude-code --project /path/to/project --dry-run
bash scripts/install.sh --group llm --agent claude-code --project /path/to/project
```

Use `codex`, `cursor`, `gemini`, or `copilot` for another agent.
