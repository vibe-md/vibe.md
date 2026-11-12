# Embedded & Real-Time AI Safety
## Engineering Patterns, Failure Analysis, Remediation and Verification

This reference supports the `embedded-ai-runtime-guard` skill.

It contains illustrative C/C++, Rust, and Python patterns for auditing AI-enabled embedded systems.

All hardware-specific values, control algorithms, and fallback behaviors must be derived from the target system's requirements and hazard analysis.

Examples are engineering templates, not certified safety implementations.

---

# 1. Core Architecture and Trust Boundaries

An AI-enabled embedded application commonly contains the following pipeline:

```text
Physical Sensors
       |
       v
Input Validation
       |
       v
Preprocessing
       |
       v
AI Inference Worker
       |
       v
Output Validation
       |
       v
Deterministic Control Layer
       |
       v
Hardware Safety Interlocks
       |
       v
Physical Actuators
```

A separate recovery path must exist:

```text
AI Failure / Timeout / Invalid Output
                  |
                  v
          Failure Detection
                  |
                  v
         Fallback State Machine
                  |
                  v
       Project-Defined Non-AI Mode
                  |
                  v
         Independent Validation
                  |
                  v
              Hardware
```

The AI worker must not be the only component capable of maintaining system safety.

## 1.1 Important Trust Boundaries

| Component | Potential Risk | Expected Control |
|---|---|---|
| Sensor buffers | Invalid dimensions and corrupted data | Bounds and format validation |
| AI model | Invalid or unpredictable output | Independent output validation |
| Inference worker | Timeout or process failure | Isolation and deadline monitoring |
| Heap and tensor memory | Resource exhaustion | Explicit capacity limits |
| RTOS scheduler | Blocking and priority inversion | Scheduling and synchronization analysis |
| Fallback controller | Incomplete recovery | Explicit state machine |
| Hardware driver | Invalid actuator commands | Independent hardware validation |
| Model files | Unauthorized or corrupted model | Trusted integrity verification |

---

# 2. Memory and Resource Management

## 2.1 Dynamic Allocation Inside an Inference Loop

### Vulnerable C++ Example

```cpp
#include <vector>

void inference_loop(const float* sensor_data, size_t length) {
    while (true) {
        std::vector<float> input(sensor_data, sensor_data + length);

        auto* output = new float[1024];

        run_ai_inference(input.data(), input.size(), output);

        apply_ai_output(output);

        delete[] output;
    }
}
```

### Why This Is Risky

- Repeated allocations can introduce unpredictable latency.
- Heap fragmentation can reduce future allocation capacity.
- Allocation failure may occur after prolonged uptime.
- The implementation does not establish a bounded resource budget.
- An allocation failure may interrupt a critical control operation.

Dynamic allocation is not automatically a vulnerability. Its suitability depends on the platform, allocator, timing requirements, and resource constraints.

### Improved Bounded Buffer Pattern

```cpp
#include <array>
#include <cstddef>

constexpr std::size_t INPUT_CAPACITY = PROJECT_INPUT_CAPACITY;
constexpr std::size_t OUTPUT_CAPACITY = PROJECT_OUTPUT_CAPACITY;

struct InferenceBuffers {
    std::array<float, INPUT_CAPACITY> input{};
    std::array<float, OUTPUT_CAPACITY> output{};
};

bool prepare_input(
    InferenceBuffers& buffers,
    const float* source,
    std::size_t length
) {
    if (source == nullptr || length > INPUT_CAPACITY) {
        return false;
    }

    for (std::size_t i = 0; i < length; ++i) {
        buffers.input[i] = source[i];
    }

    return true;
}
```

`PROJECT_INPUT_CAPACITY` and `PROJECT_OUTPUT_CAPACITY` must be replaced with validated platform-specific values.

### Audit Checks

- Is the buffer capacity established?
- Can the input exceed the capacity?
- Is the buffer shared between concurrent tasks?
- Is ownership defined?
- Is the memory located in an appropriate memory region?
- Does the application handle capacity failure?
- Is the buffer size included in the RAM budget?

## 2.2 Tensor Arena Capacity

For TensorFlow Lite Micro-style environments, inspect:

- Tensor arena allocation.
- Model tensor requirements.
- Scratch buffer requirements.
- Alignment.
- Model initialization failures.
- Maximum supported input dimensions.

A declared arena size does not prove that the arena is large enough.

Look for actual initialization errors and documented memory requirements.

## 2.3 Resource Lifecycle

Inspect:

