---
name: qa-performance-testing
description: Sets up load and stress tests. Use when simulating high user traffic and benchmarking response times. Not for functional edge-case validation.
metadata:
  collection: vibe.md
  group: qa
---

# QA Performance & Load Testing

## Purpose
Simulates concurrent user load to evaluate system response times and scalability.

## When to Use
- Benchmarking performance thresholds and load limits for endpoints.

## Step-by-Step Instructions
1. **Check Tooling:** Inspect existing performance tools. Ask the user before installing CLI binaries or packages (e.g., `k6`, `artillery`).
2. **Define Parameters:** Confirm Virtual Users (VUs) count, duration, and target URL with the user.
3. **Script Scenario:** Write the load script with think time (sleep) between requests.
4. **Run & Report:** Present metrics (p95 response time, throughput, error rates).

## Safety Considerations
- **CRITICAL:** Do NOT run load tests against production environments without explicit authorization.

## Examples
**User:** "Load test our search API."
**Agent:** Asks before installing k6, confirms staging target, scripts 50 VUs for 1 minute, and reports response metrics.