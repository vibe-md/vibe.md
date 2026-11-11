---
title: Security
summary: AI application security reviews and local access-control regression tests.
categories: Security, AI / Agents
maintainers: [NoaGaler]
---

# Security

Skills that help coding agents review AI application security and turn access rules into local regression tests.

## Skills

| Skill | What it does |
| --- | --- |
| `security-agent-guard` | Reviews code that uses LLMs or AI agents for prompt injection, excessive agent permissions, unsafe tool calls, cross-user leaks in retrieval (RAG), sensitive data in prompts, and unsafe use of model output. Read-only: it reports findings and does not change code. |
| `security-media-privacy` | Read-only audit of Computer Vision pipelines and image/video ingestion code (unblurred frames, EXIF GPS metadata, insecure temporary files, and cloud uploads). |
| [`multimodal-visual-attack-guard`](./multimodal-visual-attack-guard/SKILL.md) | Audits multimodal AI applications for indirect visual prompt injection, untrusted image-derived data propagation, and unauthorized tool execution. |
| `security-access-regression` | Turns declared access rules into local regression tests with allowed controls, forbidden reads, unchanged-state assertions, and disposable-copy checks that the tests detect regressions. Writes tests, not a general security audit. |
| `security-otp-failopen` | Writes local tests for a one-time code flow: single use, expiry, account and purpose binding, attempt and issuance limits, and the provider error, timeout or malformed answer that must never complete the action. Tests only, with a fake delivery adapter. |

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