- Model initialization and destruction.
- Camera frame ownership.
- DMA buffers.
- File descriptors.
- Network connections.
- Tensor allocations.
- Worker lifecycle.

Every acquired resource should have a defined release path, including error and timeout paths.

---

# 3. Real-Time Execution

## 3.1 Blocking Inference in a Control Loop

### Vulnerable Example

```cpp
void control_task() {
    while (true) {
        auto result = ai_model.predict(read_sensors());

        write_actuator(result);

        sleep_ms(10);
    }
}
```

### Why This Is Risky

If inference takes longer than the control task's execution budget:

- The control loop may miss its deadline.
- Other tasks may be delayed.
- Watchdog servicing may be affected.
- Stale sensor information may be used.
- System responsiveness may deteriorate.

A remote API call can have highly variable latency and should not be placed in a time-critical control path.

## 3.2 Decoupled AI Worker

A better architecture separates inference from deterministic control.

```text
                +-------------------+
                |   Sensor Task     |
                +---------+---------+
                          |
                          v
                +-------------------+
                |  Input Snapshot   |
                +---------+---------+
                          |
                          v
                +-------------------+
                |   AI Worker       |
                |  Non-Critical     |
                +---------+---------+
                          |
                          v
                +-------------------+
                | Validated Output  |
                | Timestamp + State |
                +---------+---------+
                          |
                          v
                +-------------------+
                | Control Task      |
                | Deadline-Bounded  |
                +---------+---------+
                          |
                          v
                +-------------------+
                | Hardware Driver   |
                +-------------------+
```

The control task should consume only a validated, sufficiently fresh AI result.

If no valid result is available, it must follow the project-defined fallback state machine.

## 3.3 ISR Safety

AI inference, memory allocation, blocking mutex operations, network access, and long-running computations generally do not belong inside an interrupt service routine.

Inspect whether ISR callbacks:

- Copy bounded data.
- Use permitted ISR-safe synchronization.
- Avoid blocking.
- Avoid dynamic allocation.
- Defer processing to an appropriate task.

Platform-specific RTOS rules must be checked before proposing changes.

---

# 4. Non-AI Fallback Analysis

## 4.1 Missing Fallback

### Vulnerable Example

```cpp
void handle_ai_failure() {
    // TODO: implement safe behavior
}
```

This function does not establish a recovery behavior.

A function declaration or call is not evidence of a complete fallback.

### Required Audit

Trace:

1. Where AI failure is detected.
2. Whether the handler is reached.
3. What state is entered.
4. What happens to the actuator command.
5. Whether the fallback operates independently of AI.
6. Whether recovery is defined.

## 4.2 Empty Exception Handler

### Vulnerable Python Example

```python
def control_device(model, sensor_data):
    try:
        output = model.predict(sensor_data)
        hardware.write(output)
    except Exception:
        pass
```

Problems:

- Failure is silently ignored.
- The previous hardware command may remain active.
- There is no defined fallback.
- The system does not expose its failure state.
- Invalid model output is not independently checked.

## 4.3 Infinite AI Retry

### Vulnerable Example

```python
while True:
    try:
        result = model.predict(data)
        break
    except Exception:
        continue
```

An unavailable model can prevent the application from ever entering its recovery path.

### Improved Retry Policy

Retries must be:

- Bounded.
- Deadline-aware.
- Limited by an explicit policy.
- Followed by a defined fallback when exhausted.

Retries must never delay a time-critical recovery action.

## 4.4 Fallback State Machine

A useful architecture separates AI availability from physical operating state.

```text
           +----------------+
           |   AI_ACTIVE    |
           +-------+--------+
                   |
          Invalid / stale output
                   |
                   v
           +----------------+
           | FAILURE_DETECTED|
           +-------+--------+
                   |
                   v
           +----------------+
           | FALLBACK_ENTRY |
           +-------+--------+
                   |
                   v
           +----------------+
           | NON_AI_ACTIVE  |
           +-------+--------+
                   |
          Recovery conditions
          explicitly satisfied
                   |
                   v
           +----------------+
           | RECOVERY_CHECK |
           +-------+--------+
                   |
             Validation
                   |
                   v
           +----------------+
           |   AI_ACTIVE    |
           +----------------+
```

This is an architectural example, not a universal physical state-transition policy.

A real implementation must also define:

- Transition guards.
- Failure latching.
- Retry limits.
- Recovery hysteresis.
- Sensor validity.
- AI warm-up requirements.
- Re-entry conditions.
- Maximum transition time.
- Behavior if fallback itself fails.

## 4.5 User-Defined Safe-State Requirement

