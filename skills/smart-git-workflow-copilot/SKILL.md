---
name: smart-git-workflow-copilot
description: Provides interactive strategic guidance and workflow planning on branch management, commit scoping, and logical task segmentation. Use alongside version control tools during feature development, refactoring, or when preparing commits, pushes, and pull requests.
metadata:
  categories: Productivity, Backend, Frontend
  maintainers: odelia50872
---

# Smart Git & Workflow Copilot

Provides interactive guidance and strategic planning on branch management, commit scoping, and logical task segmentation. Unlike direct execution tools, this skill focuses on architectural workflow planning, helping users structure their development process cleanly.

## Prerequisites
- Git installed and configured in the local development environment.
- A clear understanding of the project's task scope.

## When to Use
- During feature development, refactoring, or bug-fixing sessions when organizing work structure.
- When changes span multiple distinct domains (e.g., modifying both database models and UI components simultaneously).
- When preparing to commit, push, or open a pull request and needing strategic help organizing work into clean, atomic commits and branches without overlapping version-control execution.

## Rules & Best Practices
1. **User approval required:** Always ask for and obtain explicit user confirmation before executing or recommending any automated action that modifies git state, such as committing, pushing, or opening a pull request.
2. **Proactive boundary detection:** Alert the user when current edits start crossing multiple unrelated responsibilities, suggesting a clean branch switch or separation.
3. **Conventional Commits standard:** Propose structured, descriptive commit messages adhering to standard conventions (e.g., `feat:`, `fix:`, `refactor:`, `chore:`) based on the code diff.
4. **Atomic change management:** Guide the user to split large, monolithic changes into smaller, reviewable commits and logical branches.

## Instructions
1. Analyze the user's current workspace changes or request from a structural and workflow perspective.
2. Suggest logical task segmentation and appropriate branch strategies distinct from low-level execution.
3. Propose conventional commit messages and wait for explicit user approval before proceeding with any state-changing recommendations.

## Examples
- **User:** "Help me organize my current changes into a clean development strategy."
- **Assistant:** Proposes a structured plan dividing the work into logical branches and conventional commit scopes, and asks: *"Would you like to proceed with this workflow plan?"*
