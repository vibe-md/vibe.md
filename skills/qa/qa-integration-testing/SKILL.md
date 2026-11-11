---
name: qa-integration-testing
description: Creates integration tests that verify interactions between application components, databases, APIs, and external services. Use when testing real component integrations in a controlled test environment. Not for isolated unit testing (use qa-unit-testing).
metadata:
  collection: vibe.md
  group: qa
---

# QA Integration Testing

## Purpose

Verifies that multiple application components work correctly together by testing their actual interactions, interfaces, and data exchange in a controlled test environment.

## When to Use

- Testing interactions between application layers or modules.
- Verifying database queries, persistence, and data retrieval.
- Testing API endpoints and service communication.
- Checking integrations between internal components and external services.
- Detecting integration issues that isolated unit tests may miss.

## Step-by-Step Instructions

1. **Locate Test Framework:** Identify the project's test runner, integration testing tools, and existing test execution commands.

2. **Map Component Interactions:** Identify the components involved in the integration, including APIs, databases, services, and shared interfaces.

3. **Prepare Test Environment:** Configure the required test infrastructure, such as a test database, local API server, or service containers. Ensure test data is isolated from production data.

4. **Configure Test Dependencies:** Use real implementations of the components whose integration is being tested. Mock only unrelated external services when necessary.

5. **Implement Integration Tests:** Write tests covering:
   - Successful communication between components.
   - Correct data exchange and transformations.
   - Database persistence and retrieval.
   - API request and response behavior.
   - Error handling and failure scenarios.
   - Transaction handling and consistency where applicable.

6. **Manage Setup and Cleanup:** Initialize the required test environment and test data before execution. Clean up created records, connections, temporary resources, and containers after tests finish, including when a test fails.

7. **Execute & Verify:** Run the integration test suite and inspect the results. Verify that failures are caused by actual integration issues rather than incorrect test configuration.

8. **Stop Condition:** If integration tests fail because of an application bug, stop and report the failure, its affected components, and relevant evidence. Do NOT modify production logic or weaken test assertions without explicit user instructions.

## Examples

**User:** "Write integration tests for the user registration API."

**Agent:** Identifies the API and database dependencies, configures an isolated test database, sends registration requests to the real API, verifies that user records are persisted correctly, tests duplicate registration and invalid input scenarios, and cleans up the test data afterward.