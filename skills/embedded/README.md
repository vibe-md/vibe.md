---
title: Embedded & Edge AI
summary: Security, runtime reliability, memory safety, real-time determinism, and hardware protection for embedded and edge AI systems.
categories: AI / Agents, Security, Performance
maintainers: [YaelTamari]
---

# Embedded & Edge AI

A collection of specialized skills for auditing, hardening, and testing embedded, microcontroller, and edge AI applications.

The package focuses on the interaction between AI models, hardware interfaces, operating systems, constrained resources, and deterministic control systems.

Its goal is to help developers identify runtime failures, memory exhaustion risks, unsafe AI-generated hardware commands, and incomplete non-AI recovery mechanisms before deployment.

## Skills

| Skill | What it does |
| --- | --- |
| `embedded-ai-runtime-guard` | Performs evidence-based, read-only audits of embedded and edge AI applications for memory safety, resource exhaustion, real-time execution risks, deterministic non-AI fallbacks, actuator command validation, sensor input safety, and model runtime integrity. Proposes concrete remediation and regression tests for identified gaps. |

## Installation

From a vibe.md checkout:

```bash
bash scripts/install.sh --group embedded --agent claude-code --project /path/to/project --dry-run
```

After reviewing the dry-run output:

```bash
bash scripts/install.sh --group embedded --agent claude-code --project /path/to/project
```

Supported agents include `claude-code`, `codex`, `cursor`, `gemini`, and `copilot`.

## Supported Environments

- Embedded C and C++ applications.
- Rust-based embedded systems.
- Microcontrollers and resource-constrained devices.
- FreeRTOS, Zephyr, and other RTOS environments.
- Embedded Linux and edge computing platforms.
- Raspberry Pi and NVIDIA Jetson applications.
- On-device machine learning and local inference.
- Applications using remote AI APIs to influence hardware control.
- Robotics, drones, industrial automation, and embedded prototypes.

## Engineering Focus

The package emphasizes:

- Deterministic and bounded memory usage.
- Real-time deadlines and non-blocking execution.
- Watchdog independence and fault recovery.
- Complete non-AI emergency fallback paths.
- Independent hardware command validation.
- Sensor and buffer validation.
- AI output freshness and integrity.
- Failure simulation and regression testing.

## Design Principles

1. Deterministic control must not depend on unpredictable AI execution.
2. AI-generated commands must never bypass hardware safety validation.
3. Every relevant AI failure path must have an explicitly defined recovery strategy.
4. Physical safe states must come from system requirements and hazard analysis, never from assumptions made by the auditing agent.
5. Audits are read-only by default.
6. Findings must be supported by code evidence.
7. Proposed fixes require explicit developer approval before application.
8. Static analysis must be distinguished from runtime and hardware verification.

## Safety Notice

These skills provide engineering review and code-level security assistance.

They do not certify a device as safe, replace hazard analysis, establish safety requirements, or replace hardware-in-the-loop testing and qualified engineering validation.

All proposed hardware-control changes must be reviewed against the target device's actual electrical, mechanical, operational, and safety requirements.
