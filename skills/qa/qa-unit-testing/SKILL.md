---
name: qa-unit-testing
description: Creates unit and integration tests for isolated functions. Use when testing utility functions or components in isolation. Not for test-first React component development (use test-first-react).
metadata:
  collection: vibe.md
  group: qa
---

# QA Unit & Integration Testing

## Purpose
Tests individual functions, utilities, and components in isolation.

## When to Use
- Writing unit tests for pure functions, algorithms, and isolated application logic.

## Step-by-Step Instructions
1. **Analyze Logic:** Identify inputs, outputs, and edge conditions.
2. **Setup Mocks:** Mock external dependencies and network calls.
3. **Implement Tests:** Use existing test runner (Jest, Vitest, PyTest) to cover logic branches.

## Examples
**User:** "Add unit tests for `formatCurrency`."
**Agent:** Creates test cases covering positive values, zero, negative numbers, and invalid inputs using Jest.