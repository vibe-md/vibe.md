---
name: qa-performance-testing
description: Sets up load and stress tests. Use when simulating high user traffic and benchmarking response times. Not for functional edge-case validation.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---

# QA Performance & Load Testing

## Purpose
Simulates high user traffic to identify system bottlenecks, measure response times, and verify scalability.

## When to Use
- Preparing for a product launch or high-traffic event.
- Benchmarking API response times.
## When NOT to Use
- For functional validation of edge cases.

## Prerequisites
- Load testing tool installed (e.g., k6). Target environment specs.

## Step-by-Step Instructions
1. **Define Scenario:** Establish target Virtual Users (VUs), duration, and ramp-up stages.
2. **Script the Load:** Write the HTTP requests with appropriate think time (sleep) between actions.
3. **Set Thresholds:** Define pass/fail criteria (e.g., 95th percentile response time < 300ms).
4. **Handle Auth:** Implement logic to handle tokens efficiently across thousands of VUs.
5. **Analyze Results:** Provide instructions for reading the output metrics.

## Validation Criteria
- Script must include think times to accurately simulate real user behavior.

## Safety Considerations
- **CRITICAL:** Never execute load tests against Production environments without explicit, documented user authorization.

## Expected Output
A load testing script (e.g., `load.k6.js`) and execution instructions.

## Examples
**User:** "Create a k6 script to stress test our search API."
**Agent:** Outputs a k6 script that ramps up to 100 VUs over 1 minute, hits the search endpoint, and asserts that the error rate remains below 1%.