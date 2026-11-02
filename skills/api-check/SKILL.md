---
name: api-check
description: Compare frontend API requests and consumers with backend routes to find mismatches in methods, paths, field names, response shapes, and error handling. Use for API integration reviews and debugging frontend/backend contract incompatibilities; report exact mismatches with file references.
metadata:
  categories: Debugging, Frontend, Backend
  maintainers: ItayShar
---

# API Check

## When to Use

Use this skill to review API integrations or diagnose incompatibilities between frontend requests and backend routes.

## Instructions

Audit frontend/backend contracts within the requested feature, endpoints, or diff. If no scope is specified, inventory callers and routes in the available project. Report findings; edit code only if fixes are requested.

### Compare effective behavior

Trace frontend calls through shared clients, serializers, interceptors, base URLs, and proxies to mounted backend routes, validators, handlers, and response middleware. Trace returned data through client transforms to actual consumers. Account for route prefixes and rewrites before declaring a route missing. Use runtime implementation as evidence, checking schemas, generated clients, types, and tests for drift.

Compare:

- Methods and paths: HTTP verbs, effective URLs, route parameters, query parameters, encoding, and relevant routing behavior.
- Request fields: exact names and nesting, body/query/path placement, content type, required fields, nullability, types, enums, and defaults. Account for aliases, serialization, and coercion actually applied.
- Response shapes: status codes, empty bodies including 204, envelopes, arrays versus objects, field names, nesting, pagination, nullability, and serialized values. Compare what consumers read against each relevant server response branch.
- Error handling: validation, authentication/authorization, not-found, and application errors. Follow status codes and error payloads through middleware and client wrappers to catch branches or UI handling. Check rejection of non-success statuses, error field access, and parsing of empty or non-JSON bodies. Distinguish network failures from server responses.

Different variable names, unused response fields, unused backend routes, or types reconciled by adapters are not evidence of a mismatch. Use existing tests or isolated local checks when needed; do not call live mutating endpoints merely to verify contracts.

### Report findings

Lead with confirmed mismatches ordered by user impact. For each, provide:

- The affected operation and exact frontend request or expectation versus backend requirement or output. Use concrete field paths and values where useful.
- Verified file and line references for both sides, plus relevant wrapper or configuration evidence. For missing routes, cite the caller and searched registration locations and scope rather than inventing a definition.
- The trigger, observable consequence, and minimal alignment recommendation. If the intended contract is unclear, explain the choice without assuming which side must change.

Consolidate symptoms sharing a root cause. Separate unverified concerns from confirmed findings and identify missing evidence. Finish with inspected coverage, validation performed, and limitations such as missing repositories or dynamic routes. If no mismatches are found, say so only within the inspected scope.

## Examples

- "Use $api-check to compare the checkout frontend requests with backend routes. Report exact mismatches with file and line references."
- "Review this diff for API contract drift, including request fields, response shapes, and error handling."

Example finding (illustrative file references): `frontend/orders.ts:42` sends `customerId`, but `backend/orders.ts:18` requires `customer_id`. Submitting an order fails validation with HTTP 400. Align the submitted field name with the accepted contract.