When the physical behavior is undefined, the agent must ask the developer.

Example:

> The AI failure path is present, but the required non-AI operating behavior has not been specified.
>
> Which system requirement defines the intended behavior after inference becomes unavailable?
>
> Please provide the applicable safety requirement or describe the required operating state.

Do not choose a physical action merely because it appears conventional.

---

# 5. C++ Fallback and Output Validation Template

The following example illustrates separation between AI output acquisition, validation, control logic, and hardware interfaces.

It intentionally leaves the physical fallback implementation project-defined.

```cpp
#include <cmath>
#include <cstdint>
#include <algorithm>

struct AiResult {
    float value;
    float confidence;
    uint32_t timestamp_ms;
    bool valid;
};

struct ControlLimits {
    float minimum;
    float maximum;
};

bool is_fresh(
    uint32_t now_ms,
    uint32_t timestamp_ms,
    uint32_t max_age_ms
) {
    // Unsigned subtraction supports normal timer wraparound,
    // provided the configured interval is within the timer's
    // supported comparison range.
    return static_cast<uint32_t>(now_ms - timestamp_ms) <= max_age_ms;
}

bool validate_ai_result(
    const AiResult& result,
    uint32_t now_ms,
    uint32_t max_age_ms,
    float minimum_confidence
) {
    return result.valid &&
           std::isfinite(result.value) &&
           std::isfinite(result.confidence) &&
           result.confidence >= minimum_confidence &&
           result.confidence <= 1.0f &&
           is_fresh(now_ms, result.timestamp_ms, max_age_ms);
}

float clamp_command(
    float value,
    const ControlLimits& limits
) {
    return std::clamp(
        value,
        limits.minimum,
        limits.maximum
    );
}

// These interfaces must be implemented and reviewed
// against the actual target hardware and safety requirements.

bool read_latest_ai_result_nonblocking(AiResult& result);

bool read_validated_sensor_snapshot(float& value);

bool compute_project_defined_fallback(
    float sensor_value,
    float& command
);

bool validate_project_command(float command);

void apply_hardware_command(float command);

void report_fallback_state();

void control_step(
    uint32_t now_ms,
    const ControlLimits& limits
) {
    constexpr uint32_t MAX_AI_AGE_MS =
        PROJECT_MAX_AI_AGE_MS;

    constexpr float MIN_CONFIDENCE =
        PROJECT_MIN_CONFIDENCE;

    AiResult result{};

    bool available =
        read_latest_ai_result_nonblocking(result);

    bool ai_valid =
        available &&
        validate_ai_result(
            result,
            now_ms,
            MAX_AI_AGE_MS,
            MIN_CONFIDENCE
        );

    float command = 0.0f;

    if (ai_valid) {
        command = clamp_command(result.value, limits);
    } else {
        float sensor_value = 0.0f;

        if (!read_validated_sensor_snapshot(sensor_value)) {
            report_fallback_state();
            // A separate, project-defined fault state
            // is required here. Do not invent an output.
            return;
        }

        if (!compute_project_defined_fallback(
                sensor_value,
                command
            )) {
            report_fallback_state();
            // Escalate to the independently specified
            // hardware/system fault-handling path.
            return;
        }

        report_fallback_state();
    }

    if (!std::isfinite(command) ||
        !validate_project_command(command)) {
        report_fallback_state();
        return;
    }

    apply_hardware_command(command);
}
```

### Important Limitations

This example does not implement:

- A complete hardware safety interlock.
- A complete fallback controller.
- A real RTOS scheduling policy.
- A watchdog.
- A complete actuator slew-rate limiter.
- A thread-safe AI result exchange implementation.

Those must be designed against the target platform.

A clamp does not replace a state-dependent safety check.

---

# 6. Python Edge AI: Isolated Inference Timeout

## 6.1 Why a Thread Timeout Is Not Sufficient

A common pattern is:

```python
future.result(timeout=0.2)
```

This limits how long the caller waits for a result.

It does not guarantee that the underlying computation stops.

Calling `Future.cancel()` also does not reliably terminate an already running thread.

Additionally, exiting a ThreadPoolExecutor context manager can wait for running workers.

For potentially unbounded native inference, a process boundary may provide stronger isolation.

## 6.2 Process-Isolated Inference Example

The following is an illustrative architecture.

The inference process must not control physical hardware directly.

The parent process owns the hardware interface and validates all returned values.

