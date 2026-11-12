---
name: embedded-ai-runtime-guard
description: Performs evidence-based security and runtime safety audits of embedded, microcontroller, RTOS, and edge AI applications using C/C++, Rust, MicroPython, or Python. Analyzes memory bounds, resource exhaustion, inference deadlines, blocking operations, watchdog independence, non-AI fallback completeness, hardware actuator validation, sensor inputs, and model runtime integrity. Identifies incomplete failure paths, asks for missing safety requirements, and proposes implementation-ready fixes and regression tests. Use when AI models or remote AI services interact with embedded software, real-time tasks, sensors, or physical hardware. Not for cloud-only applications or general code refactoring unrelated to embedded AI safety.
license: MIT
metadata:
  collection: vibe.md
  group: embedded
  author: Yael Tamari
---

# Embedded AI Runtime Guard

## 1. Purpose

Audit embedded and edge AI applications for runtime reliability, memory safety, deterministic behavior, and hardware protection.

The skill evaluates the complete interaction between:

- AI models and inference engines.
- Operating systems and RTOS tasks.
- Memory, stack, heap, and persistent resources.
- Sensor input pipelines.
- AI-generated decisions and commands.
- Hardware interfaces and actuators.
- Non-AI fallback and recovery mechanisms.

The primary objective is to identify situations where AI failure, excessive resource consumption, unpredictable execution time, corrupted output, or invalid hardware commands can cause system instability or unsafe physical behavior.

The skill must not assume that an AI model is reliable merely because its API call succeeds.

## 2. When to Use

Use this skill when reviewing:

- Embedded C/C++ or Rust applications integrating AI inference.
- Microcontroller firmware using TensorFlow Lite Micro or similar runtimes.
- FreeRTOS, Zephyr, or other real-time operating systems.
- Edge AI applications running on Raspberry Pi or NVIDIA Jetson.
- Robotics, drones, industrial controllers, and embedded automation.
- AI-assisted sensor processing and hardware control.
- Local inference or remote AI APIs that influence physical actuators.
- Systems requiring deterministic non-AI recovery when inference becomes unavailable.

### When Not to Use

Do not use this skill for:

- Cloud-only applications without hardware or real-time constraints.
- General web application security audits.
- General prompt injection reviews unrelated to embedded runtime safety.
- Pure code-style refactoring.
- Live hardware operation or physical actuator testing.

Use a more specialized security skill when the task falls outside embedded AI runtime safety.

## 3. Prerequisites and Initial Discovery

Before auditing, inspect the available project structure and identify:

1. Programming languages and build system.
2. Target hardware and processor architecture.
3. Operating system or RTOS.
4. AI framework and model execution environment.
5. Hardware abstraction layers and driver interfaces.
6. Sensor input sources.
7. Actuator output destinations.
8. Timing and memory requirements, if documented.
9. Existing fallback requirements and safety documentation.
10. Existing unit, integration, simulation, and hardware tests.

Do not invent missing configuration values.

If critical information is unavailable, record it as an audit limitation.

Ask focused clarification questions only when the missing information materially affects the safety assessment or the proposed implementation.

## 4. Operating and Safety Principles

### 4.1 Read-Only by Default

The audit must not modify project files.

The agent may:

- Read source code and configuration.
- Inspect existing tests.
- Trace function calls and state transitions.
- Analyze memory and timing-related code.
- Produce reports and proposed patches.

The agent must not:

- Overwrite source files.
- Automatically implement a fallback.
- Change hardware configuration.
- Flash firmware.
- Send physical commands.
- Modify production deployment settings.

Any proposed change must be presented separately.

Applying a patch requires explicit user approval.

### 4.2 Evidence-Based Findings

Every actionable finding must include:

- Exact file path.
- Line number or relevant code location.
- Observed implementation.
- Explanation of the missing or unsafe control.
- Realistic failure scenario.
- Potential runtime or physical consequence.
- Recommended remediation.
- Confidence level.

Do not report a vulnerability based only on a suspicious function name or keyword.

Trace the relevant control flow and data flow whenever possible.

### 4.3 No Assumed Physical Safe State

Never assume that any of the following is universally safe:

- Stopping a motor.
- Holding the previous command.
- Moving to a neutral position.
- Hovering.
- Opening or closing a valve.
- Disabling an actuator.
- Switching to a PID controller.

The correct behavior depends on the device, environment, operating conditions, and hazard analysis.

If the required behavior is undefined, request clarification before generating hardware-specific fallback logic.

