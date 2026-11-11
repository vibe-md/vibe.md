---
name: smart-git-workflow-copilot
description: Provides interactive planning and strategic workflow design for branching, commit scoping, and logical task segmentation. Use this skill when planning how to organize work before executing actions with gitly-save, gitly-branches, or gitly-sync.
metadata:
  categories: Productivity, Backend, Frontend
  maintainers: odelia50872
---

## Purpose
Provides interactive planning and strategic workflow design for branching, commit scoping, and logical task segmentation. This skill focuses purely on architectural planning and structuring your development process.

## When to Use
- When planning how to structure complex changes, features, or refactoring sessions before touching git commands.
- When you need help deciding how to segment a large task into logical pieces.

## Prerequisites
- Basic familiarity with your project structure and development goals.

## Relationship with Gitly
This skill focuses **only on planning and strategy**. For actual execution and command-line operations, use the dedicated independent skills in the `gitly` package:
- **`gitly-save`**: Use when you are ready to save your work and create commits.
- **`gitly-branches`**: Use when creating or switching between branches and experiments.
- **`gitly-sync`**: Use when pushing changes, backing up, or syncing with GitHub.

## Rules & Best Practices
1. **User approval required:** Always ask for and obtain explicit user confirmation before recommending any git-state-changing actions.
2. **Planning separation:** Keep planning advice strictly separate from execution commands, directing execution tasks to `gitly`.

## Instructions
1. Analyze the user's development state and goals from a planning perspective.
2. Propose a structured workflow plan, suggesting when to use `gitly-save`, `gitly-branches`, or `gitly-sync` for the actual execution.
3. Wait for explicit user approval before proceeding.

## Examples
- **User:** "How should I structure my changes for this new feature?"
- **Assistant:** Proposes a strategic task-segmentation plan and advises using `gitly-branches` to create the feature branch and `gitly-save` when committing.
