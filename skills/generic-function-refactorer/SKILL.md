---
name: generic-function-refactorer
description: Identifies hard-coded or overly specific functions, components, or utilities in the codebase and refactors them into clean, reusable, parameter-driven abstractions. Use when cleaning up code, improving reusability, or abstracting repetitive implementations.
metadata:
  categories: Productivity, Backend, Frontend
  maintainers: odelia50872
---

## Purpose
Identifies hard-coded or overly specific functions, components, or utilities in the codebase and refactors them into clean, reusable, parameter-driven abstractions adhering to the DRY (Don't Repeat Yourself) principle.

*(Note: Unlike `code-hygiene` which focuses on checking for existing helpers before writing new code, this skill specifically handles refactoring and generalizing existing hard-coded or rigid code.)*

## When to Use
- When writing or reviewing functions, hooks, or components that contain hard-coded values, magic numbers, or tightly-coupled logic.
- Before finalizing a module or a feature, to scan for duplicated logic across files.
- When the user asks to clean up code, improve reusability, or abstract repetitive implementations.

## Prerequisites
- Basic familiarity with the codebase and the programming language/type system used.
- A clean working directory with existing tests to ensure refactoring safety.
- Ability to run existing tests after the refactoring process to verify no regressions were introduced.

## Rules & Best Practices
1. Analyze before modifying: Check if a similar helper or utility already exists before proposing a new abstraction.
2. Preserve signatures safely: Ensure that making a function generic does not break existing TypeScript/JSDoc types or runtime behavior in consumer components.
3. Parameterize thoughtfully: Extract hard-coded constants, API endpoints, or business-logic thresholds into well-named parameters or configuration objects with sensible defaults.
4. Clean documentation: Add clear JSDoc or TypeScript generics annotations explaining the expected types and parameters for the newly generalized function.

## Instructions
1. Analyze the concrete functions or components provided by the user for hard-coded logic or repetition.
2. Propose a clean, parameter-driven or generic abstraction while preserving type safety.
3. Wait for explicit user approval before applying changes to the codebase.

## Examples
- User: "Can you make this utility function generic so it works for multiple data types?"
- Assistant: Proposes a refactored generic implementation with clear parameters/types and asks: "Would you like to apply this refactoring?"
