# Skill selection scenarios

`scenarios.json` lists natural-language requests and which installed skill an agent
should pick for each. It covers clear requests, ambiguous ones, requests in Hebrew,
and requests that must **not** select any skill.

## What this does and does not prove

A skill directory existing, and its description reading well, does **not** prove an
agent will select it. These scenarios are inputs for checking that against a real
agent. The unit test (`tests/test_evals.py`) only checks that the scenario file is
well-formed and that every skill it names exists. It does not run a model.

Keep four things separate when you evaluate:

| Layer | Question | How to check |
| --- | --- | --- |
| Discovery | Does the agent list the installed skills? | Install the package into a scratch project; use the agent's skill list (`/skills`, `$`, or its skill picker). |
| Selection | Given the prompt, does it choose the expected skill? | Send the prompt and record which skill the agent says it uses. |
| Activation | Does it then read that skill's full `SKILL.md`? | Check the agent's tool or transcript output for the skill being loaded. |
| Execution | Are the steps it takes correct and safe? | Use a throwaway Git repository and compare against the skill's own rules. |

## Running the scenarios by hand

1. Install the package into an empty scratch project, for example `bash scripts/install.sh --group gitly --agent claude-code --project /tmp/vibe-eval`.
2. Start the agent in that project and send each `prompt`.
3. For `positive` scenarios the chosen skill must be in `expected`. For `ambiguous` ones, choosing any listed skill or asking a focused question is acceptable (see `notes`). For `negative` ones no vibe.md skill should be loaded.
4. Record the agent and version, and report mismatches as an issue with the prompt and the skill the agent chose. A recurring mismatch usually means two descriptions overlap and one of them needs a clearer "Use when / do not use when".

Model behavior changes between versions and runs. Treat a single pass or fail as a
data point, and repeat important scenarios.

## Adding scenarios

Add an entry when you add or change a skill description. Use a real request in the
words a user would use, not the skill's own name. Add a `negative` scenario for any
word your skill shares with ordinary coding work.
