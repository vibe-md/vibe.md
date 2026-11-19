# Non-AI Fallback Engineering

This reference defines how to assess fallback completeness and how to propose remediation without inventing physical behavior.

## 1. What Counts as a Fallback

A fallback is an explicit, reachable, bounded, non-AI behavior used when AI cannot provide a valid result within the system's requirements.

A timeout, `try/catch`, log statement, `safe_mode` function name, `TODO`, empty handler, silent return, or endless retry is not by itself a complete fallback.

## 2. Required Failure Coverage

Trace each applicable case:

- Inference timeout/deadline miss.
- Inference exception, crash, or worker termination.
- Model load/init failure or model unavailable.
- Invalid schema, NaN/Inf, out-of-range, or low-confidence output.
- Stale or duplicated inference result.
- Sensor failure, stale data, or malformed input.
- Remote API/network loss.
- Resource exhaustion/allocation failure.
- Repeated failure and watchdog reset/reboot.

A system may intentionally group several failures, but verify that the grouped path handles each one correctly.

## 3. Completeness Checklist

For each failure branch, determine:

1. Is the failure detected?
2. Is detection bounded by a documented deadline?
3. Is the fallback reachable from the failure branch?
4. Is the required physical behavior defined by project requirements?
5. Does fallback avoid the failed AI model, worker, network, or unavailable resource?
6. Are its inputs valid and fresh enough?
7. Are fallback outputs independently validated?
8. Are hardware interlocks still active?
9. Are entry, exit, retry, and recovery conditions defined?
10. Can the system oscillate between AI and fallback?
11. Are state transitions observable without blocking critical work?
12. Are failure and recovery tests present?

## 4. Safe-State Clarification

If the required physical behavior is missing or ambiguous:

- Identify the affected actuator/process and the failure condition.
- Explain why the auditing agent cannot select a safe state.
- Ask the developer for the required behavior and relevant constraints.
- Ask only for information needed to propose a correct implementation.

Potential design choices (for discussion only) include controlled stop, hold-last-valid-setpoint with an explicit freshness bound, manual control, a classical controller, or a device-specific safe state. None is universally safe.

Do not write hardware-specific fallback code until the required behavior and necessary interfaces are known. If the developer cannot yet define them, provide an abstract interface and a list of unresolved engineering decisions.

## 5. Proposed Remediation Contract

A proposed fallback implementation should identify:

- Trigger conditions and deadline source.
- State machine and transition rules.
- Non-AI controller or action, as specified by the developer.
- Sensor validity/freshness requirements.
- Independent output validation and interlocks.
- Bounded retry and recovery policy.
- Telemetry/diagnostic behavior.
- Test seams for deterministic fault injection.

Do not silently change the intended physical behavior. Do not assume that holding the last command, stopping a motor, hovering, opening/closing a valve, or switching to PID is safe.

## 6. Example State Model

The following is an abstract state model, not a device-specific safety design:

```text
AI_ACTIVE
  | valid, fresh result within deadline
  v
VALIDATE_AND_APPLY
  | invalid result / timeout / worker failure
  v
NON_AI_FALLBACK
  | recovery prerequisites satisfied
  v
RECOVERY_CHECK
  | explicit re-entry policy satisfied
  v
AI_ACTIVE
```

The actual fallback action, transition deadline, recovery prerequisites, and actuator state must be defined by the device requirements.

## 7. Finding Guidance

- `FAIL`: inspected code demonstrates that a required failure path has no effective fallback, or that the fallback is bypassable/ineffective.
- `PARTIAL`: a fallback exists but lacks material validation, independence, bounded transitions, or tests.
- `NOT VERIFIED`: the relevant behavior may exist in an uninspected HAL, external controller, or hardware interlock.
- `NOT APPLICABLE`: the architecture has no corresponding AI-dependent physical/control path.

Do not label an empty-looking wrapper as a confirmed physical hazard if the actual behavior is delegated to an unavailable component. State the evidence boundary.
