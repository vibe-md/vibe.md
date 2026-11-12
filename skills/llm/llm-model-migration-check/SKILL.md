---
name: llm-model-migration-check
description: Plans a safe switch from one language model to another. Finds every model ID and model-specific setting in the project, checks the provider's current documentation for deprecations and API differences, compares eval results on the current and target models, and drafts a rollout and rollback plan. Use when a provider retires a model, when the team wants to upgrade or change models, or when model IDs are scattered through the code. Does not change production settings or deploy.
compatibility: Needs the project's source code and configuration. Checking current model status needs network access to the provider's documentation. Running evals on a new model costs money, and the skill asks before doing it.
metadata:
  collection: vibe.md
  group: llm
---

# LLM model migration check

## Purpose

Changing a model ID is a one-line edit that can change every answer the feature gives. This skill makes the switch deliberate: find every place the project depends on a specific model, list what differs on the target model, measure the effect on the project's own evals, and plan a rollout that can be reversed quickly.

## When to Use

- A provider has announced that a model the project uses will be deprecated or retired.
- The team wants to move to a newer, cheaper, or faster model.
- The user is not sure which models the project uses, or where they are set.

Do not use this skill:

- to build the evaluation set itself. Use `llm-eval-builder` first if the project has no evals.
- to improve a prompt for the current model. Use `llm-prompt-review`.
- to make the switch in production. This skill plans and checks; the user decides and deploys.

## Prerequisites

- Read access to the code, configuration, and infrastructure files that choose a model.
- Network access to read the provider's current model and deprecation documentation. Without it, the skill marks model status as unverified.
- For eval comparisons: the project's evals and a test API key the user supplies through their environment, plus the user's approval of the cost.

## Instructions

1. **Read the provider's current documentation first.** Find the provider's model list and its deprecation or retirement page, and record the date you read them. Note the current model, the target model, and the retirement date if one is announced. Do not rely on memory for model IDs, dates, prices, or limits, since they change often. If you cannot reach the documentation, say so and mark these facts as unverified.

2. **Inventory every model dependency.** Search code, configuration files, environment variable names, infrastructure files, tests, and documentation for model IDs, aliases, and provider SDK calls. For each one, record the file and line, and how the model is chosen: hard-coded, environment variable, config file, database, or feature flag. Include fallback models and models used only in background jobs or scripts. Read the names of environment variables, never their secret values.

3. **Record the settings at each call site.** Note anything that depends on the model: maximum output tokens, temperature, stop sequences, tool or function calling, structured output or JSON mode, system prompt handling, context window, streaming, prompt caching, batch processing, rate limits, and the price per token.

4. **List the differences on the target model.** Compare each setting with the target model's documentation. Record renamed or removed parameters, changed limits, features that work differently, changed defaults, and the price difference. Tie each difference to the call sites it affects. Mark each item as confirmed from the documentation, inferred, or unknown.

5. **Note centralization separately.** If the model ID appears in many places, recommend a single setting that every call site reads. Treat that as its own change, and do not mix it into the migration unless the user asks.

6. **Measure behavior with the project's evals.** If evals exist, run the same cases on the current and target models, after showing the user a cost estimate and getting approval. Start with a small sample. Compare the results check by check, and list the cases that newly fail. If there are no evals, recommend building a small set with `llm-eval-builder` before switching. Do not describe the models as equivalent without a measurement.

7. **Draft a rollout and rollback plan.** Order the call sites from lowest to highest risk. Recommend switching through a setting or feature flag, so rollback is a configuration change and not a code change. List what to watch after the switch: error rate, parse failures, latency, cost, and user-facing complaints. State the condition that triggers a rollback.

8. **Report.** Include the documentation read and its date, the inventory table, the differences, the eval comparison and its sample size, the expected cost change, the risks, the unknowns, and the plan. Keep confirmed facts, documentation claims, and your own inferences clearly separate.

9. **Do not change production.** Do not edit production configuration, rotate or print keys, or deploy. Edit code only if the user asks, one call site at a time. Do not commit or push unless asked.

## Example inventory

```text
Documentation read: provider model list and deprecations page, read on <date>

| Where                    | Model chosen by    | Current model | Settings that matter           |
| ------------------------ | ------------------ | ------------- | ------------------------------ |
| app/summarize.py:14      | env MODEL_NAME     | <current-id>  | max tokens 512, JSON mode      |
| jobs/tagging.py:30       | hard-coded         | <current-id>  | tools, temperature 0           |
| scripts/backfill.py:8    | hard-coded         | <older-id>    | batch processing               |
```

## Examples

**User:** "Our provider says the model we use is being retired next quarter. What do we need to do?"

**Agent:** Reads the provider's deprecation page and records the date. Finds three call sites, one of which uses an even older model in a backfill script nobody remembered. Lists that the target model renames a token-limit parameter and handles JSON mode differently. Proposes running the existing evals on both models, after showing the cost, and drafts a flag-based rollout with a rollback condition.

**User:** "Switch everything to the newest model."

**Agent:** Explains that it will plan and check the switch, not deploy it. Produces the inventory and the list of differences, recommends measuring with the project's evals first, and offers to make the code edits one call site at a time if the user approves.
