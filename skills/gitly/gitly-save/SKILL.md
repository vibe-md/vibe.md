---
name: gitly-save
description: Review project changes and save an intentional version with a meaningful commit. Use for save/commit requests such as "save everything I did today", "save my progress", "שמור", or "שמור את ההתקדמות".
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly save

Read [the shared operating contract](../GITLY.md) first and follow its approval contract.

## Responsibility and triggers

Create one truthful local version from an explicitly reviewed set of changes. Examples: “Save my progress,” “save only the login fix,” “commit this,” “שמור את כל מה שעשיתי היום”. Use `gitly-setup` when Git or identity is missing and `gitly-sync` only for an explicitly requested/configured online backup.

## Prerequisites and inspection

Read preferences, then inspect branch/HEAD, full status, staged changes, untracked and ignored paths, and relevant diffs. Detect likely secrets by filename and content patterns without printing values. Flag large files, generated output, binaries, submodules, LFS candidates, and changes that cannot be understood from the diff. Never use `git add .` or `git add -A`.

Existing staged paths are part of the proposed commit. If any are outside the intended save, stop and ask whether to include them or handle them separately; do not silently unstage them.

## Mutating workflow

Create an evidence-backed, concise commit subject in the user's language unless project conventions require another language. The plan must list every path, existing staged content, the exact message, whether hooks can run, and whether a later GitHub backup is proposed. After approval and a fresh state check:

1. Stage only each approved path with `git add -- <paths>`.
2. Verify `git diff --cached --name-status` and `git diff --cached --check` exactly match the plan.
3. Commit with the approved message.
4. Verify the new commit ID and that unapproved working changes remain.

If `save_destination` is `local_and_github`, coordinate with `gitly-sync`. A separate sync plan/approval is the safe default; a combined approval is valid only when both exact steps and remote effects were shown up front.

## Output, errors, and recovery

Report what was saved, what remains unsaved, the readable description, date, and short commit ID as secondary metadata. Stop on no changes, missing identity, secret uncertainty, ignored files, changed state, hook failure, index mismatch, detached HEAD, or commit failure. A local commit is recoverable through `gitly-restore`; never amend or rewrite it silently.
