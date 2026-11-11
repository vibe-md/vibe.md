---
name: qa-e2e-playwright
description: Writes automated End-to-End browser tests. Use when testing full user flows and UI interactions. Not for testing isolated backend functions.
metadata:
  collection: vibe.md
  group: qa
---

# QA End-to-End (E2E) Automation

## Purpose
Creates browser automation tests simulating real user journeys.

## When to Use
- Testing user workflows (login, checkout, navigation) end-to-end.

## Step-by-Step Instructions
1. **Check Environment:** Reuse the project's existing test framework. Ask for user approval before installing new packages (e.g., `playwright`, `cypress`).
2. **Select Elements:** Prefer accessible selectors (`data-testid`, ARIA roles).
3. **Write Journeys:** Implement step-by-step UI actions and assertions.
4. **Isolate State:** Ensure tests run independently without shared state.

## Safety Considerations
- Confirm test target is non-production before running actions that modify state.

## Examples
**User:** "Write an E2E test for user login."
**Agent:** Checks setup, writes `login.spec.ts` targeting input fields, and asserts successful navigation to dashboard.