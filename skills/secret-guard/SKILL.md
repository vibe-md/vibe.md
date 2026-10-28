---
name: secret-guard
description: Keeps credentials out of the repository by checking configuration files and staged changes for secrets before they are saved or pushed. Use when a project starts using API keys, tokens, or service credentials, before the first commit, and whenever configuration or authentication files change.
license: MIT
metadata:
  collection: vibe.md
  author: talforsher
---

# Secret guard

## Purpose

Stop API keys, tokens, and other credentials from being committed, and set up the small habits - ignored env files, committed example files, staged checks - that keep them out permanently.

## When to Use

- The project starts using an API key, token, or service credential.
- Before the first commit, or before committing a new configuration file.
- The user asks to "add my API key", "set up the environment file", or mentions keys in code.
- Checking whether a secret was already committed or pushed.

Do not use this skill to rotate or revoke credentials; that happens at the provider. Use it to detect, contain, and document.

## Prerequisites

- git, for ignore rules, staged checks, and history searches.
- No specific framework or language is assumed.

## Instructions

1. Baseline first. List the project's configuration surfaces: `.env` and `.env.*` files, config and settings files, `docker-compose` files, `*.tfvars`, and similar. Note which are committed, which are ignored, and which hold real values.
2. Ignore before writing. Before any secret touches disk, make sure the file that will hold it is in `.gitignore`. Offer to create an example file (such as `.env.example`) with the same keys and empty placeholder values, so the committed file documents the shape without the values.
3. Check before saving. Before a save or push, scan staged and recently changed content for credential patterns:
   - Provider formats: AWS access keys (`AKIA...`), Google API keys (`AIza...`), OpenAI keys (`sk-...`), Stripe live keys (`sk_live_`, `rk_live_`), GitHub tokens (`ghp_`, `gho_`, `ghu_`), Slack tokens (`xox[abprs]-...`), JWTs (`eyJ...` blocks), and private key PEM headers.
   - Generic shapes: `password`, `secret`, `token`, or `key` assignments in config files with long high-entropy values, and credentials embedded in database or service URLs.
4. Never print a found secret in full. Report the file, the line, the first four characters, and the pattern that matched. Show enough for the user to recognize it, not enough to leak it again into logs or chat.
5. Contain what was not pushed. If a secret is staged or committed but never pushed: move it to the ignored file, replace the in-code use with an environment variable read, and commit only the sanitized version. Ask before rewriting any history.
6. Treat pushed secrets as compromised. If a secret reached a remote, say plainly that deleting or rewriting it is not enough and the credential must be rotated at the provider. Prepare the exact rotation steps for the user to run; do not contact any provider or account yourself.
7. Search all of history when asked. Use history-wide search (`git log -p` on candidate files, or a grep across all commits) rather than only the current state, and report commits and dates without printing values. Rewriting history needs explicit user approval.
8. Optional pre-commit check. With approval, add a pre-commit hook that runs the same pattern checks on staged files. State exactly what it blocks and how to skip it deliberately; never hide the bypass.
9. Report every run. What was checked, what was found (file and pattern only), what was changed, and what the user still needs to do: rotate, update ignore rules, or fill the example file.

## Examples

**User:** "Add my OpenAI key so the app can call the API."

**Agent:** Confirms `.gitignore` covers `.env`, creates `.env.example` with the same key and a placeholder, writes the real key only into `.env`, verifies with `git status` that the env file is ignored, and reports what will be committed instead.

**User:** "Did I ever commit a Stripe key?"

**Agent:** Greps the full history for Stripe live-key patterns, reports the matching commits and dates without printing values, and explains that since the repository was pushed, rotation at Stripe is required no matter what is removed now.
