---
name: qa-api-testing
description: Generates automated API tests to validate endpoints. Use when testing RESTful APIs and HTTP responses. Not for frontend/backend contract validation (use api-check) or access control testing (use security-access-regression).
metadata:
  collection: vibe.md
  group: qa
---

# QA API & Backend Testing

## Purpose
Validates backend API endpoint status codes, payloads, and data structures.

## When to Use
- Writing automated integration tests for backend API routes and microservices.

## Prerequisites
- Access to test database/staging API environment.

## Step-by-Step Instructions
1. **Environment Check:** Confirm with the user that the target environment is NOT production before writing or executing POST, PUT, DELETE, or teardown scripts.
2. **Review Routes:** Identify endpoints, expected request payloads, and status codes.
3. **Write Tests:** Create request specs using the project's existing test framework (or Supertest/PyTest).
4. **Validate Schema:** Assert status codes (200, 400, 401) and payload body structure.

## Safety Considerations
- Never execute state-changing or teardown operations on production environments.

## Examples
**User:** "Write tests for `/api/users`."
**Agent:** Confirms staging environment, creates API test cases for GET and POST endpoints, and asserts response contracts.