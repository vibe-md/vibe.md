---
name: context-first-coding
description: Implements non-trivial code changes by first inspecting the project’s conventions, affected code, dependencies, and available checks, then making focused edits and verifying them. Use for integrated feature work, complex refactors, or unfamiliar project areas where assumptions could cause incorrect changes.
license: MIT
metadata:
  auther: Bracha-Rosenfeld
  categories: Productivity, AI / Agents
  title: Context-First Coding
---

# Context-First Coding

## Purpose

Ground code changes in the project that actually exists. Understand the
relevant code and conventions before editing, distinguish verified facts from
assumptions, and deliver a focused change with evidence that it works.

## When to Use

- Implementing a feature that touches multiple files or existing workflows.
- Refactoring code in an unfamiliar or interconnected part of a project.
- Working in a project with conventions, dependencies, or architecture that
  are not obvious from the request.
- The user asks for careful implementation or says previous code relied on
  incorrect assumptions.

Do not invoke this workflow for explanations, trivial isolated edits, or
standalone code that does not need to fit an existing project. Use a more
specialized skill when one clearly matches the task. For focused duplicate
searches, third-party API verification, or cleanup of code left unused by a
change, prefer a specialized skill for that concern; this workflow focuses on
grounding and carrying out the broader implementation.

## Instructions

### 1. Ground the request in the project

1. Identify the requested outcome, constraints, and what should remain
   unchanged. Resolve ambiguity only when different interpretations would
   materially change the implementation.
2. Inspect relevant files, project guidance, tests, and the surrounding
   dependency graph. Trace important callers and callees; identify shared
   state, side effects, and dependencies the change could affect. Do not treat
   a function or component as isolated without examining its relevant context.
   Search the workspace before asking the user for information already
   available there.
3. Check applicable manifests, lockfiles, configuration, and installed
   dependencies before relying on a framework or package.
4. Inspect the current changes in files you may touch. Never overwrite or
   revert pre-existing user changes, stage existing changes, or modify
   unrelated or unfinished work just because it appears incorrect or
   inconsistent. If existing changes conflict with the request, explain the
   conflict and ask how to proceed.
5. Separate what the repository confirms from assumptions. Treat the
   implementation and surrounding behavior as stronger evidence than names
   or comments alone. If inspection contradicts the initial understanding or
   plan, reassess and update the plan before proceeding. Do not invent project
   APIs, file locations, conventions, or dependency capabilities.

### 2. Verify important assumptions

1. For a third-party API, configuration key, or command that matters to the
   change, check a suitable source of truth: installed types or source,
   version-specific project documentation, or the official documentation for
   the installed version.
2. Do not claim an API or behavior was verified unless you found evidence.
   If it cannot be verified locally, state what is missing and use available
   documentation or ask the user when the uncertainty affects correctness.
3. Follow established project patterns where they fit the requirement. Do not
   copy a pattern blindly if the current request or evidence shows it is
   unsuitable.
4. If inspection shows that work beyond the requested behavior would touch
   more than three additional files or modules, pause and ask for explicit
   approval before including that out-of-scope work. Explain why the extra
   changes seem useful. Do not count necessary callers, tests, or documentation
   for the requested behavior as scope creep just because they are additional.

### 3. Plan proportionally, then implement

1. For a multi-step or cross-cutting change, briefly state the affected areas
   and approach before editing. For a small, clear change, proceed without
   unnecessary ceremony.
2. Ask a focused question before coding only when a consequential choice
   cannot be resolved from the request or repository, such as a breaking
   interface, data migration, or materially different product behavior.
   Do not pause for approval after each routine implementation step.
3. Make the smallest coherent change that meets the request. Keep feature
   changes, refactors, and unrelated cleanup separate unless the user asks to
   combine them.
4. For multi-file or cross-cutting changes, implement in small, modular phases.
   Verify each phase independently when practical before moving to the next.
   Do not pause for approval between routine phases.
5. Update relevant tests and documentation when the change affects them. Do
   not weaken or remove checks merely to make validation pass.

### 4. Verify the result

1. Find and run the most relevant project checks, starting with focused tests
   and expanding when the change affects shared or public behavior. If
   automated tests do not exist or cannot run, consider suitable alternatives
   such as compilation, static analysis, type checking, or targeted manual
   inspection.
2. If a check fails after an edit, inspect the output and distinguish a
   regression from a pre-existing or environment-related failure. For the same
   failure, make no more than two focused fix attempts, rerunning the relevant
   check after each. If it still fails after the second attempt, stop editing,
   show the exact relevant error output, and ask the user how to proceed.
3. Review the final diff against the original scope. Confirm that existing
   imports, comments, exports, and unrelated helper logic were not
   unintentionally modified or removed. Any necessary removals must be
   intentional, relevant to the request, and reported.
4. Distinguish automated checks that actually ran from manual verification.
   Manual inspection is not a passing automated test. Do not report a check
   as passing unless it completed successfully. Report what changed, key
   assumptions or evidence, checks and their results, and anything that could
   not be verified.

## Safety Rules

- **Bounded fixes:** For the same failing check, make at most two focused fix
  attempts. If it still fails, stop and ask the user for guidance.
- **Scope protection:** Ask for explicit approval before including more than
  three additional files or modules of out-of-scope work.
- **Diff cleanliness:** Preserve existing imports, comments, exports, and
  unrelated helper logic. Investigate unexpected changes or removals; report
  any intentional, task-related removals.
- **Verification honesty:** Never claim a check passed if it failed, was
  skipped, or could not be run.

## Examples

**User:** "Add pagination to the existing results page, following the patterns
already used in this project."

**Agent:** Inspects the page, its data flow, related components, and tests;
identifies the existing pagination conventions; implements a focused change;
and runs the relevant checks. It asks only if the repository leaves an
important behavior unclear.

**User:** "Refactor this service, but keep its current behavior."

**Agent:** Reads the service, its callers, and tests before editing, states the
scope of a multi-file change, preserves observable behavior, and reports the
focused tests and other checks run.

**User:** "This change may also require cleanup across a few unrelated
modules."

**Agent:** Keeps the requested change separate from cleanup. If the proposed
out-of-scope work would touch more than three additional files or modules, it
explains the scope expansion and asks for explicit approval before including
it.

**User:** "The focused test still fails."

**Agent:** Investigates the failure and makes at most two focused fix attempts,
running the test after each. If it still fails, the agent stops, shares the
exact relevant error output, and asks the user how to proceed rather than
continuing to guess.
