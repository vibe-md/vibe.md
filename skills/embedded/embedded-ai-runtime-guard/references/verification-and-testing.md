# Verification and Regression Testing

This reference guides test recommendations for embedded AI runtime controls.

## 1. Test Strategy

Prefer a layered strategy:

1. Unit tests for pure validation and state-transition logic.
2. Fault-injection tests for timeout, invalid output, allocation failure, and worker failure.
3. Integration tests for task, queue, and driver boundaries.
4. Simulation for system-level timing and state behavior.
5. Hardware-in-the-loop (HIL) for hardware-dependent behavior, performed only by qualified personnel in an approved safe environment.

The default audit is read-only and does not execute firmware, flash hardware, or issue actuator commands.

## 2. Required Test Questions

For each test, define:

- Preconditions and controlled test environment.
- Injected failure and injection point.
- Expected state transition.
- Expected actuator command or explicitly mocked interface result.
- Deadline/latency assertion where requirements provide a bound.
- Resource cleanup assertion.
- Recovery and repeated-failure behavior.
- What the test cannot prove.

Tests should assert observable outcomes, not merely that a fallback function was called.

## 3. Recommended Scenarios

- Model initialization failure.
- Inference timeout and cancellation.
- Worker crash/termination.
- Invalid output schema.
- NaN/Inf and out-of-range values.
- Stale or reordered inference result.
- Sensor buffer shorter/longer than expected.
- Allocation failure or bounded-pool exhaustion.
- Queue saturation and lock contention.
- Watchdog health-check failure.
- Fallback activation and recovery.
- Repeated failures without unbounded retries.
- Model replacement failure and rollback behavior, if supported.
- Actuator output rejected by independent validation.

## 4. Python Process Lifecycle

When inference runs in a child process, assess whether timeout handling actually terminates and reaps the child. A robust proposal should consider:

- A bounded join/wait period.
- Graceful termination where supported.
- A second bounded wait.
- Forced kill only when necessary and supported by the platform.
- A final join/wait to reap the process.
- Cleanup of pipes, queues, shared memory, and temporary resources.
- Handling of already-exited processes and races.
- Ensuring fallback does not wait indefinitely for cleanup.

Do not claim a child has stopped merely because a timeout exception was raised. Verify the process state and cleanup path.

## 5. Test Safety

- Use mocks/fakes for actuator interfaces in unit tests.
- Do not connect tests to live equipment by default.
- Keep test credentials and proprietary model files out of logs.
- Do not use arbitrary physical thresholds; derive expected values from requirements.
- Run HIL only with explicit authorization, an approved test plan, and appropriate physical safeguards.

## 6. Test Report

For each proposed test, state:

- Test name and level.
- Failure injected.
- Expected behavior.
- Assertion(s).
- Required mocks/fixtures.
- Platform assumptions.
- Whether it was proposed, inspected, or actually executed.