```python
import math
import multiprocessing as mp


def inference_worker(connection, model_factory, input_data):
    try:
        model = model_factory()
        result = model.predict(input_data)

        connection.send(("ok", result))

    except Exception as exc:
        connection.send(("error", str(exc)))

    finally:
        connection.close()


def terminate_worker(process, grace_seconds=0.1):
    if process.is_alive():
        process.terminate()
        process.join(timeout=grace_seconds)

    if process.is_alive() and hasattr(process, "kill"):
        process.kill()
        process.join(timeout=grace_seconds)


def isolated_inference(
    model_factory,
    input_data,
    timeout_seconds
):
    context = mp.get_context("spawn")

    receiver, sender = context.Pipe(duplex=False)

    worker = context.Process(
        target=inference_worker,
        args=(sender, model_factory, input_data)
    )

    try:
        worker.start()
        sender.close()

        if not receiver.poll(timeout_seconds):
            return "TIMEOUT", None

        try:
            status, result = receiver.recv()
        except EOFError:
            return "WORKER_FAILURE", None

        worker.join(timeout=0.1)

        if worker.is_alive():
            terminate_worker(worker)

        if status != "ok":
            return "INFERENCE_ERROR", None

        return "SUCCESS", result

    finally:
        receiver.close()

        if worker.is_alive():
            terminate_worker(worker)

        worker.close()


def validate_model_output(value):
    if isinstance(value, bool):
        return False

    if not isinstance(value, (int, float)):
        return False

    return math.isfinite(value)
```

### Important Engineering Constraints

- `model_factory` must be compatible with the selected multiprocessing start method.
- Model initialization may itself consume significant memory.
- Process creation overhead must be included in the timing budget.
- Repeated worker creation can create resource pressure.
- A persistent supervised worker may be more suitable for some systems.
- Terminating a process does not undo external side effects.
- A native library or hardware driver may require separate recovery.
- Hardware access must remain outside the inference worker.

The actual fallback must execute in an independent, supervised control path.

This example demonstrates isolation, not certified real-time execution.

---

# 7. Actuator Output Protection

## 7.1 Invalid AI Output

An AI model may return:

- NaN.
- Infinity.
- A value outside the physical operating range.
- An unexpected data type.
- An outdated command.
- A command inconsistent with the current operating state.

## 7.2 Validation Template

```python
import math


def validate_actuator_command(
    value,
    minimum,
    maximum
):
    if isinstance(value, bool):
        return False

    if not isinstance(value, (int, float)):
        return False

    if not math.isfinite(value):
        return False

    if value < minimum or value > maximum:
        return False

    return True
```

This validates a numerical range only.

A complete actuator safety layer may also require:

- Slew-rate limits.
- State-dependent restrictions.
- Interlocks.
- Command freshness.
- Plausibility checks.
- Independent driver validation.

Never derive physical limits from AI output.

---

# 8. Sensor and Buffer Validation

## 8.1 Vulnerable Buffer Handling

```cpp
void process_sensor_data(
    const float* input,
    size_t length
) {
    float tensor[64];

    for (size_t i = 0; i < length; ++i) {
        tensor[i] = input[i];
    }

    run_inference(tensor, length);
}
```

The implementation does not verify:

- Whether input is null.
- Whether length exceeds capacity.
- Whether values are finite.
- Whether tensor dimensions match the model.

## 8.2 Improved Validation

```cpp
#include <cmath>
#include <cstddef>

bool copy_sensor_data(
    const float* input,
    size_t length,
    float* output,
    size_t capacity
) {
    if (input == nullptr || output == nullptr) {
        return false;
    }

    if (length == 0 || length > capacity) {
        return false;
    }

    for (size_t i = 0; i < length; ++i) {
        if (!std::isfinite(input[i])) {
            return false;
        }

        output[i] = input[i];
    }

    return true;
}
```

Also inspect whether the buffer can change concurrently during copying.

For DMA and shared memory, ownership and synchronization must be explicit.

---

# 9. Watchdog and Recovery

## 9.1 Incorrect Watchdog Pattern

```cpp
while (true) {
    watchdog_feed();

    run_ai_inference();

    update_control();
}
```

If the AI operation blocks indefinitely, the watchdog may not be serviced again.

## 9.2 Another Dangerous Pattern

```cpp
void watchdog_task() {
    while (true) {
        watchdog_feed();
        sleep_ms(100);
    }
}
```

A watchdog task that feeds independently without checking system health may conceal a stalled control task.

## 9.3 Improved Architectural Principle

A watchdog supervisor should evaluate meaningful health conditions.

Possible monitored conditions include:

- Control-loop progress.
- Deadline violations.
- Task health.
- Resource exhaustion.
- Communication health.
- Fallback state.
- Recovery progress.

