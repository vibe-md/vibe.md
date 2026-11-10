---
name: qa-change-impact-analysis
description: Performs impact analysis on code changes to identify logic regressions. Use when evaluating side effects of modified shared components. Not for checking pixel-perfect UI differences.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---

# Change Impact Analysis & Regression Shield

## Purpose
Acts as a safeguard against "silent bugs". Analyzes the broader impact of a specific code change on the overall system architecture and user flows.

## When to Use
- After refactoring shared UI components or core utilities.
- When evaluating a Pull Request for potential side effects.
## When NOT to Use
- For checking pixel-perfect UI differences (use `qa-visual-regression` instead).

## Prerequisites
- Access to the `git diff` or the modified files and the project structure.

## Step-by-Step Instructions
1. **Trace Dependencies:** Identify all components/pages that import or rely on the modified files.
2. **Global & State Check:** Evaluate if the change inadvertently alters global state or shared logic.
3. **Edge Case Mapping:** Analyze how the changes affect edge cases (e.g., empty states).
4. **Generate Report:** Output a Regression Risk Report highlighting components that need re-testing.

## Validation Criteria
- The analysis must identify at least indirect dependencies, not just the file changed.

## Safety Considerations
- Ensure the agent does not alter code, only analyzes the read-only diff.

## Expected Output
A "Regression Risk Report" listing high, medium, and low-risk areas affected by the change.

## Examples
**User:** "I updated the global input styling. Check for impact."
**Agent:** Traces the CSS change, discovers it affects the Checkout and Login forms, and warns that error message visibility in those forms might be compromised.