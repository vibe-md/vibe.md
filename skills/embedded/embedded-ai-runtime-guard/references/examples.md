# Embedded AI Runtime Guard Examples

These examples are illustrative patterns, not certified safety implementations. Adapt them to the actual hardware, RTOS, driver APIs, timing budgets, and hazard analysis. Never copy a physical safe-state action without confirming the device requirements.

## 1. C++: Avoid Per-Iteration Heap Allocation

### Risk pattern

```cpp
void inference_step(const float* input, std::size_t count) {
    std::vector<float> tensor(input, input + count); // May allocate/grow each call.
    auto* buffer = new float[count];                 // Repeated heap allocation.
    run_model(tensor.data(), buffer);
    apply_output(buffer[0]);
    delete[] buffer;
}
```

This pattern may create allocator pressure and fragmentation in a frequently executed path. It is not proof of a leak by itself; assess allocation frequency, allocator behavior, bounds, and execution context.

### Bounded-buffer pattern

```cpp
#include <array>
#include <cstddef>

constexpr std::size_t kInputCapacity = 128;

struct InferenceInput {
    std::array<float, kInputCapacity> values{};
    std::size_t size{0};
};

bool copy_input(const float* source,
                std::size_t source_size,
                InferenceInput& destination) {
    if (source == nullptr || source_size == 0 ||
        source_size > destination.values.size()) {
        return false;
    }

    for (std::size_t i = 0; i < source_size; ++i) {
        destination.values[i] = source[i];
    }
    destination.size = source_size;
    return true;
}
```

This bounds this input buffer. It does not establish that the model runtime, stack, or all other allocations are bounded.

## 2. C++: Validate Model Output Before Hardware Boundary

`std::clamp` requires C++17. The permitted limits below are placeholders and must come from device requirements.

```cpp
#include <algorithm>
#include <cmath>

struct OutputLimits {
    float minimum;
    float maximum;
};

bool validate_output(float model_value,
                     const OutputLimits& limits,
                     float& accepted_value) {
    if (!std::isfinite(model_value) ||
        !std::isfinite(limits.minimum) ||
        !std::isfinite(limits.maximum) ||
        limits.minimum > limits.maximum) {
        return false;
    }

    accepted_value = std::clamp(
        model_value, limits.minimum, limits.maximum);
    return true;
}
```

A real system may also require rate limits, state-dependent constraints, freshness checks, interlocks, and validation inside the driver. Clamping alone is not a safety case.

## 3. C++: Abstract Fallback Boundary

Do not choose the physical action inside a generic audit template. Require the project to supply a device-specific controller.

```cpp
enum class ControlMode {
    Ai,
    NonAiFallback,
    Fault
};

class NonAiController {
public:
    virtual ~NonAiController() = default;

    // Implement only after the device's required behavior is specified.
    virtual bool enter_fallback() = 0;
    virtual bool update_from_validated_inputs() = 0;
};

bool handle_ai_failure(NonAiController& fallback,
                       ControlMode& mode) {
    mode = ControlMode::NonAiFallback;

    if (!fallback.enter_fallback()) {
        mode = ControlMode::Fault;
        return false;
    }

    return true;
}
```

The implementation of `enter_fallback()` and `update_from_validated_inputs()` must be based on approved device requirements. This interface does not itself make a device safe.

## 4. C++: Unit-Test the Transition with a Fake

```cpp
#include <cassert>

class FakeFallback final : public NonAiController {
public:
    bool entered{false};
    bool enter_ok{true};

    bool enter_fallback() override {
        entered = true;
        return enter_ok;
    }

    bool update_from_validated_inputs() override {
        return true;
    }
};

void test_ai_failure_enters_fallback() {
    FakeFallback fallback;
    ControlMode mode = ControlMode::Ai;

    const bool ok = handle_ai_failure(fallback, mode);

    assert(ok);
    assert(fallback.entered);
    assert(mode == ControlMode::NonAiFallback);
}

void test_failed_fallback_reports_fault() {
    FakeFallback fallback;
    fallback.enter_ok = false;
    ControlMode mode = ControlMode::Ai;

    const bool ok = handle_ai_failure(fallback, mode);

    assert(!ok);
    assert(fallback.entered);
    assert(mode == ControlMode::Fault);
}
```

These are logic-level examples. A project test should use its actual state machine, inject the AI failure at the relevant boundary, and assert the required outputs using mocked hardware interfaces.

## 5. Python: Validate Sensor and Model Values

