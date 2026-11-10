---
name: qa-api-testing
description: Generates automated API tests to validate endpoints. Use when testing RESTful APIs and HTTP responses. Not for testing UI rendering.
metadata:
  collection: vibe.md
  group: qa
  maintainers:
    - Faigy-Rosenfeld
    - odelia50872
---

# QA API & Backend Testing

## Purpose
Validates that backend services return correct data, handle errors properly, and conform to API contracts.

## When to Use
- Testing RESTful APIs, GraphQL endpoints, or microservices.
- Validating HTTP status codes and JSON schemas.
## When NOT to Use
- Testing UI rendering (use E2E or Unit).

## Prerequisites
- Target API documentation or endpoint access. Tools like Supertest or PyTest.

## Step-by-Step Instructions
1. **Identify Endpoints:** Review routes, required headers, and payloads.
2. **Setup Environment:** Configure authentication tokens or database seeding if required.
3. **Write Requests:** Cover GET, POST, PUT, and DELETE methods.
4. **Assert Responses:** Validate HTTP status codes (200, 400, 401) and response bodies.
5. **Teardown:** Ensure test data is cleaned up after execution.

## Validation Criteria
- Assertions must check both the status code and the structure of the returned payload.

## Safety Considerations
- Do not run destructive API tests (DELETE, POST) against production databases.

## Expected Output
An API automation script (e.g., `users.api.spec.ts`) ready to run in the test environment.

## Examples
**User:** "Create API tests for the `/api/users` endpoint."
**Agent:** Sets up a Supertest script, writing cases to fetch the user list (200) and test validation errors for missing fields (400).