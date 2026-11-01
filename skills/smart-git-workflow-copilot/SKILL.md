---
name: smart-git-workflow-copilot
description: Monitors development progress and codebase changes in real time to provide proactive guidance on branch management, commit scoping, and logical task segmentation. Use during feature development, refactoring, or when preparing commits, pushes, and pull requests.
metadata:
  categories:
    - Productivity
    - Backend
    - Frontend
  maintainers:
    - odelia50872
---

# Smart Git & Workflow Copilot

Monitors development progress and codebase changes in real time to provide proactive guidance on branch management, commit scoping, and logical task segmentation.

## When to Use
- Continuously during feature development, refactoring, or bug-fixing sessions.
- When changes span multiple distinct domains (e.g., modifying both database models and UI components simultaneously).
- When the user is ready to commit, push, or open a pull request and needs help organizing work into clean, atomic commits and branches.

## Rules & Best Practices
1. **Proactive boundary detection:** Alert the user when current edits start crossing multiple unrelated responsibilities (e.g., mixing a bug fix with a brand-new feature), suggesting a clean branch switch or separation.
2. **Conventional Commits standard:** Propose structured, descriptive commit messages adhering to standard conventions (e.g., `feat:`, `fix:`, `refactor:`, `chore:`) based on the staged or modified code diff.
3. **Atomic change management:** Guide the user to split large, monolithic changes into smaller, reviewable commits and logical branches to keep the git history clean and maintainable.
4. **Non-intrusive alerts:** Provide concise recommendations without interrupting the user's active coding flow unless a high-risk divergence (like editing production config on a feature branch) is detected.
