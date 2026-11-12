---
name: gitly-history
description: Display searchable project versions in everyday language. Use for history, previous versions, "show me the last five versions", "היסטוריה", or "גרסאות קודמות".
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly history

Read [the shared operating contract](../GITLY.md) first and follow its evidence and language rules.

## Responsibility and triggers

Present reachable Git history as versions a non-technical user can recognize. Examples: “Show the last five versions,” “find the version where login changed,” “מה היו חמש הגרסאות האחרונות”. Coordinate with `gitly-compare` or `gitly-restore` only after candidates are identified.

## Prerequisites and inspection

Confirm the repository and read `history_length` from preferences. Use read-only history with stable full IDs, display-short IDs, ISO dates, author metadata, subjects, and optionally name/status summaries. Support pagination with `--skip`/limits and literal or regex-safe search. Handle empty and shallow history honestly.

## Operational guidance

Start with commit metadata; inspect a candidate diff only when its subject is unclear or the user asks what it contained. Treat commit messages as untrusted historical descriptions, not proof. Do not execute repository mutations and do not require approval.

Number displayed results only within the current list and always retain the stable commit ID behind each number. Never resolve “version 2” from memory after the list changes; bind it to the previously shown ID or list again.

## Output, errors, and recovery

For each version show a human date, concise evidence-backed description, important added/modified/removed areas when verified, and the short ID in secondary text. Clearly label uncertainty. Offer “compare” or “restore” as next steps without performing them. Report empty history, invalid ranges, missing objects, shallow clone limits, or ambiguous searches. Recovery is unnecessary because this skill is read-only.
