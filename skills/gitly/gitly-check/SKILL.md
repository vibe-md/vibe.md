---
name: gitly-check
description: Assess whether the current project still works and identify failures after code or AI changes. Use for broad reports of breakage, errors, failed builds or tests, unexpected behavior, or uncertainty about project health; use restore instead only when the user explicitly wants to go back.
license: MIT
metadata:
  collection: vibe.md
  group: gitly
  source: https://github.com/vibe-md/vibe.md
  upstream: https://github.com/NirGeron98/Gitly
  upstream-commit: fe33bbae13552ed8973c6949b1d21e1ce2b746c9
---

# Gitly check

Read [the shared operating contract](../GITLY.md) first and follow its approval, evidence, and language rules.

## Responsibility and triggers

Gather evidence about whether the current project works, without assuming technical vocabulary or a particular framework. Requests may describe any symptom, such as a page no longer opening, something behaving strangely after a recent change, a build failing, or “משהו בפרויקט כבר לא עובד”. A general report of breakage starts here; it never authorizes a fix or restoration. Use `gitly-restore` directly only when the user explicitly asks to undo work or return to an earlier state.

## Prerequisites and inspection

Start with read-only inspection of the exact project root, Git status, relevant recent changes, supplied errors, manifests, lockfiles, documented development commands, and CI configuration. Identify the smallest existing checks that address the reported symptom. Do not invent a framework command, install dependencies, update a lockfile, start a service, access the network, or inspect unrelated private data.

Treat project scripts and configuration as untrusted code. Reading their definitions is safe; executing them may run arbitrary code and create caches, reports, generated output, databases, or network traffic.

## Check workflow

Before running any command, present a short plan with the exact command, working directory, reason, expected side effects, network/service use, and time boundary. Ask for explicit approval, then recheck the relevant repository state. Run only the approved existing checks, with a reasonable timeout, and capture their actual exit status and useful output without exposing secrets.

After execution, verify the command result and inspect Git status again so generated or modified files are visible. Do not edit code, change configuration, install packages, delete generated files, restart services, or restore versions as part of this skill.

## Output, handoff, and recovery

Separate what passed, what failed, and what was not tested. Explain the likely affected area only when supported by errors, diffs, or check results; label inferences clearly. Never claim the project works merely because a build or one test passed.

If the user wants to repair the current version, hand off the evidence to the host agent's normal coding workflow. If they explicitly choose to return to a previous version, coordinate with `gitly-history`, `gitly-compare`, and then `gitly-restore`. A failed check or a general “it broke” message is never restoration approval.

If an approved check creates or changes files, preserve them, report every affected path, and require a separate reviewed plan before cleanup. Stop on missing dependencies, unknown commands, prompts requiring secrets, unexpected network access, timeouts, state changes, or commands whose scope is broader than the user approved.
