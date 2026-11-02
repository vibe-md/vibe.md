# Sensitive information in AI features

Load this file when the code builds prompts, sends data to a model provider, or stores prompts and responses.

## Scope

This file covers exposure that exists because the application uses a model. It does **not** cover secrets committed to the repository or secrets in ordinary logs. For those, use `secret-guard` and `pre-commit-security-review` if they are installed, and say so in the report.

## The risk

- **Secrets in prompts:** API keys, passwords, internal URLs, or other users' data written into a system prompt or template. Models can be led to repeat their instructions, so nothing in a prompt should be treated as hidden from the user.
- **Unneeded data sent to the provider:** personal or confidential fields sent to an external model when the task does not need them.
- **Stored conversations:** full prompts and responses written to logs, analytics, or databases with no limit, redaction, or retention rule. Users type private things into chat boxes.
- **Responses that include other data:** the model receives data the current user may not see, so it can repeat it in the answer.

## What to trace

1. **Prompt construction.** Read system prompts, templates, and the code that fills them. Note any secret, credential, internal address, or data about people other than the current user.
2. **Fields sent.** For each model call, list the data fields included. Compare them with what the task needs.
3. **Storage of conversations.** Find where prompts, responses, and tool results are logged or saved, and whether sensitive fields are removed and how long the data is kept.
4. **Data the model sees.** Check whether the context includes records the current user is not allowed to see.

## When it is a finding

Report a finding when you can point to both:

- the specific secret or sensitive field, with file and line, and
- where it goes: the prompt, the provider call, the log, or the store, with file and line.

Do not print a secret value in the report. Give the file, the line, the variable name, and the first four characters at most.

## When it is not a finding

- Credentials are read from environment variables or a secrets manager and used only to authenticate the API call, not placed in the prompt.
- The data sent is what the feature exists to process, such as a document the user asked to summarize, and the provider and data handling are documented.
- Prompts and responses are logged with sensitive fields removed, or only metadata such as length, timing, and model is logged.
- The variable name looks sensitive (`token`, `key`), but the value is not a secret, such as a token count.

## Severity

| Severity | When |
| --- | --- |
| High | A live credential or another user's private data is placed in a prompt, or full conversations containing personal data are stored with no access control. |
| Medium | Personal or confidential fields are sent to the provider without need, or conversations are stored with access control but no redaction or retention limit. |
| Low | Internal details such as hostnames or business rules are in a prompt, with limited harm if repeated. |

## Fixes to recommend

1. **Keep secrets out of prompts.** Tools that need credentials read them in code; the model never sees them.
2. **Send only needed fields.** Remove or mask identifiers before the model call.
3. **Redact and limit logs.** Remove sensitive fields before storing, restrict access, and set a retention period.
4. **Scope context to the user.** Give the model only data the current user may see.
5. **Assume the prompt is public.** Write system prompts as if users will read them.

## Example finding

> **Where:** `bot/prompts.py:5` (secret), `bot/chat.py:22` (model call)
> **What:** Secret in system prompt. The internal admin API key (`sk-a...`) is written into the system prompt so the model can "include it in requests".
> **Why it matters:** A user can ask the model to repeat its instructions and receive a working admin key.
> **Severity:** High. A live credential can be disclosed to any user.
> **Certainty:** Confirmed. The prompt and the call are in the reviewed files.
> **Fix:** Remove the key from the prompt. Give the model a tool that calls the admin API in code, reading the key from the environment and checking the user's permission.
