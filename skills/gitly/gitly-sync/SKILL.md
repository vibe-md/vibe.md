---
name: gitly-sync
description: Explain and safely synchronize local work with a Git remote using fetch, fast-forward pull, or non-force push. Use for sync, push, pull, online backup, "back it up", "סנכרן", or "גיבוי בענן".
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly sync

Read [the shared operating contract](../GITLY.md) first and follow its approval contract.

## Responsibility and triggers

Move versions between the local project and a configured remote without overwriting history. Examples: “Back up my project to GitHub,” “get the online changes,” “סנכרן עם גיטהאב”. Use `gitly-github-connect` when authentication or a remote is missing and `gitly-save` when local changes need a version first.

## Prerequisites and inspection

Inspect branch/HEAD, status/index, remotes, upstream configuration, and local tracking refs without network access. Explain that remote knowledge may be stale. Network fetch changes remote-tracking refs, so it is a mutation requiring approval. Detect detached HEAD, dirty pull state, missing upstream, ahead/behind counts, divergence, protected branches, submodules, and LFS.

## Mutating workflow

Prepare exactly the requested direction:

- Refresh knowledge: `git fetch -- <remote>`.
- Download updates only when the tree is clean: `git pull --ff-only <remote> <branch>`. Refuse divergence instead of creating a silent merge.
- Upload: `git push --set-upstream <remote> <branch>`. Never add force flags.

The plan must name remote/branch, data direction, known divergence, credential/helper behavior, remote effect, and recovery. A save approval never authorizes a push. Recheck local state and remote configuration after approval, execute, then fetch/inspect refs as needed to verify the relationship.

## Output, errors, and recovery

Report whether local and online versions now match, what moved, and what remains only local/remote. Stop on non-fast-forward rejection, divergence, dirty pull, offline/authentication errors, changed upstream, protected branches, partial network failure, or unexpected remote URLs. Preserve history; inspect again and offer choices instead of force-pushing or auto-merging.
