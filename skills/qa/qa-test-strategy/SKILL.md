---
name: qa-test-strategy
description: Analyzes requirements to generate test plans. Use when mapping out test scenarios for specific requirements. Not for writing the actual test code.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---


# QA Test Strategy & Planning

## Purpose
To define a clear, risk-based testing strategy before any test code is written, ensuring maximum coverage and efficiency.

## When to Use
- When starting a new feature or project.
- To map out test scenarios for specific requirements.
## When NOT to Use
- When the user explicitly asks to write the actual test code (use specific automation skills instead).

## Prerequisites
- Access to feature requirements, user stories, or architecture documents.

## Step-by-Step Instructions
1. **Analyze Requirements:** Review the provided feature description or code.
2. **Identify Risks:** Highlight potential breaking points and edge cases.
3. **Define Scenarios:** List specific test scenarios (Happy path, Negative, Edge cases).
4. **Allocate Test Types:** Decide which scenarios belong to Unit, API, or E2E layers.
5. **Draft the Plan:** Compile the findings into a structured Test Plan document.

## Validation Criteria
- The plan must cover both positive and negative flows.
- The allocation of tests (Unit vs. E2E) follows the Testing Pyramid principles.

## Safety Considerations
- Do not execute tests during this phase; focus only on planning.

## Expected Output
A structured Markdown document containing: Feature Overview, Risk Assessment, Test Scenarios list, and Test Layer Allocation.

## Examples
**User:** "Plan tests for a new user registration feature."
**Agent:** Analyzes the requirement and outputs a Test Plan covering unit tests for email validation, API tests for the `/register` endpoint, and E2E tests for the UI flow.