# Excessive agency

Load this file when the code gives a model tools, functions, or the ability to act on its own.

## The risk

An agent should have only the power its task needs. Every extra tool, broad permission, or unattended action raises the damage when the model is wrong or manipulated (see `prompt-injection.md`).

This file asks **which** capabilities the agent has. How each tool checks its input is covered in `tool-calling.md`.

## What to trace

1. **Stated purpose.** Find what the agent is for: its system prompt, the feature name, the README, or the user's description.
2. **Tool list.** List every tool, function, plugin, or MCP server registered for that agent, with file and line.
3. **Reach of each tool.** For each one, note:
   - what it can touch (one folder or the whole disk, one table or the whole database, one recipient or anyone);
   - whether it can only read, or can also write, send, delete, pay, or run code;
   - whose permissions it uses (the current user's, or a service or admin account).
4. **Autonomy.** Check whether irreversible or external actions run without a person approving them, and whether the agent loop has a step limit.

## When it is a finding

Report a finding when the code shows at least one of these:

- **Unneeded tool:** a tool that has no clear use for the stated purpose. Name the tool and the purpose.
- **Overly broad tool:** a tool that can do far more than the task needs, such as a general shell, raw SQL, or any URL, when a narrow action would do.
- **Elevated permissions:** a tool that acts with a service, admin, or shared account instead of the current user's permissions.
- **No approval:** an irreversible or external action that runs without a confirmation step.

Mark it **confirmed** when the tool registration and its reach are both visible. Mark it **suspected** when the reach depends on configuration you could not read, such as cloud permissions or a token's scopes, and say what to check.

## When it is not a finding

- The tool is clearly needed for the stated purpose and is limited to what that purpose needs.
- A broad tool is restricted in code, for example by an allowlist of commands, paths, or hosts that the model cannot change.
- The action is irreversible but the code asks the user to confirm it and shows what will happen.
- The agent is a local developer tool the user runs on purpose, and its broad access is documented and expected. Mention it as context, not as a finding.

## Severity

| Severity | When |
| --- | --- |
| High | The agent can take an irreversible or external action, or act with admin or service-wide permissions, without approval, and it reads any untrusted content. |
| Medium | The agent has broad or unneeded capability, but actions are reversible, limited in scope, or need approval for part of the cases. |
| Low | An unneeded tool is registered but is read-only and touches only data the user can already see. |

## Fixes to recommend

1. **Remove** tools the purpose does not need.
2. **Narrow** the rest: read-only where possible, fixed folders, tables, hosts, or recipients, enforced in code.
3. **Use the user's permissions.** Pass the current user's identity to each tool and check access there, not in the prompt.
4. **Add approval** for irreversible or external actions, showing the exact action and parameters.
5. **Limit the loop.** Cap the number of steps or tool calls per request, and log each action for review.

## Example finding

> **Where:** `support/agent.ts:30` (tool list), `support/tools/db.ts:12` (tool)
> **What:** Excessive agency. A support chatbot that answers order questions is given `run_sql`, which executes any SQL with the application's database account.
> **Why it matters:** If the model is wrong or manipulated, it can read every customer's data or delete tables; the task only needs to look up one order for the signed-in user.
> **Severity:** High. Database-wide write access with no approval, in an agent that reads user messages.
> **Certainty:** Confirmed. The registration and the tool code are both in the reviewed files.
> **Fix:** Replace `run_sql` with `get_order(order_id)`, which runs a fixed, parameterized query and checks that the order belongs to the signed-in user.