### 4.4 Separate AI Failure from System Failure

Distinguish between:

- AI inference failure.
- AI timeout.
- Invalid or stale model output.
- Sensor failure.
- Memory exhaustion.
- Communication failure.
- RTOS scheduling failure.
- Hardware driver failure.
- Complete system failure.

Each failure category may require a different recovery strategy.

### 4.5 Static Evidence Is Not Runtime Proof

A static code audit cannot independently prove:

- Actual worst-case execution time.
- Physical actuator behavior.
- Real hardware safety.
- Absence of all memory leaks.
- Complete runtime memory consumption.
- Watchdog behavior under every hardware failure.

Mark these properties NOT VERIFIED unless sufficient runtime or hardware evidence is available.

## 5. Audit Workflow

Follow the stages in order.

### Stage 1: Architecture and Execution Mapping

Identify the complete AI-to-hardware pipeline.

Trace:

Sensor Input
-> Input Validation
-> Preprocessing
-> AI Inference
-> Output Validation
-> Decision Logic
-> Hardware Driver
-> Actuator

Also identify:

- AI initialization and shutdown.
- Model loading and unloading.
- Worker tasks and scheduling priorities.
- Communication channels.
- Timeout handling.
- Fallback entry and recovery paths.

Create a concise architecture summary.

### Stage 2: Memory and Resource Safety

Inspect initialization and runtime memory behavior.

Check:

1. Dynamic allocations in high-frequency or real-time paths.
2. Repeated malloc, calloc, realloc, new, and delete operations.
3. Dynamic container growth.
4. Tensor arena capacity.
5. Model input and output buffer bounds.
6. KV-cache and context memory limits.
7. RTOS task stack sizes.
8. Stack exhaustion and recursion risks.
9. Allocation failure handling.
10. File descriptor, socket, camera frame, and DMA buffer lifecycle.
11. Resource cleanup on timeout and exception paths.
12. Long-running resource accumulation.

For Python systems, inspect:

- Unbounded queues.
- Repeated object creation in high-frequency loops.
- Large tensor copies.
- Model reload behavior.
- Unbounded caches.
- Worker and process lifecycle.
- Unreleased resources.

Do not automatically classify every dynamic allocation as a defect.

Evaluate its location, frequency, boundedness, failure handling, and execution-time requirements.

Report missing capacity limits as a finding when the relevant resource can grow without an established bound.

### Stage 3: Real-Time Execution and Deadline Safety

Determine whether AI operations can interfere with time-critical control tasks.

Inspect:

1. Synchronous inference inside control loops.
2. Blocking remote AI requests.
3. Blocking mutex acquisition.
4. Unbounded queue waits.
5. Network operations inside high-priority tasks.
6. AI execution inside interrupt service routines.
7. Priority inversion.
8. Unbounded retry loops.
9. Deadline monitoring.
10. Cancellation and recovery behavior.

Verify that:

- Critical control loops have explicit timing requirements.
- AI execution has an appropriate execution budget.
- Inference does not block critical tasks indefinitely.
- AI results are checked for freshness.
- Missed deadlines trigger a defined recovery path.
- Worker failure does not prevent the control loop from progressing.

Do not assume a universal timeout such as 500 ms.

Use documented system requirements and task scheduling constraints.

### Stage 4: Watchdog and Recovery Independence

Inspect watchdog configuration and servicing behavior.

Check:

1. Whether the watchdog can detect a stalled AI worker.
2. Whether watchdog servicing depends on successful AI inference.
3. Whether a failed worker can prevent other critical tasks from progressing.
4. Whether watchdog servicing occurs only after meaningful system health checks.
5. Whether recovery after reset is defined.
6. Whether repeated resets can create an endless restart cycle.
7. Whether the device has a documented recovery or safe-start procedure.

Do not recommend continuously feeding the watchdog merely to avoid resets.

A watchdog must represent actual system health, not just task execution.

### Stage 5: Non-AI Fallback Completeness

This is a primary audit objective.

Inspect every relevant AI-dependent decision and hardware-control path.

Check whether the implementation handles:

- AI timeout.
- Inference exceptions.
- Model initialization failure.
- Model unavailable.
- Invalid output.
- NaN or Inf output.
- Low confidence.
- Stale output.
- Worker crash.
- Communication loss.
- Resource exhaustion.
- Repeated inference failure.

For each failure path, trace the actual fallback behavior.

A fallback is not complete merely because:

