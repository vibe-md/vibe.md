---
name: generic-function-refactorer
description: Identifies hard-coded or overly specific functions, components, or utilities in the codebase and refactors them into clean, reusable, parameter-driven abstractions. Use when cleaning up code, improving reusability, or abstracting repetitive implementations.
metadata:
  categories:
    - Frontend
    - Backend
    - Productivity
  maintainers:
    - odelia50872
---

# Generic Function Refactorer

Identifies hard-coded or overly specific functions, components, or utilities in the codebase and refactors them into clean, reusable, parameter-driven abstractions adhering to the DRY (Don't Repeat Yourself) principle.

## When to Use
- When writing or reviewing functions, hooks, or components that contain hard-coded values, magic numbers, or tightly-coupled logic.
- Before finalizing a module or a feature, to scan for duplicated logic across files.
- When the user asks to clean up code, improve reusability, or abstract repetitive implementations.

## Rules & Best Practices
1. **Analyze before modifying:** Check if a similar helper or utility already exists (coordinating with tools like Code Hygiene) before proposing a new abstraction.
2. **Preserve signatures safely:** Ensure that making a function generic does not break existing TypeScript/JSDoc types or runtime behavior in consumer components.
3. **Parameterize thoughtfully:** Extract hard-coded constants, API endpoints, or business-logic thresholds into well-named parameters or configuration objects with sensible defaults.
4. **Clean documentation:** Add clear JSDoc or TypeScript generics annotations explaining the expected types and parameters for the newly generalized function.
