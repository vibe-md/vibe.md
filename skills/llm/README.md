---
title: LLM Engineering
summary: Practical skills for building and checking features that use language models.
categories: AI / Agents, Testing
maintainers: [NirGeron98, AdiBer1]
---

# LLM Engineering

Skills that help a coding agent build, measure, and maintain features that call language models.

## Skills

| Skill | What it does |
| --- | --- |
| `llm-eval-builder` | Builds a small, repeatable evaluation set and runner for an LLM feature, with deterministic checks, optional rubric grading, and baseline comparison for regressions. Asks before any paid model call. |
| `llm-prompt-review` | Reviews prompts and prompt templates for a clear task, an output format that matches the parser, edge cases, and testability, then proposes specific edits. Read-only unless asked. |
| `llm-model-migration-check` | Plans a safe switch between models: inventories model IDs and settings, checks the provider's current documentation, compares evals on both models, and drafts a rollout and rollback plan. Does not deploy. |

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