The exact watchdog design must follow the MCU and RTOS requirements.

Do not feed a watchdog solely because a timer expired.

---

# 10. Failure Injection and Regression Tests

## 10.1 Python Output Validation Tests

```python
import math
import pytest


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        None,
        "invalid",
        True,
    ],
)
def test_invalid_actuator_values_are_rejected(value):
    assert not validate_actuator_command(
        value,
        minimum=0.0,
        maximum=100.0
    )


def test_out_of_range_command_is_rejected():
    assert not validate_actuator_command(
        150.0,
        minimum=0.0,
        maximum=100.0
    )


def test_valid_command_is_accepted():
    assert validate_actuator_command(
        50.0,
        minimum=0.0,
        maximum=100.0
    )
```

The numerical limits in these tests are illustrative test values, not hardware recommendations.

## 10.2 Fallback State Tests

A fallback state machine should be tested independently of physical hardware.

Example test scenarios:

| Scenario | Expected Verification |
|---|---|
| AI timeout | Fallback entry is requested |
| Invalid model output | AI output is rejected |
| Stale model output | Old output is not applied |
| Model initialization failure | AI is not treated as available |
| Sensor failure | Sensor-fault path is entered |
| Repeated AI failures | Retry policy remains bounded |
| Recovery attempt | Re-entry conditions are checked |
| Fallback failure | Independent fault path is invoked |

## 10.3 Test Design Requirements

A good test should verify:

1. The failure condition is actually induced.
2. The correct state transition occurs.
3. Invalid output does not reach the hardware interface.
4. The fallback does not call the failed AI worker.
5. The result is bounded by the relevant requirements.
6. Recovery does not occur prematurely.
7. Failure events are observable.

Prefer dependency injection and mocked hardware interfaces.

Do not use a live actuator as a unit-test target.

---

# 11. Audit Finding Examples

## Finding EMB-001: Unbounded Inference Memory Allocation

Severity: High candidate.

Evidence:

Repeated dynamic allocation occurs inside a high-frequency inference path.

Risk:

Unpredictable allocation latency, fragmentation, and allocation failure.

Recommendation:

Establish bounded memory requirements and move allocations into an appropriate initialization phase where possible.

## Finding EMB-002: Missing AI Failure Recovery

Severity: Depends on system criticality.

Evidence:

The inference error handler contains no defined recovery behavior.

Risk:

The system may continue using an outdated command or enter an undefined operating state.

Recommendation:

Define the required non-AI behavior from system safety requirements, then implement and test the transition.

## Finding EMB-003: Blocking Inference

Severity: Depends on deadline and scheduling impact.

Evidence:

A synchronous inference call is executed within a time-critical task.

Risk:

Deadline misses and loss of control-loop responsiveness.

Recommendation:

Decouple inference and introduce bounded result acquisition.

## Finding EMB-004: Unvalidated Hardware Command

Severity: Depends on actuator and operating conditions.

Evidence:

Model output is passed directly to a hardware interface.

Risk:

Invalid commands may exceed permitted physical operating constraints.

Recommendation:

Introduce independent validation before hardware access.

## Finding EMB-005: Watchdog Not Independent

Severity: Depends on recovery architecture.

Evidence:

Watchdog servicing is coupled to the AI inference task.

Risk:

A model stall may prevent the system from recovering as intended.

Recommendation:

Review watchdog ownership and implement meaningful system-health supervision.

---

# 12. Final Engineering Review Checklist

Before concluding an audit, verify that the following have been assessed:

- [ ] AI execution architecture mapped.
- [ ] Memory capacity and allocation behavior reviewed.
- [ ] Resource ownership and cleanup reviewed.
- [ ] Stack and heap risks reviewed.
- [ ] Real-time deadlines identified.
- [ ] Blocking operations identified.
- [ ] ISR constraints reviewed.
- [ ] Watchdog independence assessed.
- [ ] AI timeout handling traced.
- [ ] Every relevant AI failure path traced.
- [ ] Fallback implementation inspected.
- [ ] Safe-state requirements identified.
- [ ] Recovery and re-entry conditions reviewed.
- [ ] Hardware commands independently validated.
- [ ] Sensor buffers and tensor dimensions validated.
- [ ] Model initialization and integrity reviewed.
- [ ] Failure tests assessed.
- [ ] Remaining unknowns documented.
- [ ] Proposed patches separated from applied changes.

A successful static audit does not certify physical safety.

Runtime measurements, simulation, hardware-in-the-loop testing, and system-level safety validation may still be required.
