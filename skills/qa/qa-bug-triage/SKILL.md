---
name: qa-bug-triage
description: Investigates failing tests and generates bug reports. Use when analyzing logs, stack traces, or CI failures. Not for planning new features.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---

# QA Bug Investigation & Triage

## Purpose
Moves beyond writing tests to actively diagnosing why a test or application failed, identifying the root cause, and documenting it.

## When to Use
- A CI pipeline fails and the reason is unclear.
- Investigating a user-reported bug or a stack trace.
## When NOT to Use
- When planning new features (use `qa-test-strategy`).

## Prerequisites
- Access to error logs, stack traces, or failing test output.

## Step-by-Step Instructions
1. **Analyze Failure:** Review the provided logs, stack trace, or test screenshot.
2. **Determine Flakiness:** Check if the failure is a real bug, a test sync issue (flaky test), or a data issue.
3. **Isolate Root Cause:** Trace the error back to the specific function or network request.
4. **Define Steps to Reproduce:** Extract clear, step-by-step instructions to reproduce the issue.
5. **Draft Bug Report:** Create a standardized ticket.

## Validation Criteria
- The report must clearly distinguish between the "Expected Behavior" and "Actual Behavior".

## Safety Considerations
- Mask any sensitive user data (PII) or secrets found in the logs before processing.

## Expected Output
A professional Bug Report containing: Title, Severity, Environment, Steps to Reproduce, Expected vs. Actual, and Root Cause Analysis.

## Examples
**User:** "Our E2E test failed on the payment step. Here is the CI log."
**Agent:** Analyzes the log, identifies a `Timeout exceeding 30000ms waiting for selector .success-msg`, determines the API returned a 500 error, and outputs a complete Bug Report for the backend team.