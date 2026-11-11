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

1. **Trace Imports:** Use search tools (e.g., `git grep`, `rg`, or IDE search) to list all files importing the modified module:

   ```bash
   rg "import.*from ['\"].*path/to/module['\"]"
   ```

2. **Map Dependents:** Inspect the output list to identify secondary components, routes, or utilities affected by the change.

3. **Assess Risks:** Check for potential breaking changes in function signatures, state mutations, or side-effects.

4. **Generate Risk Report:** Present a clear summary of dependent files and user flows that require targeted regression testing.

## Examples

**User:** "I updated the form validation utility. What could break?"

**Agent:** Runs `rg` to find imports of `formValidation`, identifies that Login and Signup forms share it, and highlights those flows for regression testing.