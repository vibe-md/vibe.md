---
name: llm-prompt-review
description: Reviews the prompts and prompt templates behind an LLM feature for a clear task, an output format that matches the code that parses it, handling of edge cases, and testability, then proposes specific edits. Use when the user asks to review or improve a prompt, before merging a prompt change, or when an LLM feature gives inconsistent or unparseable output. Read-only unless the user asks for edits. Not for prompt-injection or other security review.
compatibility: Needs the project's source code. Reviewing a prompt needs no network access or model calls. Measuring a proposed change uses the project's evals, which may call a paid model and ask first.
metadata:
  collection: vibe.md
  group: llm
---

# LLM prompt review

## Purpose

Find the problems in a prompt that change what the model produces: an unclear task, an output format the code cannot parse, missing instructions for edge cases, and conflicting rules. Propose small, specific edits with a reason for each, and recommend how to measure whether the edit helped. The goal is a prompt that gives consistent, usable output, not a prompt that reads more elegantly.

## When to Use

- The user asks to review, improve, or tighten a prompt or prompt template.
- A prompt change is about to be merged.
- An LLM feature gives inconsistent answers, ignores instructions, or returns output the code fails to parse.

Do not use this skill:

- to look for prompt injection or other security risks. Use `security-agent-guard`.
- to build an evaluation set. Use `llm-eval-builder`, and come back here to improve the prompt it measures.
- to choose or switch models. Use `llm-model-migration-check`.

## Prerequisites

- The project's source code, including where prompts are stored and where the model's output is parsed or used.
- No API keys or model calls are needed for the review. Running evals to measure a change is optional and needs the user's approval because it costs money.

## Instructions

1. **Find every part of the prompt.** Locate the system prompt, templates, few-shot examples, tool descriptions, and the code that assembles them. Record the file and line for each part and for every variable inserted into the prompt. Review the prompt as the model receives it, after assembly, not only the template file.

2. **Learn what the output is for.** Read the code that receives the model's response. Note whether it parses JSON or another format, which fields it reads, what it shows to users, and what happens when parsing fails. If the purpose of the feature is unclear, ask the user for one output they would ship and one they would reject.

3. **Check the prompt against this list.** Report only the items that apply:
   - **Task:** the job is stated plainly near the start. A role ("You are an expert...") adds nothing unless it carries real context.
   - **Output format:** the format is stated explicitly and matches what the parser expects, including field names, types, and whether the response is JSON or plain text. A mismatch here is usually the most important finding.
   - **Edge cases:** the prompt says what to do with empty or missing input, very long input, an unsupported language, and a question that has no answer in the provided context. A model told nothing will guess.
   - **Conflicts:** no two instructions contradict each other, and important rules are not buried after a long block of context.
   - **Vague words:** words like "appropriate," "good," or "concise" are replaced with something checkable, such as a length limit or a list of required sections.
   - **Examples:** examples match the required format, cover more than one kind of input, and do not contain text the model is likely to copy into real answers.
   - **Variables:** inserted values are clearly separated from instructions, and the prompt still makes sense when a variable is empty.
   - **Cost:** large static text repeated on every call is necessary. If the provider supports prompt caching, static parts come before the parts that change.

4. **Check the prompt and code together.** Compare the requested format with the parser, the validation, and any retry logic. Note where the code silently accepts bad output or fails without telling the user.

5. **Rank the findings by effect on output.** Put first what is most likely to produce wrong or unusable output. Drop wording preferences that would not change the model's behavior.

6. **Propose edits as a diff.** For each finding, show the smallest change that fixes it, with a one-line reason. Keep the original intent and voice. Do not rewrite the whole prompt unless the user asks for that.

7. **Recommend how to measure the change.** If the project has evals, recommend running them before and after the edit, and ask before any paid run. If it has none, suggest `llm-eval-builder`. Do not claim the edited prompt is better without a measurement.

8. **Mention security only briefly.** If untrusted text reaches a prompt that can call tools or see other users' data, say so in one line and point to `security-agent-guard`. Do not perform that review here.

9. **Do not change files unless asked.** If the user asks for the edits, apply one change at a time and show it. Do not commit, push, or deploy.

## Report format

For each finding:

- **Where:** file and line in the prompt, and in the code when relevant.
- **What:** the problem in one sentence.
- **Why it matters:** the output it causes, such as "the parser expects `items`, but the prompt asks for `results`, so every response fails to parse."
- **Edit:** the proposed change as a short diff.

End with how to measure the change, and with anything you could not check, such as a prompt assembled at runtime from a database.

## Examples

**User:** "Our summary feature sometimes returns a bulleted list and sometimes a paragraph. Can you fix the prompt?"

**Agent:** Finds the template and the code that displays the summary. Reports that the prompt asks for "a short summary" with no format, and that one of the two examples uses bullets while the other does not. Proposes a stated format, a length limit, and consistent examples, as a diff. Recommends measuring with `llm-eval-builder` before merging.

**User:** "Review this prompt before I merge it."

**Agent:** Reviews the assembled prompt and the parser. Finds that the prompt requests a field named `category`, while the code reads `type`, and that nothing says what to return when the input is empty. Reports those two findings with edits, and notes that the rest of the prompt is clear.

**User:** "Can someone trick this prompt into leaking data?"

**Agent:** Explains that this is a security question and suggests `security-agent-guard`.
