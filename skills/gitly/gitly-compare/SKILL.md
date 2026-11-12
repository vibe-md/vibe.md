---
name: gitly-compare
description: Compare two reachable versions or a version with current work using Git evidence. Use for "what changed", "compare yesterday and today", "מה השתנה", or "השווה גרסאות".
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly compare

Read [the shared operating contract](../GITLY.md) first and follow its evidence and language rules.

## Responsibility and triggers

Explain meaningful differences between two chosen versions, or between one version and current work. Examples: “What changed between yesterday and today?”, “compare version 2 with 5,” “מה השתנה מאז אתמול”. Use `gitly-history` to resolve ambiguous human descriptions first.

## Prerequisites and inspection

Resolve each selected ref to a reachable commit with `git rev-parse --verify --end-of-options <ref>^{commit}`. Record the stable IDs. For current work, inspect both staged and unstaged changes. Use read-only `git diff --name-status`, `--stat`, rename detection, and focused diffs. Avoid loading huge or irrelevant diffs; summarize binaries and submodules without pretending to read them.

## Operational guidance

No approval is needed because comparison is read-only. Group verified changes into additions, modifications, removals, and renames. Inspect relevant code/tests before describing behavioral implications. Label an implication “inferred” unless a test or direct evidence verifies it. Never print secret values encountered in historical content.

## Output, errors, and recovery

Name both endpoints with dates/descriptions and secondary IDs, then give a concise plain-language summary and file-level evidence. Say when no difference exists. Report ambiguous/missing refs, unrelated history, shallow clone gaps, binary files, oversized diffs, and dirty-tree boundaries. Offer restore only as a separate `gitly-restore` workflow. Recovery is unnecessary because this skill is read-only.
