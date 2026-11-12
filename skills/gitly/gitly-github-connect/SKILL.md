---
name: gitly-github-connect
description: Check GitHub CLI authentication and safely create or link a GitHub repository. Use for GitHub connection, online backup setup, "connect to GitHub", or "חבר לגיטהאב".
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly GitHub connection

Read [the shared operating contract](../GITLY.md) first and follow its approval contract.

## Responsibility and triggers

Connect a local project to GitHub through trusted tooling. Examples: “Connect this to GitHub,” “create a private online backup,” “חבר את הפרויקט לגיטהאב”. Coordinate with `gitly-setup` if no local repository exists and `gitly-sync` after a remote is ready.

## Prerequisites and inspection

Check for `gh`, inspect local remotes, and run read-only `gh auth status` without exposing its sensitive details. If GitHub CLI is missing, provide its official installation instructions; installing it is separate and needs approval. If unauthenticated, explain the browser/device flow. Never ask for a password, token, SSH private key, one-time code, or credential pasted into chat.

## Mutating workflow

Starting authentication is an external action: show the exact `gh auth login --web` flow, request approval, then let the user complete browser/device authentication themselves. Verify with `gh auth status`.

For creation, require an explicit repository name and `private` or `public`; default preferences may suggest but never silently choose visibility. Plan `gh repo create <name> --private|--public --source=. --remote=origin` without `--push`. For linking, validate an explicit GitHub HTTPS/SSH `.git` URL and unused remote name before `git remote add <name> <url>`.

Recheck authentication, selected account, root, and remotes after approval. Verify the resulting repository/remote without pushing code.

## Output, errors, and recovery

Report account context safely, visibility, remote name, and that code is still local until `gitly-sync` is approved. Stop on SSO/organization restrictions, occupied remotes, invalid URLs, ambiguous ownership, authentication failure, or existing repositories. Remote removal and GitHub repository deletion are separate destructive requests and are never automatic.
