# Embedded AI Safety Controls

Use this reference to assess each control in the actual architecture. A control is applicable only when the relevant component or failure path exists.

## 1. Memory and Resource Determinism

Review:

- Repeated allocation/deallocation in inference or control loops.
- Dynamic vector/string/container growth.
- Tensor arena, scratch, model context, KV-cache, and I/O buffer capacities.
- Stack depth, recursion, task stack sizes, and large local buffers.
- Allocation failure and partial initialization behavior.
- Cleanup on exceptions, timeouts, cancellation, and model replacement.
- File descriptors, sockets, camera frames, DMA buffers, queues, and worker lifecycle.
- Python object churn, unbounded queues/caches, tensor duplication, and process leaks.

Assess allocation location, frequency, upper bounds, allocator characteristics, fragmentation risk, timing constraints, and failure handling. Static allocation is not automatically safe if the configured capacity is wrong or unchecked.

## 2. Real-Time Execution

Review:

- Inference and remote requests inside control loops or ISRs.
- Blocking mutexes, semaphores, queues, sleeps, and network calls.
- Scheduling priorities, priority inversion, and CPU contention.
- Explicit deadlines and how missed deadlines are detected.
- Worker isolation, cancellation, and bounded result handoff.
- Whether the control loop can continue if inference stalls.

Compare timing to documented system requirements. Never invent a universal timeout.

## 3. Watchdog Independence

Review:

- Watchdog period and servicing location.
- Whether servicing follows meaningful health checks.
- Whether AI inference success is incorrectly required to service the watchdog.
- Whether a stalled AI worker can block watchdog monitoring.
- Reset cause handling, boot recovery, restart loops, and safe-start behavior.

Do not recommend feeding the watchdog unconditionally. A watchdog should reflect system health, not merely prove that some code is executing.

## 4. AI Output Freshness and Validity

Before AI output influences control, assess:

- Result timestamp, sequence number, and age limit.
- Model/runtime identity and expected output schema.
- Numeric type, dimensions, units, finite values, and range.
- Confidence/uncertainty policy when one is explicitly defined.
- Behavior on missing, duplicated, reordered, malformed, or stale results.
- Whether output validation is independent of model-generated claims.

Do not invent a confidence threshold. If none is specified, report a missing requirement rather than selecting one.

## 5. Actuator Command Protection

Trace each AI-derived command to the driver. Assess:

- Physical min/max limits grounded in device requirements.
- Units, numeric conversion, overflow, NaN, and Inf rejection.
- Slew-rate and acceleration limits.
- State-dependent envelopes and plausibility checks.
- Independent interlocks and hardware-level protections.
- Validation immediately before the hardware write.
- Behavior when a command is rejected.

Clamping alone is not a complete safety case. The permitted range and transition behavior must come from system requirements and hazard analysis.

## 6. Sensor and Buffer Safety

Before preprocessing or tensor copy, inspect:

- Pointer validity, buffer length, array bounds, and tensor dimensions.
- Integer overflow in size calculations.
- Type conversion, alignment, and serialization.
- NaN/Inf, impossible values, invalid timestamps, and stale readings.
- Malformed packets and partial sensor frames.
- Concurrent access, DMA ownership, and lifetime.
- Validation consistency through preprocessing.

## 7. Model Runtime and Artifact Integrity

Review:

- Model load/init failures and compatibility checks.
- Input/output tensor shape and type validation.
- Memory reservation and runtime configuration.
- Model identity/version and controlled replacement.
- Cleanup when loading or replacing a model fails.
- Integrity checks for external storage and OTA artifacts.

A checksum detects accidental corruption only if its expected value is trusted independently. Authenticity requires a trusted signature-verification design, including key management and update policy. Do not describe an untrusted checksum as authentication.

## 8. Failure Independence

For each protection, ask whether it depends on the component that may have failed. Examples:

- Can fallback execute if the AI worker is deadlocked?
- Can the watchdog detect failure if the scheduler is starved?
- Can output limits still be enforced if the model returns malformed data?
- Can recovery run if the network is unavailable?
- Can the system enter its defined state if a sensor is invalid?

Record dependencies that are outside the inspected code as `NOT VERIFIED`.
