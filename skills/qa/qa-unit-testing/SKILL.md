---
name: qa-unit-testing
description: Creates unit and integration tests for isolated functions. Use when testing utility functions or components in isolation. Not for testing full user journeys across a browser.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---

# QA Unit & Integration Testing

## Purpose
Ensures individual components and functions work correctly in isolation, enforcing high code coverage and reliability.

## When to Use
- Writing tests for utility functions, algorithms, or state managers.
- Testing UI components in isolation (e.g., React Testing Library).
## When NOT to Use
- When testing full user journeys across a real browser (use `qa-e2e-playwright`).

## Prerequisites
- The testing framework (Jest, PyTest, etc.) is configured in the project.

## Step-by-Step Instructions
1. **Analyze Functionality:** Understand the inputs and expected outputs of the target code.
2. **Setup Mocks:** Use mocking techniques for external services, timers, or network requests.
3. **Write Cases:** Write tests for happy paths, negative paths, and edge cases.
4. **Group Logically:** Use `describe` and `it`/`test` blocks clearly.
5. **Review Coverage:** Ensure branches and statements are adequately covered.

## Validation Criteria
- Tests must not make real network or database calls (must be isolated).

## Safety Considerations
- Never mutate the actual source code logic to make a test pass.

## Expected Output
A complete, runnable test file (e.g., `utils.test.js`) with proper assertions.

## Examples
**User:** "Add unit tests for the `calculateTotal` function."
**Agent:** Creates a test file, imports the function, and writes test cases for empty carts, discounted items, and invalid inputs using Jest.