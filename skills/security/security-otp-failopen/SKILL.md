---
name: security-otp-failopen
description: Writes local tests that prove a one-time code (SMS, email or authenticator) cannot be replayed, guessed, reused across accounts or purposes, and cannot fail open when the delivery provider errors or times out. Use when adding or changing code verification, password reset by code, or step-up confirmation. Not for access-control matrices, general diff review, login implementation, or testing a live service.
license: MIT
compatibility: Requires source code, the project's test runner, and an isolated test environment with synthetic accounts and a fake delivery provider. No external account, phone number or network access required.
metadata:
  collection: vibe.md
  group: security
  author: talforsher
---

# One-time code fail-open tests

## Purpose

Make the whole life of a verification code an executable contract: issued for one purpose, to one account, single use, expiring on schedule, and never satisfied by the delivery provider being unavailable.

The specific failure this skill exists to catch: code that treats "could not verify" as "verified".

## When to Use

- Add regression coverage for a code-based login, password reset, phone or email change, or step-up confirmation.
- Verify a change to code generation, storage, expiry or the provider adapter.
- Prove that an outage, timeout, or missing provider response blocks the flow instead of completing it.

For a read-only review of a diff, use `pre-commit-security-review` if installed. Use `security-access-regression` when the question is who may read or change whose records. Use `security-agent-guard` for AI-specific risks. This skill writes tests for one verification flow, not a general audit.

## Prerequisites and permissions

- Source code, the existing test runner, and the project's session or token fixtures.
- A disposable local environment with synthetic accounts and a fake delivery adapter. Prefer the framework's in-process test client and a captured or stubbed provider, not a sandbox key that sends real messages.
- The request to add tests permits local test and fixture edits. Do not change application policy, rewrite the flow, or touch production code without a separate request. Never install dependencies, point tests at a real provider endpoint, or send messages to real phone numbers or addresses.

## Instructions

1. **Choose one flow.** Read the handler that issues the code, the handler that verifies it, the storage layer, and the provider adapter. Identify from code, not from marketing copy, what a positive verification requires. If no flow was named, pick the one in the current diff; do not test every code in the application.
2. **Write down the contract before the tests.** For the chosen flow, state: issuer, recipient, code length and generation source, storage form, time to live, single-use rule, attempt limit, and the exact condition that authorizes the protected action. Use documented product behaviour where it exists. Where the intended rule is unclear, leave that case explicitly undecided rather than blessing today's implementation. Start from the [test matrix](assets/otp-test-matrix.md).
3. **Confirm the environment cannot send or authenticate outside the sandbox.** Check that the provider adapter is replaced, that no real destination is reachable, and that test accounts are synthetic. A configured key with a `test` prefix is not proof. If isolation cannot be established, write the tests and leave them unexecuted with that reason.
4. **Test the allowed path first.** A correct code for the correct account completes the protected action once. Without this control, a flow that rejects everything would look secure. Confirm the session or token actually changes state.
5. **Test each lifecycle breach through the same boundary.** Select only cases that the contract calls for from the [failure modes](references/failure-modes.md): replay after success, redemption of an expired code, a code issued for one account used by another, a code issued for one purpose used for another, and concurrent redemption of the same code. Change one variable at a time against a known-good code.
6. **Test the provider going quiet.** Make the adapter raise, time out, return an error body, return a malformed or empty response, and return `5xx`. For each, the protected action must not complete unless the product's documented offline path allows it explicitly. Also check that a failure to deliver does not leave a code valid that the user never received.
7. **Test guessing and cost.** Verify that the documented attempt limit is enforced per code and per account, that a failed attempt does not extend the window, and that issuance itself is limited so one account cannot be used to send many messages. Do not run a brute-force search; assert the boundary with a small number of attempts.
8. **Check that the tests can fail.** On a disposable copy only, introduce the specific defect the test guards: make the provider error path return success, or remove the single-use flag. The relevant test must fail. Restore the copy and record both outcomes. Never mutate the working tree under test.
9. **Run and report.** Run the focused tests, then the existing suite. Report each case, expected result, actual observation, and anything not exercised, including any real-provider behaviour you could not observe. Do not claim the flow is secure because the cases passed. Show the diff; do not stage, commit, push or deploy it.

## Examples

**User:** "We just added an SMS code to the password reset. Test it."

**Agent:** Reads the issue and verify handlers plus the SMS adapter, fills the matrix for that flow, then proves: correct code resets once; the same code fails on replay; an expired code fails; another account's code fails; a reset code cannot confirm a login. Uses a fake adapter, so no message leaves the machine.

**User:** "Our provider had an outage last week. Make sure that can't log anyone in."

**Agent:** Makes the fake adapter raise, time out, and return a `5xx`, then asserts the flow ends unauthenticated in each case. Adds the single mutation that returns success from the error handler and confirms the test catches it.

**User:** "Test our new SIM-swap step too, against the carrier."

**Agent:** Keeps the work local. Tests how the application treats each possible carrier answer, including unavailable and unsupported, using recorded shapes. Does not call a live carrier, and states that real-provider behaviour was not observed.
