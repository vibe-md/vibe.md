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
1. **Analyze Requirements:** Review feature specifications or user stories.
2. **Identify Scenarios:** Map happy path, negative path, and boundary cases.
3. **Assign Test Layers:** Distribute scenarios across Unit, API, and E2E levels.
4. **Output Test Plan:** Generate a structured Markdown document outlining the plan.

## Examples
**User:** "Create a test plan for user registration."
**Agent:** Outlines unit validation rules, API contract checks, and E2E registration journeys in a Test Plan document.