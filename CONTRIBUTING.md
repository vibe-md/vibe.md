# Contributing to vibe.md

Thank you for helping build vibe.md. This guide covers everything you need to add a new skill, improve an existing one, or work on the tooling around them.

**The short version:** vibe.md is a collection of **packages**. A package is a topic (for example `gitly` or `security`) that groups related skills. A skill is one directory containing a `SKILL.md` file, inside its package: `skills/<package>/<package>-<skill>/SKILL.md`. Add a skill or a whole package, run the validator, and open a Pull Request from your fork. A maintainer reviews and merges it, and everything after the merge (packaging, the catalog, the website) happens automatically. You never need to change the installer, the validator, the build script, the website, or CI to add a skill or a package.

| I want to... | Do this |
| --- | --- |
| Improve an existing skill | Edit its `SKILL.md` and open a Pull Request. |
| Add a skill to an existing package | Add `skills/<package>/<package>-<skill>/SKILL.md`. See [Adding a skill](#adding-a-skill). |
| Add a new package | Add `skills/<package>/README.md` and at least one skill. See [Creating a new package](#creating-a-new-package). |
| Find out what happens after my PR | See [Review and publication](#review-and-publication). |

## Contents

- [Project philosophy](#project-philosophy)
- [Code of Conduct](#code-of-conduct)
- [Getting started](#getting-started)
- [Repository architecture](#repository-architecture)
- [Adding a skill](#adding-a-skill)
- [The SKILL.md format](#the-skillmd-format)
- [Optional resources](#optional-resources)
- [A complete example](#a-complete-example)
- [Validating and testing](#validating-and-testing)
- [Pull Request workflow](#pull-request-workflow)
- [Review and publication](#review-and-publication)
- [Review criteria](#review-criteria)
- [Security requirements](#security-requirements)
- [Licensing and attribution](#licensing-and-attribution)
- [Changing the tooling](#changing-the-tooling)
- [Reporting bugs and proposing skills](#reporting-bugs-and-proposing-skills)

## Project philosophy

- **Everything around the code.** Skills focus on the work that surrounds writing code: Git workflows, reviews, testing, documentation, releases, deployment, and team processes.
- **One skill, one job.** A skill should do one thing well. Two unrelated workflows belong in two skills.
- **Portable by default.** Skills follow the open [Agent Skills](https://agentskills.io/specification) format so they work across coding agents. Agent-specific behavior is the exception and must be documented.
- **Honest and safe.** A skill does exactly what it says, documents what it needs, and never surprises the user with destructive or hidden actions.
- **Simple infrastructure.** The tooling discovers skills by convention. Keep it that way: no registries, manifests, or per-skill configuration.

## Code of Conduct

Everyone taking part in vibe.md is expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md). Be kind, assume good intent, and keep feedback about the work.

## Getting started

### Requirements

| Tool | Needed for | Version |
| --- | --- | --- |
| Git | Everything | Any recent version |
| Bash | Running the installer | 3.2 or later (the macOS default works) |
| Python | Validator and tests | 3.9 or later |
| PyYAML | Validator | Pinned in `requirements-dev.txt` |
| ShellCheck | Linting the installer (optional locally, enforced in CI) | Any recent version |

On Windows, use WSL or Git Bash.

### Set up your copy

```bash
# 1. Fork https://github.com/vibe-md/vibe.md on GitHub, then clone your fork:
git clone https://github.com/<your-username>/vibe.md.git
cd vibe.md

# 2. Install the development dependency (a virtual environment is recommended):
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-dev.txt

# 3. Make sure everything passes before you change anything:
python3 scripts/validate-skills.py
python3 -m unittest discover -s tests
```

## Repository architecture

```text
vibe.md/
├── skills/                    # Standalone skills and one level of groups
│   ├── README.md
│   ├── _shared/vibe/SKILL.md   # Router included in every installation
│   └── gitly/<skill>/SKILL.md  # Independently usable group members
├── scripts/
│   ├── install.sh             # Installer: install, update, uninstall (bash, no dependencies)
│   ├── validate-skills.py     # Validator used locally and in CI
│   └── build-packages.py      # Builds ZIP downloads and catalog.json for every package
├── evals/                     # Natural-language scenarios for checking skill selection
├── tests/                     # Validator, installer, lifecycle, packaging, and catalog tests
└── .github/
    ├── workflows/validate-skills.yml   # Runs on every Pull Request
    ├── workflows/publish.yml           # Runs only after a merge to main
    ├── CODEOWNERS                      # Who must review which files
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE.md
```

Key rules:

1. `skills/` is the single source of truth. Each skill exists exactly once, there.
2. A skill has `SKILL.md`; a group contains skill directories one level down and has no `SKILL.md` of its own. Group names use lowercase kebab-case. `skills/_shared/` is reserved for common skills installed with every selection.
3. Skills are discovered automatically by the installer, validator, and CI. Names must be unique across standalone skills, all groups, and shared skills because installation flattens them into one directory.
4. Agent directories such as `.claude/skills/` are *installation destinations*, not sources. Never commit skills there.
5. Test fixtures live in `tests/fixtures/` and never appear in the public catalog.

## Adding a skill

1. **Check for overlap.** Search the [existing skills](skills/) and [open Pull Requests](https://github.com/vibe-md/vibe.md/pulls). Improving an existing skill is often better than adding a near-duplicate.
2. **Pick a name.** Lowercase letters, digits, and single hyphens, up to 64 characters, starting with the package name, for example `gitly-branches` or `security-audit`. Installation puts every package's skills into one agent directory, so the prefix keeps names unique (the validator warns when it is missing). Prefer clear, descriptive names over clever ones.
3. **Create the directory** `skills/<package>/<package>-<skill>/` and add `SKILL.md`. Even a single skill belongs in a package: create one, as described below. (The installer still supports a standalone `skills/<skill-name>/` for local use, but standalone skills are not published on the website.)
4. **Add optional resources** (`scripts/`, `references/`, `assets/`) only if the skill needs them.
5. **Validate and test** as described below.
6. **Open a Pull Request.**

A skill contribution should stay inside its standalone skill or group directory. If you think the tooling needs to change to support your skill, open an issue first so we can keep the infrastructure generic.

### Creating a new package

A package is a directory under `skills/` that holds skills. Packages are discovered
automatically, so a new package never needs a change to the installer, the build
script, CI, or the website. Create:

```text
skills/security/
├── README.md                  # optional frontmatter below, then the documentation
├── LICENSE                    # optional, shared by the package
└── security-audit/SKILL.md    # at least one skill
```

`README.md` may start with this frontmatter. Every field is optional, and anything
omitted is derived (the title from the directory name, the summary from the first
paragraph, the skills from the directory):

```yaml
---
title: Security
summary: One sentence that says what the package helps with.
category: Security          # Version Control, Testing, Debugging, Deployment, Documentation, Security, or Productivity
maintainers: [your-github-username]
---
```

The website, the downloads, and the installer all read this information from the
source, so there is nothing else to register. Add yourself under `maintainers` and
to `.github/CODEOWNERS` if you want to review future changes to the package.

### Adding a group (technical details)

Create `skills/<group>/<skill-name>/SKILL.md` for each workflow. Each workflow
may use resources inside its own directory, or top-level Markdown documents and
`LICENSE` shared by its group. Link shared files as `../CONTRACT.md` or `../LICENSE`.
The installer and ZIP builder include them once in `<agent-skills>/<group>/` and
resolve those links in installed skills. Individual installation also includes
these group resources. Keep skill names globally unique and distinct from group
resources directory names. Links to sibling workflows or outside the group remain
invalid.

Include this metadata for the shared router, alongside the usual frontmatter:

```yaml
metadata:
  collection: vibe.md
  group: your-group
```

The installer discovers the group automatically. `--group your-group` installs
all its members alongside common skills from `_shared/`; `--skill your-skill`
installs one member with the same common skills. No group registry, router table,
or installer edit is required. Adding a second group must preserve earlier skills
and reuse identical common skills. The router reads installed skill descriptions,
then loads only the selected skill. Test both group and individual installation.

## The SKILL.md format

`SKILL.md` has two parts: YAML frontmatter, then Markdown instructions.

### Frontmatter

The file must start with `---` on the very first line.

| Field | Required | Rules |
| --- | --- | --- |
| `name` | Yes | 1–64 characters. Lowercase `a-z`, `0-9` and hyphens. No leading, trailing, or consecutive hyphens. Must match the directory name exactly. Must be unique. |
| `description` | Yes | 20–1024 characters. Say what the skill does **and** when an agent should use it. |
| `license` | No | A license name such as `MIT`, or the name of a bundled license file. |
| `compatibility` | No | Up to 500 characters. Environment requirements, for example `Requires git and the GitHub CLI (gh)`. |
| `metadata` | No | A mapping for extra information such as `author` or `version`. |
| `allowed-tools` | No | Space-separated list of pre-approved tools. Experimental; support varies by agent. Avoid pre-approving shell access. |

Agents may support additional fields (for example Claude Code's `disable-model-invocation`). The validator allows them, but every extra field makes a skill less portable, so use them only when necessary and explain why in your Pull Request.

### Writing the description

Agents usually see only the `name` and `description` until they decide to load a skill. The description is how your skill gets chosen, so make it specific:

```yaml
# Good: what it does, when to use it, and the words users actually say
description: Writes release notes from merged pull requests and commit history. Use when preparing a release, drafting a changelog entry, or when the user asks what changed since the last tag.

# Too vague: the agent cannot tell when this applies
description: Helps with releases.
```

### Writing the instructions

Use this structure as a starting point:

```markdown
# Skill Title

## Purpose
What problem the skill solves.

## When to Use
The situations where the agent should apply it, and when it should not.

## Prerequisites
Tools, accounts, permissions, or network access required.

## Instructions
Numbered, actionable steps. Say what to check before acting and what to confirm with the user.

## Examples
One or two realistic requests and what the agent should do.
```

Guidelines:

- **Be actionable.** Write steps an agent can follow and a reviewer can verify. "Run `git status` and stop if the working tree is dirty" beats "make sure things are clean".
- **Be concise.** The whole `SKILL.md` is loaded into the agent's context when the skill activates. Keep it under 500 lines (the validator warns above that) and move detail into `references/`.
- **Be portable.** Do not assume a specific agent, operating system, or file layout unless you must. If you must, say so in `compatibility`.
- **Use relative paths** for files inside the skill, such as `references/checklist.md`. Grouped skills may also link to top-level group Markdown documents or `LICENSE` using `../filename`; installation includes these dependencies automatically. Other links outside the skill are rejected.
- **Ask before destructive actions.** Tell the agent to confirm with the user before deleting, force-pushing, publishing, or spending money.

## Optional resources

| Directory | Contents | Notes |
| --- | --- | --- |
| `scripts/` | Executable helpers the agent can run | Self-contained, documented dependencies, helpful error messages. Explain in `SKILL.md` what each script does. |
| `references/` | Extra documentation loaded on demand | Keep each file focused; link to it from `SKILL.md`. |
| `assets/` | Templates, examples, schemas, data | Static files only. |

None of these directories is required. Other file names are allowed, but these conventions keep skills easy to review. Symbolic links are not allowed anywhere in a skill.

The validator checks every relative Markdown link in `SKILL.md` (for example `[checklist](references/checklist.md)`): the target must exist inside the skill, or be a top-level document or `LICENSE` in its group. Links inside code blocks and inline code are not checked.

## A complete example

```text
skills/
└── release-notes/
    ├── SKILL.md
    ├── references/
    │   └── style-guide.md
    └── assets/
        └── template.md
```

`skills/release-notes/SKILL.md`:

````markdown
---
name: release-notes
description: Writes release notes from merged pull requests and commit history. Use when preparing a release, drafting a changelog entry, or when the user asks what changed since the last tag.
license: MIT
compatibility: Requires git. Uses the GitHub CLI (gh) when available.
---

# Release Notes

## Purpose

Turn the history since the last release into clear, user-facing release notes.

## When to Use

- The user is preparing a release or a changelog entry.
- The user asks what changed since a tag, date, or commit.

Do not use this skill to create tags or publish releases.

## Prerequisites

- A Git repository with at least one previous tag.
- Optional: the GitHub CLI (`gh`), authenticated, to read pull request titles.

## Instructions

1. Find the latest tag with `git describe --tags --abbrev=0`. If there is none, ask the user which commit to start from.
2. List the changes with `git log <tag>..HEAD --oneline --no-merges`.
3. If `gh` is available, read merged pull request titles for richer descriptions.
4. Group changes into Features, Fixes, and Other, following [the style guide](references/style-guide.md).
5. Fill in [the template](assets/template.md) and show the draft to the user.
6. Do not commit, tag, or publish anything unless the user asks.

## Examples

**User:** "Write release notes for everything since v1.4.0."

**Agent:** Runs `git log v1.4.0..HEAD --oneline --no-merges`, groups the 23 commits, and presents a draft under "Features", "Fixes", and "Other" for review.
````

## Validating and testing

Run both commands from the repository root before you open a Pull Request:

```bash
python3 scripts/validate-skills.py          # validates every skill in skills/
python3 -m unittest discover -s tests        # runs the validator, installer, packaging, and catalog tests
python3 scripts/build-packages.py --all --output-dir /tmp/vibe-md-build   # builds the downloads and catalog
python3 scripts/build-packages.py --verify /tmp/vibe-md-build             # checks them against your source
```

The validator checks that:

- every skill directory contains `SKILL.md` (exact spelling),
- the frontmatter exists and is valid YAML,
- `name` and `description` are present and well-formed,
- names are lowercase kebab-case, unique, and match their directory,
- relative links resolve to local files or the permitted shared group documents,
- the skill contains no symbolic links and has instructions after the frontmatter,
- no file is larger than 1 MiB, binary files appear only under `assets/`, and text is UTF-8,
- no file contains an obvious secret (private keys and common token formats),
- the package `README.md` frontmatter, if present, uses only the documented fields.

It also **warns** (without failing) about bundled `scripts/`, executable files, instructions that pipe a download into a shell, and skill names without the package prefix. Warnings tell the reviewer where to look closely.

Errors name the file and, where possible, the line, plus a hint on how to fix it. These checks catch honest mistakes. They do not replace a maintainer reading what your skill tells an agent to do.

### Test the skill with an agent

Validation proves the format is right, not that the skill is useful. Install it into a scratch project and try it with at least one agent:

```bash
mkdir -p /tmp/skill-playground
bash scripts/install.sh --skill <skill-name> --agent claude-code --project /tmp/skill-playground --dry-run
bash scripts/install.sh --skill <skill-name> --agent claude-code --project /tmp/skill-playground
```

Then open the agent in that project, check that the skill is discovered, and run a realistic request. Mention which agents you tested in your Pull Request.

## Pull Request workflow

1. Create a branch: `git checkout -b add-release-notes-skill`.
2. Commit your changes with a clear message, for example `Add release-notes skill`.
3. Push to your fork and open a Pull Request against `main`.
4. Fill in the Pull Request template checklist.
5. Wait for CI. The **Validate skills** workflow runs the validator, builds every package and the catalog, and runs the full test suite on Linux and macOS. If it fails, open the failed job; validation errors are also shown inline on the changed files. The first time you contribute, a maintainer has to approve the workflow run before it starts.
6. Respond to review feedback by pushing more commits to the same branch. New commits require a fresh approval.
7. A maintainer merges the Pull Request once CI passes and the review is approved. **Contributors cannot merge their own Pull Requests.**

Keep Pull Requests focused: one skill, or one improvement, per Pull Request.

## Review and publication

```text
Fork / branch → Pull Request → automated checks → maintainer review
   → maintainer merges → publish workflow → release → website rebuild → users can install
```

1. **Automated checks** (`validate-skills.yml`) run on your Pull Request with a read-only token and no secrets. They never publish anything.
2. **Maintainer review.** At least one maintainer must approve, and the checks must pass. Changes to `scripts/`, `.github/`, and `tests/` always need a maintainer, because they decide what everyone else's contributions are allowed to do. Bundled scripts get an extra look.
3. **Merge.** Only maintainers can merge to `main`.
4. **Publication is automatic after the merge.** The `publish.yml` workflow re-runs the checks on the merged commit, builds the ZIP downloads and `catalog.json` for every package, and publishes them as a GitHub Release. Nothing is published if any step fails.
5. **The website** reads that catalog when it builds. A deploy hook triggers a rebuild, so a new skill or package normally appears within a few minutes of the merge. Until then the website keeps showing the previous, consistent version.
6. **Users** install with the commands shown on the package page. Their installation records what it installed, so updating and removing it later is safe.

If something is slow or missing, see [docs/MAINTAINERS.md](docs/MAINTAINERS.md) for how maintainers check the publication status.

## Review criteria

Maintainers look at:

- **Purpose:** Does the skill solve a real, recurring problem? Is it distinct from existing skills?
- **Description:** Will an agent pick it at the right time, and not at the wrong time?
- **Instructions:** Are the steps clear, actionable, and verifiable? Are edge cases covered?
- **Safety:** Are destructive actions confirmed with the user? Do scripts do only what is documented?
- **Portability:** Does it avoid unnecessary agent- or platform-specific assumptions?
- **Size:** Is `SKILL.md` focused, with detail moved into `references/`?
- **Prerequisites:** Are required tools and access stated honestly?
- **Licensing:** Is all included material original or properly licensed and attributed?

### Common anti-patterns

- Vague descriptions such as "Helps with Git".
- Giant `SKILL.md` files that paste entire manuals into the agent's context.
- Instructions that only work in the author's environment (hard-coded paths, usernames, or URLs).
- Scripts that download and run remote code, need `sudo`, or change global configuration.
- Silent destructive steps: `git push --force`, `rm -rf`, or dropping data without asking.
- Links to files outside the skill directory.
- Copying third-party content without permission or attribution.

## Security requirements

All skills must follow the expectations in [SECURITY.md](SECURITY.md). In particular:

- No secrets, tokens, credentials, or personal data, ever.
- No obfuscated code, encoded payloads, or hidden network activity.
- No downloading and executing remote code at run time.
- Destructive operations must be explicit and confirmed with the user.

Pull Requests that violate these rules will be closed. Report suspected vulnerabilities privately, as described in [SECURITY.md](SECURITY.md), not in public issues.

## Licensing and attribution

- vibe.md is released under the [MIT License](LICENSE). By contributing, you agree that your contribution is licensed under the MIT License, unless the skill states a different license in its `license` field.
- You must have the right to submit everything you contribute.
- Third-party material (code, text, templates) must have a license that allows redistribution and must keep its copyright notice. Include the original license file inside the skill directory or as the group-level `LICENSE` and set the `license` field accordingly, for example `license: Apache-2.0. See LICENSE.txt`.
- Credit the original authors in `SKILL.md` or in `metadata`.
- Do not include material whose license you are unsure about. Ask in the Pull Request.

## Changing the tooling

Improvements to the installer, validator, tests, or CI are welcome. Please:

- Keep the tooling generic. Never add logic for a specific skill.
- Keep the installer dependency-free and compatible with bash 3.2.
- Add or update tests in `tests/` for every behavior change, using temporary directories. Tests must never write to a real agent configuration or require network access (network tests go behind `VIBE_MD_INTEGRATION=1`).
- Run `shellcheck scripts/install.sh` if you change the installer.

### Adding support for a new agent

Agent destinations are defined in one place, at the top of `scripts/install.sh`:

1. Add the agent id to `SUPPORTED_AGENTS`.
2. Add a case to `agent_skills_dir`, `agent_label`, and `agent_next_steps`.
3. Add the agent to `AGENT_DIRS` in `tests/test_installer.py`.
4. Document it in the "Supported coding agents" section of the README, with a link to the agent's official documentation.

Only add agents whose skill locations are documented officially.

## Reporting bugs and proposing skills

- **Bugs:** open a [bug report](https://github.com/vibe-md/vibe.md/issues/new?template=bug_report.yml) with the command you ran, the full output, and your environment.
- **Feature ideas:** open a [feature request](https://github.com/vibe-md/vibe.md/issues/new?template=feature_request.yml).
- **Skill ideas:** open a [new skill proposal](https://github.com/vibe-md/vibe.md/issues/new?template=skill_proposal.yml) if you want feedback first, or go straight to a Pull Request.
- **Security issues:** report privately, as described in [SECURITY.md](SECURITY.md).

Thank you for contributing!