- A try/catch exists.
- An error is logged.
- A timeout variable is configured.
- A function named safe_mode exists.
- A TODO comment is present.
- The code returns without defining the resulting actuator state.

Inspect the fallback implementation itself.

Evaluate:

1. Is the handler reachable?
2. Is the fallback behavior explicitly defined?
3. Does it operate independently of the failed AI component?
4. Does it avoid calling the failed AI model again?
5. Does it use valid and sufficiently fresh sensor data?
6. Does it validate its own output?
7. Does it transition the hardware into the required operating state?
8. Does it have defined entry and exit conditions?
9. Can it recover without oscillating between AI and fallback?
10. Are failure and recovery events observable?

A fallback that simply reuses the last AI command must be evaluated for freshness and validity.

### Stage 6: Interactive Safe-State Clarification

When the intended non-AI behavior is missing or ambiguous:

1. Report the missing requirement.
2. Identify the affected hardware interface.
3. Explain why the agent cannot safely choose the physical behavior.
4. Ask the developer for the required operating behavior.
5. Request relevant operating constraints when necessary.
6. Wait for the answer before generating hardware-specific implementation code.

Possible clarification topics include:

- Required behavior after inference timeout.
- Behavior after sensor failure.
- Whether a classical controller exists.
- Whether the previous valid setpoint may be retained.
- Maximum permitted transition time.
- Conditions required before returning to AI mode.
- Independent hardware interlocks.

Do not present example actions as recommendations for a real device unless they are supported by its safety requirements.

If the user cannot define the behavior, provide an abstract implementation interface and list the engineering decisions that remain unresolved.

### Stage 7: Hardware Command Validation

Trace every AI-derived value before it reaches a hardware driver.

Inspect:

1. Physical minimum and maximum values.
2. Numeric type and unit validation.
3. NaN and Inf rejection.
4. Slew-rate limits.
5. Command freshness.
6. Plausibility constraints.
7. State-dependent operating limits.
8. Independent interlocks.
9. Invalid command handling.
10. Driver-level validation.

Verify that range validation happens before hardware writes.

Do not treat numeric clamping alone as proof of safety.

The permitted range must be grounded in actual device requirements.

### Stage 8: Sensor and Buffer Safety

Inspect sensor data before it enters model preprocessing or inference.

Check:

- Array bounds.
- Buffer lengths.
- Integer overflow in size calculations.
- Tensor dimensions.
- Data type conversions.
- NaN and Inf.
- Invalid timestamps.
- Stale sensor readings.
- Out-of-range values.
- Malformed packets.
- Concurrent buffer access.
- DMA and shared-buffer ownership.

Trace validation through the complete preprocessing pipeline.

### Stage 9: Model Runtime Integrity

Inspect model initialization and runtime configuration.

Check:

- Model loading errors.
- Input/output tensor compatibility.
- Memory requirements.
- Model version identification.
- Model availability.
- Integrity checks where relevant.
- Safe behavior after model initialization failure.
- Resource cleanup during model replacement.

If model files are loaded from external storage or OTA updates, inspect signature verification and integrity validation.

Do not claim cryptographic integrity merely because a checksum exists.

A checksum detects accidental corruption only when its expected value is independently trusted. Authenticity requires an appropriate trusted signature-verification mechanism.

### Stage 10: Failure Testing and Verification

Inspect existing tests for:

- AI timeout.
- Worker termination.
- Allocation failure.
- Invalid model output.
- Sensor corruption.
- Stale inference results.
- Fallback activation.
- Fallback recovery.
- Watchdog events.
- Repeated failures.
- Hardware output bounds.

Determine whether tests verify the actual behavior rather than merely checking that a function was called.

Where tests are missing, propose:

1. Unit tests.
2. Fault injection tests.
3. Integration tests.
4. Simulation tests.
5. Hardware-in-the-loop tests, where appropriate.

The default audit does not execute firmware, flash devices, or issue physical hardware commands.

Test execution requires explicit authorization and an appropriate isolated environment.

## 6. Finding Classification

Use these severity levels:

### Critical

A confirmed, direct path can produce a potentially severe physical or system failure, with no effective protection identified in the inspected scope.

### High

A significant runtime or safety control is missing, incomplete, or bypassable, with a credible failure scenario.

### Medium

A weakness could reduce reliability, availability, or recovery capability under specific conditions.

### Low

A limited weakness or defense-in-depth improvement.

### Informational

An observation, documentation gap, or improvement opportunity without an established defect.

Never assign severity solely because a particular keyword or function is absent.

