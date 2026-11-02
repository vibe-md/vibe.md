---
name: code-explainer
description: Analyzes code snippets, functions, or entire files, providing clear, structured explanations of what each function does, its parameters, and potential edge cases. Use when reviewing code, onboarding to a new codebase, or documenting complex logic.
metadata:
  categories: Productivity, Backend, Frontend
  maintainers: odelia50872
---

# Code Explainer

## Purpose
Provides clear, structured explanations and architectural breakdowns of code functions, hooks, or components, helping developers and AI agents quickly understand codebase logic.

## When to Use
- When reviewing newly written code or pull requests to understand functionality.
- When onboarding to an unfamiliar codebase or module and needing a breakdown of complex logic.
- When the user asks to explain what a specific function or file does.

Do not use this skill to apply code modifications or refactor code without explicit user requests.

## Prerequisites
- Basic familiarity with the programming language and context of the code being reviewed.

## Instructions
1. Review the code snippet, function, or file provided by the user.
2. Outline the overall objective of the code module.
3. Provide a function-by-function breakdown detailing parameters, return values, and core logic.
4. Highlight any notable edge cases, side effects, or dependencies.
5. Present the breakdown clearly and concisely to the user.

## Examples
- **User:** "Can you explain what the functions in this utility file do?"
- **Assistant:** Provides a structured, function-by-function breakdown of file parameters, return types, and clear explanations.