---
name: backend-system-architecture
description: Designs modular backend system architectures, defines clear domain boundaries, and enforces strict separation of concerns (SOLID, Clean Architecture, CQRS). Use when structuring microservices or monolithic boundaries, designing domain models, or decoupling tightly coupled backend codebases.
metadata:
  categories: Backend, Productivity, Documentation
  maintainers: benmoyal
  title: Backend System Architecture & Boundary Separation
---

# Backend System Architecture & Boundary Separation

## Purpose

Design resilient, decoupled backend architectures by establishing clear domain boundaries, enforcing strict layer separation (e.g., Domain, Application, Infrastructure, Presentation), and preventing circular dependencies or tight coupling.

## When to Use

- Designing the architecture for a new microservice or greenfield backend application.
- Refactoring a monolithic codebase suffering from tight coupling or mixed architectural layers.
- Defining bounded contexts, API boundaries, and communication contracts between services.
- Reviewing Pull Requests to ensure architectural integrity and adherence to Clean Architecture or Domain-Driven Design (DDD) principles.

Do not use this skill for low-level syntax optimization or routine database query tuning.

## Prerequisites

- A backend codebase or a defined system requirements document.
- Familiarity with design patterns, dependency inversion, and modular software engineering principles.

## Instructions

1. **Analyze Domain Boundaries:** Identify core business domains, sub-domains, and bounded contexts to ensure distinct separation of responsibilities.
2. **Enforce Layer Isolation:** Validate that dependencies point inward (e.g., Domain logic must remain pure and free of framework, database, or external HTTP concerns).
3. **Define Clear Interfaces:** Establish explicit contracts (DTOs, ports, adapters, or API schemas) for inter-module or inter-service communication.
4. **Detect and Prevent Anti-Patterns:** Check for circular dependencies, god objects, database-driven architectures, and leaky abstractions.
5. **Document the Architecture:** Summarize the proposed boundaries, data flow, and communication protocols for review.

## Examples

**User:** "Help me refactor our monolithic backend service where the database models are directly exposed in the API controllers."

**Agent:** Analyzes the tight coupling between the presentation layer and database persistence, proposes a 3-tier clean architecture layout (Controllers -> Use Cases -> Repositories -> Entities), defines data transfer objects (DTOs) to decouple wire formats from database schemas, and outlines a step-by-step migration plan.
