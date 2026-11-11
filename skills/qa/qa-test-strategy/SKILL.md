---
name: qa-test-strategy
description: Analyzes requirements to generate test plans. Use when mapping out test scenarios for specific requirements. Not for writing the actual test code.
metadata:
  collection: vibe.md
  group: qa
---

# QA Test Strategy & Planning

## Purpose
Establishes a structured, risk-based test plan prior to test creation.

## When to Use
- Planning test coverage and scenarios for new features or user stories.

## Step-by-Step Instructions

1. **Check Existing Baseline:** Identify the project's current test suite and test commands. Run existing tests to verify that the baseline is green before planning new work.

2. **Analyze Requirements:** Review feature specifications or user stories for positive and negative paths.

3. **Identify Scenarios:** Map happy path, edge cases, boundary values, and potential failure modes.

4. **Assign Test Layers:** Distribute scenarios across Unit, API, and E2E layers adhering to the testing pyramid.

5. **Output Test Plan:** Draft a structured Markdown document outlining test scope, risks, and scenario allocations.

6. **Stop Condition:** If existing baseline tests fail, stop and notify the user before proceeding with new feature test planning.

## Examples

**User:** "Create a test plan for user registration."

**Agent:** Checks current test status, outlines unit validation rules, API contract checks, and E2E registration journeys in a Test Plan document.