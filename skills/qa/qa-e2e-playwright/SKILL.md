---
name: qa-e2e-playwright
description: Writes automated End-to-End browser tests. Use when testing full user flows and UI interactions. Not for testing isolated backend functions.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---

# QA End-to-End (E2E) Automation

## Purpose
Creates stable browser-based tests to simulate real user behavior across the application UI.

## When to Use
- Automating critical user flows (login, checkout).
- Testing cross-browser compatibility.
## When NOT to Use
- Testing isolated backend functions (use API or Unit testing).

## Prerequisites
- Playwright or Cypress installed. A running local or staging environment.

## Step-by-Step Instructions
1. **Identify Selectors:** Find stable UI selectors (prefer `data-testid` or ARIA roles).
2. **Scaffold Hooks:** Set up `beforeEach` for navigation and state reset.
3. **Simulate Actions:** Write steps mimicking user actions (click, fill, route interception).
4. **Add Assertions:** Verify UI state (visibility, text content, URL changes).
5. **Isolate State:** Ensure the test does not depend on previous tests.

## Validation Criteria
- Tests must not rely on fragile CSS classes (`.btn-blue`).

## Safety Considerations
- Warn the user if the test attempts to process real payments or modify production data.

## Expected Output
A robust E2E test file (e.g., `checkout.spec.ts`) with clear, readable steps.

## Examples
**User:** "Write a Playwright test for the login flow."
**Agent:** Creates `login.spec.ts`, navigates to `/login`, fills credentials, clicks submit, and asserts the dashboard route.