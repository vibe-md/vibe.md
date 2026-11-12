---
name: gitly-settings
description: Read or update persistent Gitly project preferences through natural language. Use for settings and phrases like "from now on", "always save online", "מעכשיו", or history/language preferences.
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly settings

Read [the shared operating contract](../GITLY.md) first and follow its approval contract and configuration schema.

## Responsibility and triggers

Translate natural language into small project-local preferences. Examples: “Always save locally and on GitHub,” “From now on only save locally,” “Show ten versions,” “מעכשיו תשמור רק מקומית”. Other skills read these preferences; settings never performs a save or sync itself.

## Prerequisites and inspection

Read `.gitly/config.md` if present; otherwise show shared defaults without creating anything. Validate version, known keys, allowed values, duplicates, and syntax. Do not overwrite malformed, unknown, or existing non-Gitly content. Never store credentials, Git identity, repository URLs, machine paths, or secrets.

## Mutating workflow

Map intent only to `save_destination`, `history_length`, `github_visibility`, or `language`. `confirmation` always remains `always`. Show an exact before/after table and explain that the next action still needs its own approval. Ask for explicit approval, re-read the file to catch concurrent changes, then create or minimally edit `.gitly/config.md` while preserving unrelated comments and valid settings. Write all six schema keys for a new file using the shared order.

Verify by reading the resulting file and reporting effective values. A preference such as `local_and_github` means “offer/plan a push after save,” never silent authorization.

## Output, errors, and recovery

Report changed and unchanged preferences in the user's language. Stop on unsupported values, history outside 1–100, malformed/unknown fields, concurrent edits, permission errors, or requests to weaken confirmation. Recovery is another approved settings change back to the previously shown value. Never delete the configuration automatically.
