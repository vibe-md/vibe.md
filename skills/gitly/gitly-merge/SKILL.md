---
name: gitly-merge
description: Inspect and safely combine an experiment branch with the current project. Use for merge/integration requests such as "put the changes into my main project", "merge", "מזג", or "שלב את הניסוי".
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly merge

Read [the shared operating contract](../GITLY.md) first and follow its approval contract.

## Responsibility and triggers

Bring an approved line of work into another without guessing through conflicts. Examples: “Put the experiment into my main project,” “merge the login branch,” “שלב את הניסוי בפרויקט הראשי”. Use `gitly-branches` when the source/destination is not yet clear and `gitly-save` if pending work must be saved first.

## Prerequisites and inspection

Require an attached destination branch and clean working tree/index. Validate and resolve the source branch, compute merge base, list source-only commits, and compare source with destination. Check whether it is already merged, fast-forwardable, divergent, or unrelated. Run project checks only when safe and relevant; do not claim they passed unless actually run.

## Mutating workflow

The plan must identify source, destination, commits/behavior expected to enter, merge mode, hooks/checks, conflict risk, and recovery. After approval and a fresh recheck, run a normal non-force merge with `git merge --no-edit -- <source>`. Do not switch destinations implicitly and do not add branch deletion.

If conflicts occur, stop immediately. Preserve conflict markers and both sides, list conflicted paths in plain language, and ask the user how the intended behavior should work. Never pick “ours”/“theirs,” regenerate a file, or resolve code automatically without a new explicit plan and evidence. Completing or aborting a conflicted merge is another mutation requiring approval.

## Output, errors, and recovery

Verify and report the fast-forward/merge commit, included versions, checks performed, and remaining branches. On failure report the exact safe state without dumping secrets. Recovery before completion is an explicitly approved `git merge --abort`; after completion use `gitly-restore`/revert rather than rewriting history.
