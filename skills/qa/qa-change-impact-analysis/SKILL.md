---
name: qa-change-impact-analysis
description: Performs impact analysis on code changes to identify logic regressions. Use when evaluating side effects of modified shared components. Not for checking pixel-perfect UI differences (use qa-visual-regression).
metadata:
  collection: vibe.md
  group: qa
---

# Change Impact Analysis & Regression Shield

## Purpose
Analyzes `git diff` and project dependencies to detect potential side effects on core user flows.

## When to Use
- Evaluating code changes in shared utilities, state management, or common components.

## Step-by-Step Instructions
1. **Trace Imports:** Inspect modified files and identify all dependent modules.
2. **Map Risk Areas:** Identify secondary pages or components that rely on the modified logic.
3. **Generate Risk Report:** Present a summary of affected user flows requiring verification.

## Examples
**User:** "I updated the form validation utility. What could break?"
**Agent:** Traces code dependencies and highlights that Login and Signup forms share this utility and should be re-tested.