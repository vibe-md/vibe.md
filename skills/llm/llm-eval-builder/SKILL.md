---
name: llm-eval-builder
description: Builds a small, repeatable evaluation set and runner for an LLM feature, with deterministic checks, optional rubric grading, and baseline comparison that catches regressions after a prompt or model change. Use when adding evals to an AI feature, checking whether a prompt or model change made outputs better or worse, or when the user asks how to measure LLM output quality. Not for security review, general unit tests, or one-off prompt wording.
compatibility: Needs the project's source code and a way to run its LLM feature locally. Model calls cost money and send data to a model provider, so the skill asks before running them. No network access is needed to write the eval set itself.
metadata:
  collection: vibe.md
  group: llm
---

# LLM eval builder

## Purpose

Turn "I think the new prompt is better" into a measurement. Build a small set of realistic cases, check each output with the cheapest reliable test first, and keep a baseline so the next prompt or model change can be compared against it. The result is a repeatable script the team can run, not a one-time impression.

## When to Use

- The user is building or changing an LLM feature and wants to know whether outputs are getting better or worse.
- A prompt, model, or retrieval setting has changed and the user needs to check for regressions.
- The user asks how to test or measure LLM output quality.

Do not use this skill:

- to review a feature for security problems. Use `security-agent-guard` for AI-specific risks.
- to write general unit tests for ordinary code. Use the project's normal test practice.
- to tweak wording in one prompt without a measurable goal. Measure first.
- to run evals against production systems, real customer data, or live accounts.

## Prerequisites

- The feature's source code: the prompt or template, the function that calls the model, and the code that parses the result.
- A way to call the feature locally. A test key for the model provider is needed only for live runs, and the user supplies it through their own environment. Never write a key into the repository.
- A decision from the user on the budget for live runs: roughly how many cases, which model, and how often.
- Permission to create files in the project. The skill writes an eval file and a runner, and nothing else, unless the user asks for more.

## Instructions

1. **Define "good" with the user before writing any case.** Ask for three outputs they would be happy to ship and three they would reject, and for the single most important failure to avoid. Write these down as the first draft of the quality criteria. If the user cannot describe good output yet, stop and say that the feature needs a clearer spec first.

2. **Find the unit under test.** Locate the function or endpoint that builds the prompt, calls the model, and returns the result. Evaluate that whole path, not the raw model call, so prompt templates, parsing, and post-processing are included. Record the file and line for each part, and the prompt's version (its file path, or a hash of its text).

3. **Collect 20 to 50 cases.** Prefer real inputs from logs or support tickets, with personal and confidential details removed or replaced with synthetic values. If there are no real inputs, write synthetic ones and say so. Cover the normal case, at least one case per important failure mode the user named, an empty or very short input, a very long input, and one input in each language the feature supports. Do not include secrets, credentials, or real personal data in the eval file.

4. **Write checks, cheapest first.** For each case, record the expected properties rather than an exact expected output when many answers are acceptable. Use deterministic checks wherever they capture the requirement:
   - the output parses and matches the required schema or format;
   - required fields or facts are present, or an extracted value equals the expected value;
   - forbidden content is absent, such as a leaked internal name or a made-up field;
   - length is within bounds;
   - a tool is called with the expected arguments, when the feature uses tools.

   Add a model-graded rubric only for qualities that deterministic checks cannot judge, such as tone or completeness. A rubric has at most three criteria, each with a pass example and a fail example. Calibrate it on about 10 cases the user has labeled by hand, and report how often the grader and the user agreed. Do not let the model grade its own output without that calibration.

5. **Create the eval file and the runner.** Use the project's language and test runner if it has one. Put the cases in a JSON Lines file, one case per line, with an `id`, the `input`, the checks to apply, and a note on why the case exists. Put the runner beside it. It should:
   - load the cases and call the feature's real function;
   - apply each check and report a pass rate per check and the ids of failing cases;
   - save results as JSON with a timestamp, the model name, and the prompt version;
   - read its API key from the environment and never print it;
   - accept a `--limit` argument so a first run can be small.

   Default the file locations to `evals/llm/<feature-name>.jsonl` and `evals/llm/run_<feature-name>`, and confirm them with the user before creating anything. Keep dependencies to a minimum.

6. **Confirm the budget, then run a small sample.** Before any live call, estimate the cost from the number of cases, the expected input and output size, and the model's published price, and show the estimate to the user. Run the first pass with `--limit 5`, check that the output and the failure messages make sense, and fix the runner or the checks if they do not. Only then ask for approval to run the full set.

7. **Record a baseline and define the comparison.** Save the first full run as the baseline. Propose a regression rule, such as "no deterministic check drops by more than 5 points, and no case that passed before fails now," and ask the user to confirm or change it. Do not pick thresholds without the user.

8. **Keep the normal test suite offline.** Live evals call a paid API, so they should be opt-in, for example behind an environment variable or a separate command. Unit tests for the parser and checks should use recorded responses, so they run without network access or a key. Do not add live evals to CI unless the user asks, and never store the key in CI configuration from this skill.

9. **Report honestly.** Give the sample size, the checks, the pass rate for each check, the failing case ids with redacted inputs, the model and prompt version, the cost of the run, and the limitations. A set of 20 to 50 cases shows direction, not statistical proof. Do not say that the feature is "good" or "accurate" from the eval set alone.

10. **Do not change the feature.** Report the failures and suggest what to try, but do not edit the production prompt, model setting, or application code unless the user asks. Do not commit, push, or deploy the eval files unless asked.

## Examples

**User:** "Our invoice extractor sometimes returns the wrong total. How do I know if my prompt change fixed it?"

**Agent:** Asks for three correct extractions and the most costly error. Finds the function that builds the prompt and parses the response. Collects 30 synthetic invoices that include a missing total, two currencies, and a multi-page layout. Writes deterministic checks: the total equals the expected value, the currency is one of the allowed codes, and the output parses. Creates `evals/llm/invoice-extractor.jsonl` and a runner, runs five cases after confirming the cost, and reports that the total check passed four of five with the failing invoice's id. Proposes a baseline and a regression rule for the user to confirm.

**User:** "Make a quality check for our support reply summaries. They should be short, accurate, and polite."

**Agent:** Explains that "accurate" needs the source ticket to check against, and asks for 20 tickets with the summaries the team accepted. Uses deterministic checks for length and for required fields, and a three-criteria rubric for politeness and accuracy with pass and fail examples. Asks the user to label 10 cases by hand before the rubric is trusted, and reports the agreement rate after calibration.

**User:** "Check that my agent doesn't leak secrets in its answers."

**Agent:** Does not build an eval for this. Explains that the question is about security, and suggests `security-agent-guard` for the review and `security-access-regression` for access tests.