```python
import math
from collections.abc import Sequence


def validate_sensor_values(values: Sequence[float],
                           expected_count: int) -> list[float]:
    if len(values) != expected_count:
        raise ValueError("unexpected sensor sample count")

    validated: list[float] = []
    for value in values:
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError("sensor value must be finite")
        validated.append(numeric)

    return validated


def validate_model_command(value: float,
                           minimum: float,
                           maximum: float) -> float:
    if not all(math.isfinite(v) for v in (value, minimum, maximum)):
        raise ValueError("command and limits must be finite")
    if minimum > maximum:
        raise ValueError("invalid configured command range")

    return min(max(value, minimum), maximum)
```

The expected sample count, units, and limits must come from the device interface contract. Add timestamp, freshness, plausibility, slew-rate, and interlock checks where required.

## 6. Python: Bounded Inference Worker Process Cleanup

This example shows process cleanup mechanics only. It does not guarantee that a process stuck in an uninterruptible kernel operation can be stopped within a hard real-time deadline. Use platform-specific supervision where required.

```python
from __future__ import annotations

import multiprocessing as mp
import time
from typing import Any


def stop_and_reap(process: mp.Process,
                  graceful_timeout: float,
                  forced_timeout: float) -> bool:
    if graceful_timeout < 0 or forced_timeout < 0:
        raise ValueError("timeouts must be non-negative")

    if not process.is_alive():
        process.join(timeout=0)
        return True

    process.join(timeout=graceful_timeout)

    if process.is_alive():
        process.terminate()
        process.join(timeout=forced_timeout)

    if process.is_alive():
        # kill() is available on supported modern Python versions.
        kill = getattr(process, "kill", None)
        if kill is not None:
            kill()
            process.join(timeout=forced_timeout)

    stopped = not process.is_alive()
    if stopped:
        process.join(timeout=0)  # Reap/collect exit status.

    return stopped


def run_inference_with_timeout(
    target: Any,
    args: tuple[Any, ...],
    timeout_seconds: float,
) -> tuple[bool, Any]:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    process = mp.Process(target=target, args=args)
    process.start()
    process.join(timeout=timeout_seconds)

    if process.is_alive():
        stopped = stop_and_reap(
            process,
            graceful_timeout=0.1,
            forced_timeout=0.5,
        )
        if not stopped:
            return False, "inference process could not be confirmed stopped"
        return False, "inference timed out"

    exit_code = process.exitcode
    if exit_code != 0:
        return False, f"inference process exited with code {exit_code}"

    return True, None
```

Production code must also define result transport, exception propagation, process-start method, child cleanup, IPC closure, and what happens if termination fails. The timeout values above are illustrative only and must not be treated as real-time guarantees.

## 7. Python: Test a Fallback State Transition

```python
from dataclasses import dataclass


@dataclass
class Controller:
    mode: str = "AI"
    fallback_entries: int = 0

    def enter_non_ai_fallback(self) -> None:
        # The actual physical behavior belongs in a device-specific,
        # requirements-backed implementation, not in this generic example.
        self.mode = "NON_AI_FALLBACK"
        self.fallback_entries += 1


def handle_inference_failure(controller: Controller) -> None:
    controller.enter_non_ai_fallback()


def test_inference_failure_enters_non_ai_mode() -> None:
    controller = Controller()

    handle_inference_failure(controller)

    assert controller.mode == "NON_AI_FALLBACK"
    assert controller.fallback_entries == 1
```

This test proves only that the abstract transition function is called. A meaningful project test must verify the required device-specific behavior and all relevant interlocks through fakes or simulation.

## 8. Audit Examples

### Example A: FreeRTOS drone vision task

**Request:** Review a C++ FreeRTOS obstacle-avoidance task for inference stalls, memory growth, and incomplete recovery.

**Expected audit approach:**

1. Trace sensor buffers, preprocessing, inference task, output validation, and motor command path.
2. Determine whether inference runs in a control task or ISR and compare its behavior with documented deadlines.
3. Inspect allocations and tensor arena bounds across repeated invocations.
4. Trace timeout and worker-failure branches into the actual fallback implementation.
5. Check actuator validation and independent flight-controller protections.
6. If the required flight behavior is undocumented, ask the developer. Do not assume hover, stop, or manual takeover is safe.
7. Propose code and mocked tests only after interfaces and requirements are known.

### Example B: Python edge gateway controlling industrial valves

**Request:** Review a Python edge controller that uses a local model to adjust coolant valves.

**Expected audit approach:**

1. Trace sensor ingestion, validation, model invocation, result freshness, and valve driver calls.
2. Check for unbounded queues, repeated tensor copies, blocked calls, and leaked inference processes.
3. Inspect NaN/Inf handling and physical command limits from documented requirements.
4. Determine whether exception and timeout paths reach a complete non-AI controller.
5. If the safe valve behavior is unspecified, ask the developer rather than choosing open, closed, or hold-last.
6. Propose pytest fault-injection tests using a fake valve interface; do not connect tests to live equipment.
