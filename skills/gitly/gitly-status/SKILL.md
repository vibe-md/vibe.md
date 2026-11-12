---
name: gitly-status
description: Explain whether project work is saved, backed up, current, or at risk using local Git evidence. Use when the user asks what state the project is in or whether work is safe; do not use to test application behavior.
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly status

Read [the shared operating contract](../GITLY.md) first and follow its evidence and language rules.

## Responsibility and triggers

Give a plain-language snapshot of version-control safety without changing anything. This applies whenever the user is unsure whether work is saved, online, current, on the expected line of work, or at risk of being lost—even when they use no Git vocabulary. Examples include “Is everything saved?”, “Am I backed up?”, “Where is my work?”, and “האם הכול שמור ובטוח?”. Use `gitly-check` instead when the question is whether the application itself works.

## Inspection

Confirm the selected project root, then inspect the current branch or detached state, HEAD, staged/unstaged/untracked work, worktrees, latest local version, configured remotes, upstream, and local ahead/behind counts. Read Gitly preferences when present. Use only local refs: do not fetch, contact GitHub, start authentication, or imply that a remote-tracking ref is fresh.

Minimize content inspection. Counts, paths, dates, and version subjects are normally enough; do not print secret values or load full diffs unless the user separately asks what changed.

## Output

No approval is needed because this workflow is read-only. Report, in everyday language:

- what is not yet saved locally;
- the latest local version and active branch or experiment;
- whether a remote and upstream are configured;
- what the locally cached refs say about ahead/behind state;
- whether online backup freshness is verified, stale, or unknown;
- the next useful Gitly action, if any.

Never claim that work is backed up online without fresh remote evidence. Offer `gitly-sync` when verification requires a fetch, `gitly-save` for unsaved work, `gitly-setup` when no repository exists, and `gitly-check` for product health. Do not perform those actions automatically.

## Errors and recovery

Report missing Git, an unexpected repository root, unborn or detached HEAD, invalid preferences, missing upstream, stale tracking data, and incomplete/shallow history without guessing. Recovery is unnecessary because this skill must not mutate files, refs, remotes, credentials, or network state.
