---
title: Security
summary: Security reviews for code, starting with risks specific to applications that use LLMs and AI agents.
categories: Security, AI / Agents
maintainers: [NoaGaler]
---

# Security

Skills that help coding agents review code for security problems and explain how to fix them.

## Skills

| Skill | What it does |
| --- | --- |
| `security-agent-guard` | Reviews code that uses LLMs or AI agents for prompt injection, excessive agent permissions, unsafe tool calls, cross-user leaks in retrieval (RAG), sensitive data in prompts, and unsafe use of model output. Read-only: it reports findings and does not change code. |

## Related skills

General code security and committed secrets are covered by standalone skills in this collection:

- `pre-commit-security-review` reviews changed code for injection, access control, and other common vulnerabilities.
- `secret-guard` keeps credentials out of the repository.

`security-agent-guard` covers what those skills do not look for: risks that exist because the application uses a model.

## Install the package

From a vibe.md checkout:

```bash
bash scripts/install.sh --group security --agent claude-code --project /path/to/project --dry-run
bash scripts/install.sh --group security --agent claude-code --project /path/to/project
```

Use `codex`, `cursor`, `gemini`, or `copilot` for another agent.
