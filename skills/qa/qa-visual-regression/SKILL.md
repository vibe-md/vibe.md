---
name: qa-visual-regression
description: Configures visual regression testing to detect pixel differences. Use when baselining UI components or changing global styles. Not for testing business logic.
metadata:
  collection: vibe.md
  group: qa
---

# QA Visual Regression Testing

## Purpose
Detects visual layout shifts and styling regressions using screenshot comparison.

## When to Use
- Capturing visual baselines for UI components or monitoring visual design stability.

## Step-by-Step Instructions
1. **Setup Snapshots:** Configure visual comparison using existing E2E/snapshot tools.
2. **Handle Dynamic Content:** Mask dynamic text, dates, or animations before capturing.
3. **Review Differences:** When visual differences occur, present snapshot diffs to the user.
4. **Update Baselines:** Obtain explicit user approval before executing commands with `-u` (update snapshot baseline).

## Examples
**User:** "Set up visual snapshot for the Navbar component."
**Agent:** Creates snapshot test, masks dynamic user avatar, and informs user how diffs will be presented for approval.