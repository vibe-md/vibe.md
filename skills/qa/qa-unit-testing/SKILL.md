---
name: qa-unit-testing
description: Creates unit tests for isolated functions and modules. Use when testing utility functions or pure logic in isolation with mocked dependencies. Not for test-first React component development (use test-first-react).
metadata:
  collection: vibe.md
  group: qa
---

# QA Unit Testing

## Purpose
Tests individual functions, utilities, and modules in isolation with mocked dependencies.

## When to Use
- Writing unit tests for pure functions, algorithms, and isolated application logic.

## Step-by-Step Instructions
1. **Locate Test Framework:** Identify the project's test runner (e.g., Jest, Vitest, PyTest) and test execution command.
2. **Analyze Logic:** Identify inputs, expected outputs, pure functions, and edge conditions.
3. **Setup Mocks:** Explicitly mock external dependencies, databases, network calls, and timers to isolate the unit under test.
4. **Implement Tests:** Write unit tests covering happy paths, negative inputs, and boundary values.
5. **Execute & Verify:** Run the test suite using the project's CLI command to confirm passing tests.
6. **Stop Condition:** If a unit test fails due to a bug in the target code, stop and report the bug to the user. Do NOT modify the target code logic or weaken test assertions without explicit user instructions.

## Examples
**User:** "Add unit tests for `formatCurrency`."
**Agent:** Identifies Jest runner, creates test cases covering positive values, zero, negative numbers, and invalid inputs, runs Jest, and verifies all pass.