Also report confidence:

- High: direct code evidence and relevant control flow are visible.
- Medium: strong evidence exists, but some dependencies are unavailable.
- Low: incomplete visibility or assumptions materially affect the conclusion.

Do not confuse confidence with severity.

## 7. Control Assessment

For every audit category, assign one status:

- PASS
- PARTIAL
- FAIL
- NOT VERIFIED
- NOT APPLICABLE

Use NOT VERIFIED when evidence is insufficient.

Use NOT APPLICABLE only when the category genuinely does not apply to the inspected architecture.

A PASS applies only to the inspected scope and available evidence.

## 8. Remediation Proposal

For every actionable finding, provide:

1. Original problematic implementation.
2. Explanation of the failure.
3. Proposed implementation.
4. Required configuration or assumptions.
5. Regression test.
6. Remaining limitations.

Proposed code must:

- Match the project's language and conventions.
- Reuse existing interfaces where possible.
- Avoid inventing hardware APIs.
- Clearly mark platform-specific placeholders.
- Avoid introducing unbounded allocations or blocking operations into critical paths.
- Preserve independent safety validation.
- Avoid silently changing the intended physical behavior.

If the required safe state is unknown, provide an abstract template rather than selecting an arbitrary physical action.

### Patch Approval

The agent must present proposed changes separately from the audit.

Do not apply changes unless the user explicitly approves the specific modification.

Approval of one patch does not authorize unrelated changes.

## 9. Audit Report Format

Generate a structured Markdown report.

# Embedded AI Runtime & Safety Audit

## 1. Executive Summary

- Target platform.
- AI runtime.
- Programming languages.
- Operating system.
- Inspected scope.
- Overall assessment.
- Findings by severity.

## 2. Architecture Overview

- Sensor input pipeline.
- Model execution.
- Control logic.
- Hardware output.
- Fallback and recovery paths.

## 3. Security and Runtime Findings

For each finding:

- ID.
- Title.
- Severity.
- Confidence.
- File and line.
- Evidence.
- Failure scenario.
- Runtime or physical impact.
- Recommended remediation.

## 4. Memory and Resource Assessment

- Allocation behavior.
- Memory limits.
- Stack and heap risks.
- Resource lifecycle.
- Unverified requirements.

## 5. Real-Time and Watchdog Assessment

- Deadline configuration.
- Blocking operations.
- Scheduling risks.
- Watchdog independence.
- Recovery behavior.

## 6. Non-AI Fallback Assessment

- Fallback coverage.
- Failure conditions.
- Fallback implementation quality.
- State transition analysis.
- Missing requirements.
- Clarifying questions.

## 7. Hardware and Sensor Validation

- Actuator limits.
- Rate limiting.
- Invalid values.
- Sensor buffer validation.
- Hardware interlocks.

## 8. Model Runtime Assessment

- Initialization.
- Memory configuration.
- Output validation.
- Model integrity.
- Recovery from model failure.

## 9. Test Coverage

- Existing tests.
- Missing scenarios.
- Proposed tests.
- Runtime and hardware verification requirements.

## 10. Control Assessment Matrix

Use:

| Control | Status | Evidence | Confidence |
|---|---|---|---|
| Memory bounds | | | |
| Resource lifecycle | | | |
| Real-time deadlines | | | |
| Non-blocking inference | | | |
| Watchdog independence | | | |
| Non-AI fallback | | | |
| State transitions | | | |
| Actuator validation | | | |
| Sensor validation | | | |
| Model integrity | | | |
| Failure tests | | | |

## 11. Proposed Remediation

List code proposals and tests separately.

Do not apply patches automatically.

## 12. Limitations

List uninspected files, missing documentation, unavailable hardware abstractions, and properties that require runtime verification.

## 10. References

Consult:

`references/examples.md`

Use it for vulnerable patterns, corrected implementations, testing strategies, and fallback templates.

## 11. Completion Criteria

The audit is complete when:

- The AI-to-hardware pipeline has been mapped to the extent possible.
- Relevant memory and resource risks have been assessed.
- Real-time execution risks have been reviewed.
- Watchdog and recovery behavior have been examined.
- AI failure paths have been traced.
- Non-AI fallback completeness has been assessed.
- Hardware commands and sensor inputs have been reviewed.
- Existing tests have been evaluated.
- Missing requirements have been identified.
- Findings contain evidence and confidence ratings.
- Proposed changes are clearly separated from applied changes.
- Remaining verification limitations are documented.
