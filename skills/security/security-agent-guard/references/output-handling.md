# Unsafe handling of model output

Load this file when the code uses a model's response for anything other than showing plain text to the same user.

## The risk

Model output is untrusted input. Anyone who can influence the model, directly or through content it reads, can influence the output. If the application passes the output into code execution, a query, a command, a page, or a redirect without checks, the model becomes a path for classic injection attacks.

## What to trace

Follow each model response, including structured output and tool arguments that the application uses itself, to where it ends up. Sensitive sinks include:

- code execution: `eval`, `exec`, dynamic imports, template rendering, running generated code;
- shell commands and process arguments;
- SQL or other queries built from the text;
- HTML inserted into a page without escaping (`innerHTML`, `dangerouslySetInnerHTML`, unescaped templates), and Markdown rendered with raw HTML or images allowed;
- URLs used for redirects, server-side fetches, or links;
- file paths and file names;
- decisions with real effect: approvals, prices, permissions, or sending messages.

Note any check between the output and the sink: parsing into a strict schema, allowlists, escaping, sandboxing, or human review.

## When it is a finding

Report a finding when model output reaches a sensitive sink with no check that would stop malicious content. Give file and line for the model call and for the sink.

Mark it **confirmed** when the path is visible. Mark it **suspected** when the output passes through code you could not read, such as a rendering library with unknown settings, and say what to check.

## When it is not a finding

- The output is shown as text through a mechanism that escapes it by default, such as text interpolation in React or Vue, and nothing turns it back into HTML.
- The output is parsed into a strict schema and only allowed values are used, for example a category from a fixed list.
- Generated code runs in an isolated sandbox with no network, secrets, or access to user data, and this is the intended feature.
- A person reviews the output before it has any effect.

## Severity

| Severity | When |
| --- | --- |
| High | Output reaches code execution, a shell, SQL, server-side fetches, or stored HTML that other users will see. |
| Medium | Output reaches HTML or a redirect seen only by the same user, or a sink with a partial check. |
| Low | Output drives a low-impact decision without validation, such as a sort order or a label. |

## Fixes to recommend

1. **Treat output as user input** and apply the same defenses as for any untrusted value.
2. **Ask for structured output** and validate it against a schema before use; reject anything unexpected.
3. **Escape for the destination:** HTML escaping, parameterized queries, argument lists for commands.
4. **Allowlist** URLs, hosts, file names, and actions.
5. **Sandbox** generated code, or require a person to review it before it runs.

## Example finding

> **Where:** `web/chat.js:40` (model call), `web/chat.js:52` (sink)
> **What:** Unsafe output handling. The assistant's reply is inserted with `innerHTML`, and replies are saved and shown to support staff.
> **Why it matters:** A user who makes the model output `<img src=x onerror=...>` can run script in a staff member's browser.
> **Severity:** High. Stored script injection reaching other users.
> **Certainty:** Confirmed. The call and the sink are in the reviewed file.
> **Fix:** Insert the reply as text (`textContent`), or render Markdown with raw HTML disabled and sanitize the result.
