---
name: git-conflict-resolver
description: Helps developers understand, investigate, and safely resolve Git merge conflicts, rebase conflicts, cherry-pick conflicts, and competing changes across branches. Use when Git reports merge conflicts or when a developer needs help reconciling conflicting file changes.
license: MIT
metadata:
  author: Faigy-Rosenfeld
  category: Version Control
  title: Git Conflict Resolver
---
# Git Conflict Resolver

## Purpose
Help developers safely understand and resolve Git conflicts without accidentally losing important code changes.
The goal is not simply to remove conflict markers, but to understand the intention behind both versions of the code and produce a correct combined result.

## When to Use
Use this skill when:
- A Git merge produces conflicts.
- A Git rebase stops because of conflicting changes.
- A cherry-pick operation produces conflicts.
- Two branches modify the same lines of a file.
- A developer needs help understanding Git conflict markers.
- A developer is unsure which version of a file to keep.

Do not use this skill for unrelated programming errors.

## Instructions

### Step 1: Understand the Situation
1. Ask the developer what Git operation they performed.
2. Identify whether the conflict comes from a merge, rebase, cherry-pick, or another operation.
3. Inspect the current Git status.
4. Identify all files marked as conflicted or modified.
5. Never assume that choosing one side is always correct.

Useful commands:
```bash
git status
git diff --name-only --diff-filter=U
```

### Step 2: Understand Conflict Markers and Branch Roles
Git conflict markers typically look like this:
```text
<<<<<<< HEAD
Current branch changes
=======
Incoming branch changes
>>>>>>> feature-branch
```

Explain the meaning based on the current Git operation:
- **During a Merge:**
  - `<<<<<<< HEAD` (Ours): The branch you were on when you ran `git merge`.
  - `>>>>>>> branch-name` (Theirs): The branch you are merging into your current branch.
- **During a Rebase:**
  - `<<<<<<< HEAD` (Ours): The upstream branch or commit being rebased onto (the base).
  - `>>>>>>> commit-hash/branch` (Theirs): The commit/branch containing your custom changes that are being reapplied.

### Step 3: Inspect Both Versions
For every conflicted file:
1. Inspect the two original versions directly from the Git index:
   - Stage 2 (`:2:`): "Ours" version.
   - Stage 3 (`:3:`): "Theirs" version.
2. Handle cases where a file was deleted on one side (check if the file exists in stage 2 or 3).
3. Read the complete file and understand the implementations on both sides.
4. Identify what each change is trying to accomplish.
5. Check whether both changes can be combined.
6. Look for dependencies between the conflicting changes.

Useful commands:
```bash
# View versions directly from the Git index
git show :2:path/to/file # "Ours" version
git show :3:path/to/file # "Theirs" version

# Compare working tree with specific sides
git diff --ours -- path/to/file
git diff --theirs -- path/to/file
```

Do not select an entire version without understanding what changes would be discarded.

### Step 4: Decide on a Resolution
Choose the appropriate strategy:

**Option A: Keep the current version**
Use when the incoming changes are unnecessary and the current implementation is correct.

**Option B: Keep the incoming version**
Use when the incoming implementation is intended to replace the current implementation.

**Option C: Combine both versions**
Use when both branches contain important changes that need to be preserved.

**Option D: Rewrite the conflicting section**
Use when the two implementations are incompatible and a new combined solution is required.

Always explain why the selected strategy is appropriate.

### Step 5: Resolve the Conflict
1. Remove the Git conflict markers.
2. Preserve the required code from both branches.
3. Ensure the resulting code is syntactically valid.
4. Check imports, function names, and dependencies.
5. Avoid unrelated refactoring.
6. Show the proposed changes to the developer.

Never overwrite files or discard changes without the developer's authorization.

### Step 6: Verify the Resolution
After editing the conflicted files:
1. Search for remaining conflict markers (`git diff --check`).
2. Inspect all staged changes to ensure no unrelated staged files are included.
3. Run relevant tests.
4. Run the project's build or compilation command.
5. Confirm that all intended changes were preserved.

Useful commands:
```bash
git diff --check
git diff --staged
git status
```

### Step 7: Complete the Git Operation
Only after the developer confirms the resolution and staged files:

For a merge:
```bash
git add <resolved-files>
git status # Ensure only intended files are staged
git commit
```

For a rebase:
```bash
git add <resolved-files>
git rebase --continue
```

For a cherry-pick:
```bash
git add <resolved-files>
git cherry-pick --continue
```

Do not run these completion commands blindly. First verify which Git operation is in progress.

## Safety Rules
- Never run `git reset --hard` as a conflict-resolution shortcut.
- Never run `git clean -fd` to remove conflict files.
- Never discard uncommitted changes without permission.
- Never force-push without explicit authorization.
- Never use `git checkout --ours` or `--theirs` on all files without inspecting their contents.
- Never claim a conflict is resolved without verification.
- Always check staged changes (`git diff --staged`) before committing to avoid committing unrelated files.
- Preserve the original intent of both branches whenever possible.

## Examples

### Example 1: Two branches modify the same function
User:
"My merge has a conflict in calculateTotal()."

Expected behavior:
1. Inspect both implementations using `git show :2:file` and `git show :3:file`.
2. Identify what each branch changed.
3. Determine whether both changes are needed.
4. Suggest a combined implementation.
5. Explain the result.
6. Recommend tests for the function.

### Example 2: Conflict during rebase
User:
"My rebase stopped and Git says there are conflicts."

Expected behavior:
1. Run `git status`.
2. Identify the files with conflicts.
3. Explain the difference between "Ours" and "Theirs" in the context of a rebase.
4. Propose a resolution.
5. Verify staged changes before continuing.

### Example 3: Developer wants to keep both changes
User:
"I need both versions of this code. How can I combine them?"

Expected behavior:
1. Inspect both code sections.
2. Understand their responsibilities.
3. Identify duplicate or incompatible logic.
4. Propose a clean combined implementation.
5. Explain how to test the result.