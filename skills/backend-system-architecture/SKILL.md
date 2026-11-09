---
name: backend-system-architecture
description: Designs modular backend architectures, organizes code by business domains (keeping related logic together), and separates reading data from changing data. Use when structuring monoliths or services, organizing clean folder layouts, or refactoring tangled codebases.
metadata:
  categories: Backend, Productivity
  maintainers: benmoyal1
  title: Backend System Architecture & Boundary Separation
---

# Backend System Architecture & Boundary Separation

## Purpose

Design resilient, decoupled backend architectures by establishing clear domain boundaries, organizing code around business concepts rather than technical layers, and avoiding tight coupling or circular dependencies without over-engineering.

## When to Use

- Structuring a new greenfield backend application or single monolith.
- Refactoring a tangled codebase suffering from tight coupling or mixed architectural layers.
- Defining clear folder layouts and separation between reading data and modifying data.
- Reviewing Pull Requests to ensure clean boundaries and maintainability.

Do not use this skill for low-level syntax optimization or routine database query tuning.

## Anti-Over-Engineering Guidance

For most small apps, keep everything in a single app with clear, organized folders (e.g., separating business logic from database access). Only split into multiple services or complex architectures when there is a concrete, proven scaling or organizational reason.

## Prerequisites

- A backend codebase or a defined system requirements document.
- Basic understanding of modular software engineering and dependency direction.

## Instructions

1. **Map Current Structure:** Examine the existing codebase to map out current folder organization, data flow, and where modules or layers couple together.
2. **Explain the Problem:** Identify specific architectural pain points (e.g., business logic mixed directly inside database controllers or circular imports).
3. **Propose a Target Layout:** Design a small, clean target layout using clear folders (e.g., keeping core rules pure and separating read vs write operations where beneficial). **Ask before moving many files.**
4. **Refactor in Small Steps:** Implement changes incrementally. Run your test suite after each small step—**stop immediately if tests fail** and resolve the issue before proceeding.
5. **Document & Review:** Summarize the new structure and data flow for peer review.

## Examples

**User:** "Help me refactor our monolithic backend service where the database models are directly exposed in the API controllers."

**Agent:** Analyzes the tight coupling between controllers and database models, proposes a clean 3-layer folder layout (Controllers -> Use Cases -> Repositories), and outlines a step-by-step refactoring plan with tests running after each change.

**User:** "Our backend app has grown into a massive tangled folder where everything imports everything else, and tests are starting to flake."

**Agent:** Maps the current messy import graph, explains the circular dependency bottlenecks, proposes a modular folder split by feature domain, and guides a safe incremental refactoring process with continuous test verification.
