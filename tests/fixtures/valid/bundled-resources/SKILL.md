---
name: bundled-resources
description: >
  A test skill with bundled scripts, references, and assets. Used by the vibe.md
  test suite to check that complete skill directories are installed.
license: MIT
metadata:
  author: vibe-md
  categories: Testing
  version: "1.0"
---

# Bundled Resources

## Purpose

Check that optional resources travel with the skill.

## When to Use

Only in automated tests.

## Instructions

1. Read [the guide](references/guide.md).
2. Run `scripts/hello.sh` only after reviewing it.
3. Start from the [template](assets/template.txt "Template").
4. See the [section below](#examples) and the [spec](https://agentskills.io/specification).

Links inside code are ignored: `[not a link](missing.md)`

```markdown
[also ignored](missing.md)
```

## Examples

Not applicable.
