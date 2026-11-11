---
name: qa-bug-triage
description: Investigates failing tests and generates bug reports. Use when analyzing logs, stack traces, or CI failures. Not for planning new features (use qa-test-strategy).
metadata:
  collection: vibe.md
  group: qa
---

# QA Bug Investigation & Triage

## Purpose
Diagnoses root causes of test failures, CI errors, and user-reported bugs.

## When to Use
- Analyzing CI failure logs, stack traces, or flaky test outputs.

## Prerequisites
- Error logs or stack trace output.

## Step-by-Step Instructions
1. **Analyze Failure:** Examine the stack trace, error message, or screenshot.
2. **Isolate Root Cause:** Trace whether the issue stems from application code, test data, or environment timing.
3. **Draft Bug Report:** Format a bug report containing reproduction steps, expected vs. actual behavior, and suspected root cause.
4. **Review with User:** Present the drafted report to the user. Do NOT file a ticket to external issue trackers unless explicitly requested.

## Safety Considerations
- Sanitize and redact any personal data (PII) or API keys found in logs.

## Examples
**User:** "Analyze why our checkout test failed in CI."
**Agent:** Parses the log, identifies a 500 server response from the payment gateway, and drafts a detailed bug report for user review.