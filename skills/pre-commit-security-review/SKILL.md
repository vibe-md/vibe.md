---
name: pre-commit-security-review
description: Reviews staged, changed, and new files for security vulnerabilities such as injection, unsafe deserialization, missing validation, broken access control, and sensitive data in logs, then explains each finding and how to fix it. Use before committing or pushing, or when the user asks whether their changes are safe.
license: MIT
compatibility: Requires git. Works with any language or framework.
metadata:
  collection: vibe.md
  author: Yossi4
  categories: Security, Version Control
  maintainers: Yossi4
  title: Pre-commit Security Review
---

# Pre-commit security review

## Purpose

Catch code-level security problems in the changes about to be committed, and teach the reader why each one is dangerous, so the fix is understood and not just applied.

## When to Use

- Before a commit or push, on the staged or changed files.
- The user asks "is this safe?", "check my changes for security issues", or similar.
- New code handles user input, queries a database, runs commands, reads files, parses data, authenticates users, or calls other services.

Do not use this skill to hunt for leaked credentials in config files; use a secret-scanning skill such as `secret-guard` for that. This one reviews the logic of the code.

## Prerequisites

- git, to read the changes.
- No specific language or framework is assumed. Take the stack from the project itself.
- Permissions: read-only. The skill runs only `git status` and `git diff` and reads files. It never edits, stages, commits, or deletes anything, so no command in it can lose work.

## Instructions

1. Scope to the change. Run `git status`, then read `git diff --staged` (or `git diff` if nothing is staged). New untracked files do not appear in a diff, so read them directly. Review only changed code and the code it directly calls. Do not audit the whole repository.
2. If the change is large, review first the files that touch input, databases, files, the network, authentication, or authorization, and say which files you did not reach.
3. Trace untrusted input. This is the core of the review. For each place data enters (request parameters, headers, file uploads, message queues, external API responses, files, environment), follow it to where it is used. A problem exists when untrusted data reaches a sensitive place without validation or encoding.
4. Use this list as a checklist after the trace, skipping classes that do not apply to the stack:
   - Injection: SQL, NoSQL, OS command, LDAP, XPath, template, and log injection. Look for string concatenation or formatting into queries and commands.
   - Unsafe deserialization of data from outside the trust boundary.
   - Path traversal and unsafe file handling (`../`, user-controlled file names, unrestricted uploads).
   - Server-side request forgery: user-controlled URLs fetched by the server.
   - Cross-site scripting and unescaped output in generated HTML.
   - Broken access control: missing authentication or authorization checks, trusting client-supplied IDs or roles.
   - Missing or weak input validation: size, type, range, and format limits.
   - Sensitive data exposure: secrets, personal data, tokens, or full request bodies written to logs or error messages.
   - Weak cryptography: home-made crypto, outdated hashes for passwords, hard-coded keys, disabled certificate checks.
   - Resource handling: missing timeouts, unbounded reads, and unclosed resources that allow denial of service.
5. If the change adds or upgrades a dependency, list it and tell the user to check it for known vulnerabilities. This skill does not audit dependencies.
6. Report each finding with the same five parts:
   - Where: file and line.
   - What: the problem in one sentence.
   - Why it matters: a concrete attack, for example the exact input that would exploit it.
   - Severity: high, medium, or low, with a one-line reason.
   - Fix: the stronger version of the code, and why it is better than the alternatives (for example, parameterized queries over escaping).
7. Separate certainty from suspicion. Mark each finding as confirmed (the exploit path is visible in the code) or suspected (it depends on code you could not see). Never present a suspicion as fact.
8. Do not change code, stage files, or commit unless the user asks. Present findings first and let the user decide what to fix.
9. Close with a verdict: safe to commit, commit after fixing the high items, or do not commit. If nothing was found, say what was checked, since a clean result only covers the classes reviewed.

## Examples

**User:** "Check my staged changes before I push."

**Agent:** Reads `git diff --staged`, finds a query built with string concatenation from a request parameter, and reports: where (file and line), what (SQL injection), why (input `' OR '1'='1` returns every row), severity high and confirmed, and the fix (a parameterized query, because the database treats the value as data and never as SQL). Ends with the verdict "fix the high item before committing".

**User:** "Is this logging OK?"

**Agent:** Notes that the full request body, including a personal-ID field, is logged on error, explains that logs are usually kept longer and read by more people than the database, and suggests logging only the request ID and the field names.
