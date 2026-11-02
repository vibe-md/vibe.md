---
name: security-agent-guard
description: Reviews code that uses LLMs or AI agents for AI-specific security risks - prompt injection, excessive agent permissions, unsafe tool calls, cross-user data leaks in retrieval (RAG), secrets or personal data in prompts, and unsafe use of model output. Reports evidence-based findings with file and line, severity, certainty, and a fix. Use when the user asks to review the security of an AI feature, chatbot, agent, tool integration, or RAG pipeline. Not for general code security or committed secrets.
license: MIT
compatibility: Read-only. Needs access to the source code. Works with any language or framework; examples use Python and JavaScript.
metadata:
  collection: vibe.md
  group: security
  author: NoaGaler
---

# AgentGuard: AI application security review

## Purpose

Find security problems that exist because an application uses a language model: the model reads untrusted text, chooses actions, calls tools, retrieves data, and produces output that other code trusts. Report only what the code shows, explain why it matters, and suggest a fix the developer can apply.

## When to Use

- The user asks whether an AI feature, chatbot, agent, or RAG pipeline is secure.
- The user asks for a security review of code that calls a model API, defines tools for a model, or builds prompts.
- The user asks about prompt injection, agent permissions, or data leaks through an AI feature.

Do not use this skill:

- to review code that does not use a model. Use `pre-commit-security-review` if it is installed.
- to find secrets committed to the repository. Use `secret-guard` if it is installed.
- to build or change an AI feature. This skill only reviews.

## Prerequisites

- Read access to the source code.
- No tools, accounts, or network access are required.
- Permissions: read-only. The skill reads files and, when available, runs `git status` and `git diff` to find changes. It never edits, deletes, commits, or runs project code.

## Instructions

1. **Set the scope.** Review what the user named. If they named nothing, review the current changes (`git diff --staged`, then `git diff`, plus new untracked files). If they ask for the whole project, start with files that use a model and say which files you did not reach.
2. **Find the model calls.** Search the scope for model SDKs and APIs, prompt templates, tool or function definitions, agent frameworks, MCP servers, and vector stores. If there are none, say so and stop: this skill does not apply.
3. **Map each AI feature.** For each model call or agent loop, write down:
   - **sources:** where text enters the prompt, and which of it is untrusted;
   - **capabilities:** tools the model can call and data it can see;
   - **sinks:** where the output and tool arguments end up.
4. **Load only the references that apply.**
   - Untrusted text reaches a prompt: [prompt injection](references/prompt-injection.md).
   - The model has tools or acts on its own: [excessive agency](references/excessive-agency.md) and [tool calling](references/tool-calling.md).
   - The code retrieves documents or embeddings into prompts: [RAG security](references/rag-security.md).
   - Prompts contain configuration or user data, or conversations are stored: [sensitive information](references/sensitive-information.md).
   - Output is used for anything other than plain text shown to the same user: [output handling](references/output-handling.md).
5. **Trace each path from source to sink.** Apply the "When it is a finding" and "When it is not a finding" rules in the reference. A finding needs a location in the code for every part of its path.
6. **Separate certainty from suspicion.** Mark each finding **confirmed** when the whole path is in code you read, or **suspected** when part of it is in code you could not read, and say which part and how to check it. Never present a suspicion as fact.
7. **Do not report** generic advice, missing best practices without a path to harm, or risks in code outside the scope. Do not print secret values.
8. **Write the report** in the format below, highest severity first.
9. **Do not change code** unless the user asks. If they ask, fix one finding at a time and show the change.

## Report format

For each finding:

- **Where:** file and line for each part of the path.
- **What:** the problem in one sentence, with the risk name.
- **Why it matters:** a concrete misuse, such as the input that would cause it.
- **Severity:** high, medium, or low, with a one-line reason.
- **Certainty:** confirmed or suspected.
- **Fix:** the change to make, and why it is stronger than the alternatives.

End with:

- **Coverage:** which AI features and which risk areas were checked, and which were skipped as not applicable. A clean result covers only what was checked.
- **Out of scope:** issues noticed that belong to other reviews, such as general web security or committed secrets, in one line each.

## Examples

**User:** "Is my support chatbot secure? The code is in `support/`."

**Agent:** Finds the model call and its tools in `support/`, maps sources (customer messages, order records), capabilities (`lookup_order`, `issue_refund`), and sinks (the reply shown in the staff dashboard). Loads the prompt injection, excessive agency, tool calling, and output handling references. Reports that `issue_refund` runs without confirmation for any amount the model provides (high, confirmed), and that replies are inserted with `innerHTML` in the dashboard (high, confirmed). Lists RAG as not applicable.

**User:** "Review my changes before I commit."

**Agent:** Reads the diff. The changes touch only CSS and a date helper, with no model calls. Says that this skill does not apply and suggests a general security review instead.
