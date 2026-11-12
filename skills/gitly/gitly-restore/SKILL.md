---
name: gitly-restore
description: Safely restore files from or revert to a previous project version while preserving recovery paths. Use only when the user explicitly wants to undo work, recover earlier content, or return to a prior state; general breakage reports belong to gitly-check.
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly restore

Read [the shared operating contract](../GITLY.md) first and follow its approval contract.

## Responsibility and triggers

Help the user return to earlier content without silently discarding work. Examples: “Go back to the version where login worked,” “restore only the dashboard,” “undo yesterday's saved version,” “חזור לגרסה שבה ההתחברות עבדה”. A general statement that something is broken is not rollback intent; use `gitly-check` first. Use `gitly-history` to find candidates and `gitly-compare` to show impact.

## Prerequisites and inspection

Distinguish four intents: view an old version (read-only), restore selected files into current work, revert one commit by adding a new commit, or move a branch pointer. Do not offer branch-pointer movement as the normal path. Resolve stable commits, inspect status/staged/untracked changes, compare selected paths, and identify conflicts, submodules, LFS, and merge commits.

## Mutating workflow

Default to selected-file restoration. The plan must state exactly what stays, changes, and may be lost. If selected paths have uncommitted work, include a recoverable checkpoint using a path-scoped stash with untracked files and a descriptive message, then restore the paths from the chosen commit. Verify the stash exists before restoring. Restore into the working tree so the user can review, then coordinate with `gitly-save` for a new version.

For undoing a complete ordinary commit, prefer `git revert --no-edit <stable-id>`. Stop on merge commits until the correct mainline parent is understood and approved. Never use hard reset, forced checkout, destructive clean, or reflog expiry.

## Output, errors, and recovery

After explicit approval and a fresh state check, execute only the selected mode and verify status/diff. Report restored paths, revert commit, unchanged work, and checkpoint name. On conflicts or partial failure, stop and show the safe state. Recovery uses the named stash, a revert of the new revert commit, or an approved merge/revert abort; never apply or drop a stash automatically.
