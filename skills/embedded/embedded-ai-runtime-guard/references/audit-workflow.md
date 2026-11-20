# Audit Workflow and Report Template

This reference defines the repeatable workflow for `embedded-ai-runtime-guard`.

## 1. Initial Discovery

Inspect the project without modifying it. Identify, where available:

- Languages, build system, target processor, board, and memory layout.
- Bare-metal, RTOS, or embedded Linux environment.
- AI framework, model runtime, model location, and inference lifecycle.
- Task/thread priorities, interrupt contexts, synchronization, and communication paths.
- Sensor sources, preprocessing, tensor buffers, and data ownership.
- Hardware abstraction layers, drivers, actuator destinations, and interlocks.
- Documented deadlines, watchdog periods, memory budgets, and safe-state requirements.
- Existing unit, integration, simulation, fault-injection, and hardware-in-the-loop tests.

Record unknowns. Do not infer target limits from common defaults.

## 2. Map the Execution and Data Flow

Trace the actual path, including error branches:

`Sensor -> Validation -> Preprocessing -> Inference -> Output Validation -> Decision -> Driver -> Actuator`

Also trace:

- Initialization, model loading, and model replacement.
- Inference worker creation, scheduling, cancellation, and shutdown.
- Timeout, exception, invalid-output, stale-output, and resource-failure paths.
- Fallback entry, fallback operation, recovery, and return to AI mode.
- Watchdog health checks and reset/restart behavior.

Identify which work runs in an ISR, high-priority task, control loop, worker thread, callback, or remote request.

## 3. Memory and Resource Review

Inspect initialization and repeated runtime paths for:

- `malloc`, `calloc`, `realloc`, `new`, `delete`, and dynamic container growth.
- Tensor arena, scratch buffer, model context, KV-cache, and input/output buffer bounds.
- Stack sizing, recursion, large local objects, and task creation parameters.
- Allocation failure handling and partial initialization cleanup.
- File descriptors, sockets, camera frames, DMA buffers, queues, locks, and worker/process lifecycle.
- Python object churn, unbounded queues/caches, tensor copies, model reloads, and subprocess cleanup.

Do not flag dynamic allocation solely because it exists. Consider frequency, boundedness, fragmentation exposure, allocator behavior, failure handling, and whether it occurs in a timing-critical path.

## 4. Real-Time, Concurrency, and Watchdog Review

Inspect:

- Synchronous inference or network calls in critical loops or ISRs.
- Blocking locks, unbounded waits, queue operations, and retries.
- Priority inversion and resource contention.
- Deadline measurement and enforcement.
- Worker cancellation and timeout semantics.
- Whether the watchdog is serviced only after meaningful health checks.
- Whether AI-worker failure can starve control, monitoring, or recovery tasks.
- Reset loops and safe-start behavior.

Do not impose a universal timeout such as 500 ms. Compare implementation behavior with documented system deadlines and watchdog constraints.

## 5. Fallback Trace

For each applicable failure, follow the control flow to the final output or state transition:

- AI timeout or deadline miss.
- Inference exception or worker crash.
- Model unavailable or initialization failure.
- Invalid, non-finite, out-of-range, low-confidence, or stale result.
- Sensor failure or stale sensor data.
- Network/remote API loss.
- Resource exhaustion or allocation failure.
- Repeated inference failure and watchdog reset.

Inspect the fallback body, dependencies, inputs, outputs, entry/exit rules, retry limits, and observability. Use `references/fallback-engineering.md`.

## 6. Sensor, Actuator, and Model Review

Trace sensor validation before tensor copies and model invocation. Trace AI output validation before any hardware write. Inspect model loading and updates where relevant. Use `references/safety-controls.md`.

## 7. Test and Verification Review

Inspect existing tests and determine whether they assert observable behavior rather than merely checking that a handler was called. Identify missing unit, fault-injection, integration, simulation, and HIL tests. Use `references/verification-and-testing.md`.

## 8. Audit Report Template

# Embedded AI Runtime & Safety Audit

## Executive Summary

- Target platform and execution environment:
- AI runtime/model:
- Languages:
- Inspected scope:
- Overall assessment:
- Findings by severity:
- Key unverified assumptions:

## Architecture and Execution Flow

- Sensor/input path:
- Inference path:
- Control and scheduling context:
- Output/actuator path:
- Fallback and recovery path:
- Uninspected HAL/driver dependencies:

## Findings

For each finding:

- **ID:**
- **Title:**
- **Severity:**
- **Confidence:**
- **Control status:**
- **Location:** `path:line`
- **Evidence:**
- **Traced path:**
- **Failure scenario and impact:**
- **Recommended remediation:**
- **Proposed regression test:**
- **Limitations:**

## Non-AI Fallback Assessment

- Failure modes traced:
- Fallback implementation status:
- Independence from AI/network:
- Input freshness and validation:
- Output validation/interlocks:
- Entry/exit/retry behavior:
- Observability:
- Missing safe-state requirements:
- Questions for the developer:
- Proposed implementation status:

## Control Assessment Matrix

| Control | Status | Evidence | Confidence |
|---|---|---|---|
| Bounded memory and allocation | | | |
| Resource lifecycle and cleanup | | | |
| Stack and buffer capacity | | | |
| Real-time deadlines | | | |
| Non-blocking critical execution | | | |
| Concurrency and priority behavior | | | |
| Watchdog independence | | | |
| Non-AI fallback completeness | | | |
| Fallback recovery transitions | | | |
| Actuator validation/interlocks | | | |
| Sensor validation | | | |
| Model runtime/integrity | | | |
| Failure and regression tests | | | |

## Proposed Remediation

Separate each proposed code change and test. State assumptions and do not apply changes automatically.

## Verification Plan and Limitations

List static evidence, tests already run by the developer, tests not run, runtime measurements needed, HIL requirements, missing documentation, and hardware validation still required.
