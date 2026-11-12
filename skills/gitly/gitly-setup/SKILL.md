---
name: gitly-setup
description: Check Git readiness and safely prepare a project repository. Use for Gitly setup, initialization, Git identity, ignore-file, "set up Git", "הגדר גיט", or "אתחל מאגר" requests.
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly setup

Read [the shared operating contract](../GITLY.md) first and follow its approval contract.

## Responsibility and triggers

Prepare a project for safe local versioning without assuming Git knowledge. Examples: “Set up Gitly,” “start keeping versions,” “Is Git ready?”, “הגדר את Gitly”, “תתחיל לשמור גרסאות”. Coordinate with `gitly-github-connect` only when the user also wants GitHub.

## Prerequisites and inspection

Check whether `git` is available and report its version. From the exact project directory inspect repository root, current branch, HEAD, status, `user.name`, `user.email`, `.gitignore`, remotes, worktree/submodule context, and `.gitly/config.md`. These checks are read-only. Do not invent identity values or initialize a parent directory accidentally.

If Git is missing, provide official platform-appropriate installation guidance. Installing software is a separate mutation and requires approval. GitHub CLI is optional here.

## Mutating workflow

Possible actions are independent and must appear in the plan:

- Initialize: `git init --initial-branch=main` in the selected project only.
- Set repository-local identity after the user supplies real values: `git config --local user.name <name>` and `git config --local user.email <email>`.
- Create or edit `.gitignore` only for patterns the user reviewed; preserve all existing content.

Show which files will be created, that initialization is local, and that Git hooks or nested repositories may change the risk. Ask for explicit approval, recheck the directory and state, execute only approved items, then verify root, branch, identity, ignore behavior, and status.

## Output, errors, and recovery

Return a plain-language readiness checklist and the next useful action. Stop on unexpected roots, unsafe ownership warnings, worktrees/submodules the user did not expect, missing identity, or permission errors. Initialization creates `.git`; do not remove it automatically. Identity and ignore changes can be corrected through a new approved setup plan. Never delete existing configuration.
