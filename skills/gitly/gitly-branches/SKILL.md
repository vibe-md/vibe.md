---
name: gitly-branches
description: List, create, and switch safe branches or isolated worktree experiments. Use for experiments, "try this without breaking my app", branch requests, "ניסוי", or "ענף".
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly branches

Read [the shared operating contract](../GITLY.md) first and follow its approval contract.

## Responsibility and triggers

Create safe places to experiment and explain them without requiring Git vocabulary. Examples: “I want to experiment without breaking my current app,” “switch back to the working version,” “תנסה משהו בלי לפגוע באפליקציה”. Coordinate with `gitly-merge` when the experiment is ready.

## Prerequisites and inspection

Read preferences and inspect current branch/HEAD, status, existing local/remote branches, and worktrees. Listing is read-only. Explain that a branch is another line of work in the same folder, while a worktree provides a separate folder for simultaneous work. Validate new names with `git check-ref-format --branch` and never use a name beginning with `-`.

## Mutating workflow

Prefer a worktree when the user wants isolation without disturbing the current folder. Propose an explicit branch name and sibling destination, verify neither exists, then plan `git worktree add -b <branch> <destination> HEAD`. For a clean single-folder flow, plan `git switch -c <branch>`. Switching existing branches requires a clean working tree and uses `git switch <branch>`.

Show the starting version, folder impact, and where future saves will go. Ask for approval, recheck names/status/worktrees, execute, and verify branch plus working directory. Never carry dirty changes across branches silently.

## Output, errors, and recovery

Report the active experiment and folder in plain language. Stop on dirty/staged changes, detached HEAD, invalid/colliding names, nested repositories, missing commits, or occupied destinations. Switching back is a new approved plan. Branch/worktree deletion is intentionally outside normal flow; explain safe manual review and require a separate explicit deletion request. Never delete unmerged work automatically.
