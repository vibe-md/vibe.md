# vibe.md

**Everything around the code.**

[![Validate skills](https://github.com/vibe-md/vibe.md/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/vibe-md/vibe.md/actions/workflows/validate-skills.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

AI can write code. Great software takes more than code.

vibe.md is an open-source collection of reusable skills for AI coding agents. Skills give your agent proven workflows for everything around the code: Git, collaboration, testing, documentation, code quality, deployment, and the processes that turn generated code into shipped software.

> **Available now:** Gitly, twelve Git and project-workflow skills, plus a shared router. See [Available Skills](#available-skills).

## Contents

- [Why vibe.md?](#why-vibemd)
- [What is vibe.md?](#what-is-vibemd)
- [Skills vs. agents](#skills-vs-agents)
- [Quick start](#quick-start)
- [Supported coding agents](#supported-coding-agents)
- [Available Skills](#available-skills)
- [Repository structure](#repository-structure)
- [How it works](#how-it-works)
- [Installation guide](#installation-guide)
- [Creating a skill](#creating-a-skill)
- [Contributing](#contributing)
- [Skill quality standards](#skill-quality-standards)
- [Security](#security)
- [Updating and removing skills](#updating-and-removing-skills)
- [Frequently asked questions](#frequently-asked-questions)
- [Community](#community)
- [License](#license)

## Why vibe.md?

AI coding tools are remarkably good at producing code. Real-world software development asks for much more:

- **Workflows.** Branching, committing, rebasing, opening Pull Requests, and releasing, done the same way every time.
- **Maintainability.** Code that follows the project's conventions and stays readable months later.
- **Testing.** Knowing what to test, running the suite, and refusing to call work done while it fails.
- **Collaboration.** Clear commit messages, useful Pull Request descriptions, and reviews that teammates can act on.
- **Documentation.** READMEs, changelogs, and comments that keep up with the code.
- **Shipping.** Builds, deployments, and the checks that come before them.

Out of the box, an agent improvises each of these from scratch, and the result varies from one session to the next. A **skill** captures a workflow once, as plain instructions plus optional helper files, so any compatible agent can follow it reliably. vibe.md is where the community builds and shares those skills.

## What is vibe.md?

vibe.md is a curated, community-maintained library of [Agent Skills](https://agentskills.io/specification):

- **Community-maintained.** Skills are contributed and improved through Pull Requests, reviewed by maintainers, and validated automatically.
- **Portable.** Every skill uses the open Agent Skills format (a directory with a `SKILL.md` file), which Claude Code, Codex, Cursor, Gemini CLI, and GitHub Copilot all understand.
- **Individually installable.** Install only the skills you want, into only the projects that need them. There is nothing to install globally.
- **Reusable.** A skill is just files. Commit it to your project and your whole team, and every agent they use, gets the same workflow.
- **Open source.** Everything is MIT-licensed and developed in the open.

## Skills vs. agents

These terms are easy to mix up, so here is what they mean in this project:

| Term | What it is | Example |
| --- | --- | --- |
| **AI agent** | The program that does the work: it reads your request, plans, edits files, and runs commands. | Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot |
| **Agent skill** | A folder of instructions (and optional scripts, references, and assets) that teaches an agent *how* to do a specific task. A skill does nothing on its own. | A skill that explains how to write release notes |
| **Multiple skills in one agent** | One agent with several skills available. It loads whichever skill matches the current task. It is still one agent. | Your agent has a commit skill and a testing skill, and uses each when relevant |
| **Multi-agent system** | Several autonomous agents coordinating with each other. | An orchestrator delegating work to specialized sub-agents |

**vibe.md is a collection of skills, not a multi-agent framework.** Installing ten skills does not create ten agents. It gives the one agent you already use ten new playbooks to choose from. Think of the agent as a developer and skills as the team's runbooks: more runbooks make the developer more capable, not more numerous.

## Quick start

**1. See what is available.**

```bash
git clone https://github.com/vibe-md/vibe.md.git
cd vibe.md
bash scripts/install.sh --list
```

The catalog shows each skill and its group, including Gitly and the shared `vibe` router.

**2. Install Gitly into your project**, choosing your agent:

```bash
bash scripts/install.sh --group gitly --agent <agent> --project /path/to/your/project
```

`<agent>` is one of `claude-code`, `codex`, `cursor`, `gemini`, or `copilot`. Add `--dry-run` first to see exactly what will be written.

**3. Use it.** Follow the installer's reload instructions, then ask "Set up Gitly", "Save my progress", or "Is everything backed up?" All twelve skills are directly available to the agent. In Codex you can also invoke `$gitly-status` directly or `$vibe` to choose a workflow. Agents can select matching skills automatically. See [Supported coding agents](#supported-coding-agents) for each agent's details.

## Supported coding agents

vibe.md supports five agents. Each one reads skills from its own project-level directory; the installer copies the skill into the directory for the agent you choose.

| Agent | `--agent` | Project directory used by the installer | Personal directory (manual install) | Also reads in a project |
| --- | --- | --- | --- | --- |
| [Claude Code](https://code.claude.com/docs/en/skills) | `claude-code` | `.claude/skills/<skill>/` | `~/.claude/skills/<skill>/` | — |
| [Codex](https://developers.openai.com/codex/skills) | `codex` | `.agents/skills/<skill>/` | `~/.agents/skills/<skill>/` | `.agents/skills/` in every directory from the working directory up to the repository root |
| [Cursor](https://cursor.com/docs/skills) | `cursor` | `.cursor/skills/<skill>/` | `~/.cursor/skills/<skill>/` | `.agents/skills/`, plus `.claude/skills/` and `.codex/skills/` for compatibility |
| [Gemini CLI](https://geminicli.com/docs/cli/skills/) | `gemini` | `.gemini/skills/<skill>/` | `~/.gemini/skills/<skill>/` | `.agents/skills/` (takes precedence over `.gemini/skills/`) |
| [GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) | `copilot` | `.github/skills/<skill>/` | `~/.copilot/skills/<skill>/` | `.claude/skills/`, `.agents/skills/` |

### How each agent discovers and uses skills

**Claude Code**
- *Discovery:* only each skill's name and description stay in context; the full `SKILL.md` loads when the skill is used.
- *Invocation:* automatically when your request matches the description, or directly with `/<skill-name>`.
- *Reload:* Claude Code watches `.claude/skills/` and picks up new skills during a session. If the `.claude/skills/` directory did not exist when the session started, run `/reload-skills` or restart.

**Codex**
- *Discovery:* Codex lists skills by name and description and loads `SKILL.md` only when it selects a skill.
- *Invocation:* explicitly with `$<skill-name>` or through `/skills`, or implicitly when the task matches the description.
- *Reload:* changes are usually detected automatically; restart Codex if a new skill does not appear.

**Cursor**
- *Discovery:* Cursor finds skills when it starts, including in nested directories of the project.
- *Invocation:* automatically when relevant, or by typing `/` in Agent chat and choosing the skill.
- *Reload:* Cursor's documentation does not describe live reloading; restart Cursor if a newly installed skill is not listed.

**Gemini CLI**
- *Discovery:* at session start, Gemini CLI adds each enabled skill's name and description to its context. `/skills list` shows what it found.
- *Invocation:* when a task matches, the model calls its `activate_skill` tool and **asks for your consent** before loading the skill.
- *Reload:* run `/skills reload`, or start a new session.
- *Note:* Google has announced that Antigravity CLI replaces Gemini CLI for individual and free-tier users, while enterprise and API-key users keep access. The paths above follow the current Gemini CLI documentation. We have not verified Antigravity CLI's skill locations, so it is not listed as supported.

**GitHub Copilot**
- *Discovery:* Copilot chooses a skill based on your prompt and the skill's description, then injects its `SKILL.md` into context.
- *Where it works:* Copilot cloud agent, Copilot code review, Copilot CLI, the Copilot app, and agent mode in VS Code.
- *Note:* Copilot cloud agent and code review run on GitHub, so commit and push `.github/skills/` for them to see the skill.

Activation always remains the agent's decision. A skill with a precise description is chosen more reliably, but no agent guarantees that a skill will be used for every matching request.

### One copy for several agents: `.agents/skills/`

The `.agents/skills/` directory is a shared convention. It is Codex's native location and is also read by Cursor, Gemini CLI, and GitHub Copilot. Installing with `--agent codex` therefore makes a skill available to all four. Claude Code does not read `.agents/skills/`; use `--agent claude-code` for it.

Avoid installing the same skill into several directories that one agent reads. Gemini CLI resolves the duplicate by precedence, but other agents may list the skill twice.

## Available Skills

| Group | Skills | Install |
| --- | --- | --- |
| [Gitly](skills/gitly/README.md) | 12 workflows for setup, status, checks, saving, history, comparison, recovery, branches, merging, GitHub connection, sync, and preferences | `--group gitly` |
| Shared | `vibe`, the router for installed groups | Included automatically |

Install one workflow with `--skill gitly-status` instead of installing the group.
Each installation includes the shared router. Group members are installed as flat,
directly discoverable skill directories, with shared group documents installed once:

```text
.agents/skills/
├── vibe/SKILL.md
├── gitly/GITLY.md              # shared contract; LICENSE and docs are here too
├── gitly-status/SKILL.md
├── gitly-save/SKILL.md
└── ...
```

The router uses the installed skills' descriptions and group metadata, so future
groups need no changes to its instructions. Skills use `SKILL.md`; `AGENTS.md` is
project guidance, not a skill entrypoint. The installer does not edit project
guidance. Automatic activation remains the host agent's decision.

Have a workflow your agent should know? [Contribute a skill](CONTRIBUTING.md) or [propose one](https://github.com/vibe-md/vibe.md/issues/new?template=skill_proposal.yml). New skills show up in `install.sh --list` as soon as they are merged.

## Repository structure

```text
vibe.md/
├── skills/                        # The skill collection (the single source of truth)
│   ├── README.md
│   ├── _shared/
│   │   └── vibe/SKILL.md          # Router installed with every selection
│   ├── gitly/                    # Installable group
│   │   ├── README.md
│   │   ├── GITLY.md             # Shared operating contract
│   │   ├── LICENSE
│   │   └── gitly-status/         # One directory per independently usable skill
│   │       └── SKILL.md        # References ../GITLY.md in source
│   └── <skill-name>/             # Standalone skills are also supported
│       ├── SKILL.md               # Required: frontmatter + instructions
│       ├── scripts/               # Optional: executable helpers
│       ├── references/            # Optional: documentation loaded on demand
│       └── assets/                # Optional: templates, examples, data
├── scripts/
│   ├── install.sh                 # Universal installer
│   └── validate-skills.py         # Skill validator
├── tests/
│   ├── fixtures/                  # Valid and invalid sample skills (never published)
│   ├── test_installer.py
│   └── test_validator.py
├── .github/
│   ├── workflows/validate-skills.yml
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
└── requirements-dev.txt           # Python dependency for the validator and tests
```

| Part | Purpose |
| --- | --- |
| `skills/` | Standalone skills and one level of groups; each leaf skill has its own `SKILL.md`. |
| `skills/_shared/` | Common skills installed with every selection, including the `vibe` router. |
| `SKILL.md` | The skill itself: YAML frontmatter (`name`, `description`, optional fields) followed by Markdown instructions. |
| `scripts/` (in a skill) | Helper programs the agent may run while using the skill. Never run by the installer. |
| `references/` (in a skill) | Longer documentation the agent reads only when needed, keeping `SKILL.md` small. |
| `assets/` (in a skill) | Static files such as templates, examples, or schemas. |
| `scripts/install.sh` | Installs a group or individual skill with shared skills, flattening the directories for discovery. |
| `scripts/validate-skills.py` | Checks every skill's structure and metadata. Used locally and in CI. |
| `tests/` | Automated tests for the validator and installer, using isolated fixtures and temporary directories. |
| `.github/workflows/` | CI that validates skills and runs the tests on every Pull Request and every push to `main`. |

## How it works

1. **A contributor adds a skill** by opening a Pull Request that creates `skills/<skill-name>/` or `skills/<group>/<skill-name>/`.
2. **CI validates it.** GitHub Actions discovers the new directory automatically, validates it, and runs the test suite on Linux and macOS. No configuration change is needed for new skills.
3. **Maintainers review it** for usefulness, clarity, safety, and licensing.
4. **The skill is merged** into `main` and becomes part of the collection.
5. **A developer installs it** with `install.sh --skill <name>` or `--group <group>`, which installs selected skills, shared group documents, and the router into their agent's discovery directory.
6. **The agent discovers it.** Claude Code and Codex usually pick up new skills during a session; Cursor may need a restart and Gemini CLI a `/skills reload`; Copilot cloud agent sees the skill once it is committed and pushed. See [Supported coding agents](#supported-coding-agents).
7. **The agent loads it when appropriate**, either because the request matches the skill's description or because you invoked it explicitly. Gemini CLI asks for your consent first.

## Installation guide

### Prerequisites

- macOS or Linux with Bash 3.2 or later and standard tools (`cp`, `diff`, `find`, `mktemp`). These are preinstalled on macOS and virtually every Linux distribution.
- `curl` and `tar` if you run the installer without cloning the repository.
- On Windows, use WSL or Git Bash. Windows is not covered by CI.

The installer has no other dependencies. It does not need Python, `sudo`, or network access when run from a clone.

### Installer reference

```text
bash scripts/install.sh --list
bash scripts/install.sh --skill <name> --agent <agent> [options]
bash scripts/install.sh --group <name> --agent <agent> [options]

  --skill <name>        One skill to install (see --list)
  --group <name>        All skills in a group (see --list)
  --agent <agent>       claude-code, codex, cursor, gemini, or copilot
  --project <dir>       Project to install into (default: current directory)
  --dry-run             Show what would happen without writing anything
  --force               Replace an existing, different copy of the skill
  --list                List the available skills
  --skills-dir <dir>    Use a local skills collection instead of the default
  --ref <ref>           Branch or tag to download when run remotely (default: main)
  -h, --help            Show help
```

### Project-level installation (recommended)

Clone the repository once, then install into any project:

```bash
git clone https://github.com/vibe-md/vibe.md.git ~/vibe.md

cd /path/to/your/project
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code --dry-run
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code
```

Without `--project`, the skill is installed into the current directory. Use `--project /path/to/project` to target a different one. Paths containing spaces are supported.

The installer:

- validates its arguments and rejects unknown agents and malformed skill names,
- copies skill resources, shared group documents and licenses, and the router; group documents are included even for a single workflow,
- resolves source group links for the flat installed layout,
- preflights every destination before writing, stages all selected skills, and restores earlier copies if a later move fails,
- refuses to write outside the target project, even through symbolic links,
- never runs any of the skill's scripts, never uses `sudo`, and never installs globally.

### Remote installation

You can run the installer without cloning. It downloads the repository archive for `main` (or the `--ref` you choose) to a temporary directory, installs the complete skill directory, and deletes the download.

The safer approach is to download the script, read it, then run it:

```bash
curl -fsSL -o vibe-install.sh https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh
less vibe-install.sh                          # review it
bash vibe-install.sh --list
bash vibe-install.sh --group gitly --agent codex --dry-run
bash vibe-install.sh --group gitly --agent codex
```

A one-line form is also supported. It runs code from the internet without letting you review it first, so use it only if you trust the source:

```bash
curl -fsSL https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh | bash -s -- --skill <skill-name> --agent codex
```

### Manual installation

Use a prepared agent ZIP generated by `scripts/build-packages.py`. It contains
ready-to-use skills and all required group documents. Read its `INSTALL.md` first
and compare existing destinations before copying. To copy a reviewed ZIP manually:

```bash
mkdir -p /path/to/project/.claude/skills
cp -R gitly-install/skills/. /path/to/project/.claude/skills/
```

Do not copy a grouped workflow's source folder alone: source group links are
resolved by the installer and package builder, and shared documents must accompany
individual workflows too. Standalone self-contained skills can still be copied
as complete directories.

Replace `.claude/skills` with the directory for your agent from the [compatibility table](#supported-coding-agents).

### Selecting an agent

Pass the agent with `--agent`. To use one skill with several agents, either install it once per agent, or install it into the shared `.agents/skills/` directory with `--agent codex` (read by Codex, Cursor, Gemini CLI, and GitHub Copilot) and additionally with `--agent claude-code` for Claude Code.

### Handling existing skills

| Situation | Result |
| --- | --- |
| The skill is not installed yet | It is installed. |
| An identical copy is already installed | Nothing changes; the installer reports that it is up to date. |
| A different directory or file with the same name exists | The installer stops with an error and changes nothing. |
| Same as above, with `--force` | Conflicting selected skills are replaced. Back up local changes first. |

These checks cover all selected group members and shared skills before any write. Other installed skills and groups are never touched. Identical shared skills are reused when adding another group.

### Reloading the agent

After installing, the installer prints the next step for your agent. In short: Claude Code and Codex usually notice new skills automatically (`/reload-skills` in Claude Code if `.claude/skills/` was just created), Cursor may need a restart, Gemini CLI needs `/skills reload` or a new session, and Copilot cloud agent needs the skill committed and pushed.

### Installing globally

The installer only installs into projects, on purpose: a project-level skill is visible, reviewable, and can be committed for the whole team. If you want a skill in every project, copy it manually into your agent's personal directory from the [compatibility table](#supported-coding-agents), for example:

```bash
mkdir -p ~/.claude/skills
cp -R gitly-install/skills/. ~/.claude/skills/
```

## Creating a skill

A minimal skill is one file:

```text
skills/
└── commit-messages/
    └── SKILL.md
```

```markdown
---
name: commit-messages
description: Writes clear Git commit messages that follow the Conventional Commits format. Use when committing changes or when the user asks for a commit message.
---

# Commit Messages

## Purpose

Produce consistent, informative commit messages.

## When to Use

Use when the user asks you to commit, or to suggest a commit message. Do not use for merge commits.

## Instructions

1. Run `git diff --staged` and read the changes. If nothing is staged, ask the user what to include.
2. Pick a type: `feat`, `fix`, `docs`, `test`, `refactor`, or `chore`.
3. Write a summary line of at most 72 characters in the imperative mood.
4. Add a body explaining *why* the change was made when it is not obvious.
5. Show the message to the user before committing.

## Examples

Staged change: a fix for an off-by-one error in pagination.

    fix: show the last page of search results

    The page count was rounded down, hiding the final partial page.
```

The essentials:

- **Naming:** lowercase kebab-case, 1–64 characters, identical to the directory name, and unique in the collection.
- **Frontmatter:** must start on the first line with `---`. `name` and `description` are required; `license`, `compatibility`, and `metadata` are optional.
- **Description:** what the skill does and when to use it, in 20 to 1024 characters. This is what agents read to decide whether to load the skill.
- **Instructions:** concrete, numbered steps an agent can follow and a reviewer can verify.
- **Scripts:** put helpers in `scripts/` and explain in `SKILL.md` what they do and when to run them.
- **References:** move long documentation into `references/` and link to it with a relative path, for example `[style guide](references/style-guide.md)`.
- **Assets:** put templates and examples in `assets/`.
- **Testing:** run `python3 scripts/validate-skills.py`, then install the skill into a scratch project and try it with a real agent.

[CONTRIBUTING.md](CONTRIBUTING.md) has the full format reference and a larger example with references and assets.

## Contributing

New skills, new packages, improvements, and fixes are all welcome. Skills belong to **packages**: a package is a topic such as `gitly` or `security`, and it is a directory under `skills/` that holds related skills. Here is the full path from idea to published skill:

1. **Fork** [vibe-md/vibe.md](https://github.com/vibe-md/vibe.md) on GitHub.
2. **Clone** your fork: `git clone https://github.com/<your-username>/vibe.md.git`
3. **Create a branch:** `git checkout -b add-security-audit`
4. **Add a skill to a package:** `skills/<package>/<package>-<skill>/SKILL.md`. For a new package, also add `skills/<package>/README.md` (see [CONTRIBUTING.md](CONTRIBUTING.md#creating-a-new-package)).
5. **Add optional resources** in `scripts/`, `references/`, or `assets/`.
6. **Run validation and the tests:**

   ```bash
   python3 -m pip install -r requirements-dev.txt
   python3 scripts/validate-skills.py
   python3 -m unittest discover -s tests
   ```

7. **Open a Pull Request** against `main` and fill in the checklist.
8. **Automated checks** run on the Pull Request. Errors point to the exact file and line.
9. **A maintainer reviews it.** Only maintainers can merge to `main`, and only after the checks pass and at least one review is approved. Address feedback by pushing more commits.
10. **After the merge, publication is automatic:** the downloads and the package catalog are built and published as a release, and the website rebuilds from it. Your skill or package appears on [vibe-md.dev](https://www.vibe-md.dev) and in the installer without any further steps.

Adding a skill or a package only requires files inside `skills/`. You never need to touch the installer, the build script, CI, or the website. See [CONTRIBUTING.md](CONTRIBUTING.md) for the details and [docs/MAINTAINERS.md](docs/MAINTAINERS.md) for how maintainers review and publish.

## Skill quality standards

A good vibe.md skill has:

- **A clear purpose.** It solves one recurring problem well.
- **A precise description** that tells the agent both what the skill does and when to use it.
- **Actionable instructions:** concrete steps, commands, and checks rather than general advice.
- **Portability.** No hard-coded paths, usernames, or agent-specific features unless necessary and documented.
- **Minimal context.** A focused `SKILL.md` (under 500 lines), with detail in `references/`.
- **Safety.** Confirmation before destructive or irreversible actions; no hidden behavior.
- **Testability.** Steps that a reviewer can try and an agent can verify.
- **Documentation.** Bundled scripts are explained, and examples show realistic use.
- **Honest prerequisites.** Required tools, accounts, and network access are listed up front.
- **Proper attribution.** Third-party material is licensed for redistribution and credited.

Common anti-patterns:

- "Helps with Git"-style descriptions that never trigger, or trigger for everything.
- Pasting whole manuals into `SKILL.md`.
- Instructions that only work on the author's machine.
- Scripts that need `sudo`, change global configuration, or download and run remote code.
- Silent `git push --force`, `rm -rf`, or other destructive steps.
- Links outside the skill and its permitted shared group documents.

## Security

Skills are instructions that your agent acts on, and they can include scripts that your agent may run with your permissions. Treat them like any third-party code:

- **Inspect a skill before installing it.** Read `SKILL.md` and every bundled script. `--dry-run` lists every file that will be copied.
- **Prefer a reviewed local clone** over piping a remote script into your shell.
- **Keep your agent's permission prompts on** for shell commands, and be wary of skills that pre-approve tools.
- **Re-review on update.**

Every skill in vibe.md is validated automatically and reviewed by maintainers before it is merged, and the installer only copies files. These measures reduce risk but cannot remove it.

To report a vulnerability or an unsafe skill, use GitHub's private vulnerability reporting as described in [SECURITY.md](SECURITY.md). Please do not open a public issue.

## Updating and removing skills

Every installation records which files it installed, with their checksums, in a
small receipt beside your agent's skills directory (for example
`.claude/.vibe-md/gitly.receipt`). Updates and removal use it to touch only files
that still match what was installed, and never files you created or edited.

**Update** by running the same install command again, with a newer collection:

```bash
git -C ~/vibe.md pull
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code --dry-run   # preview
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code
```

A skill you have not modified is updated in place. If you edited a skill, or a
directory of the same name exists that vibe.md did not install, the installer stops
and changes nothing. Pass `--force` only when you want to replace such a copy; that
discards your edits, so copy them elsewhere first. If your installed copy is
already identical, nothing changes. Installations from before receipts existed are
adopted when you install again.

**Remove** a package or a single skill with `--uninstall`:

```bash
bash ~/vibe.md/scripts/install.sh --uninstall --group gitly --agent claude-code --dry-run   # preview
bash ~/vibe.md/scripts/install.sh --uninstall --group gitly --agent claude-code
bash ~/vibe.md/scripts/install.sh --uninstall --skill gitly-status --agent claude-code
```

Files you modified after installing are kept and listed. The shared `vibe` router is
kept while another package still uses it. For an installation without a receipt, only
copies that are still identical to the vibe.md source are removed.

Then reload or restart your agent if it does not notice the change on its own.

## Frequently asked questions

**What is an Agent Skill?**
A directory containing a `SKILL.md` file (YAML metadata plus Markdown instructions) and, optionally, scripts, references, and assets. It teaches an AI coding agent how to perform a specific task. The format is an [open specification](https://agentskills.io/specification) supported by many agents.

**How is it different from an agent?**
An agent is the program that acts: it reads, plans, edits, and runs commands. A skill is knowledge the agent can load. Skills never act on their own. See [Skills vs. agents](#skills-vs-agents).

**Can I install multiple skills?**
Yes. Install as many as you like; each lives in its own directory. Agents keep only short descriptions in context and load a full skill when it is relevant, so several skills do not overload your agent.

**Can one skill work with different coding agents?**
Yes. vibe.md skills use the shared Agent Skills format. Install the skill once per agent, or use the shared `.agents/skills/` directory. A skill that relies on agent-specific features says so in its `compatibility` field.

**Do I need to install all skills?**
No. Every skill is installed individually. Install only what you need.

**Can I create my own skill?**
Yes. See [Creating a skill](#creating-a-skill). You can keep it private in your own project or contribute it to vibe.md.

**How do I submit a skill?**
Open a Pull Request that adds `skills/<skill-name>/` or `skills/<group>/<skill-name>/`. CI validates it automatically and a maintainer reviews it. See [CONTRIBUTING.md](CONTRIBUTING.md).

**Can I use skills without the installer?**
Yes. Copy the skill's directory into your agent's skills directory. See [Manual installation](#manual-installation).

**Can I install skills globally?**
Not with the installer, which only installs into projects. You can copy a skill manually into your agent's personal directory, such as `~/.claude/skills/`. See [Installing globally](#installing-globally).

**Does installing a skill modify my source code?**
No. The installer creates the selected skills, shared group documents, and router inside your agent's skills folder (for example `.claude/skills/<skill-name>/`). It does not touch your source files or agent settings, and it does not run any scripts. What the agent does once it uses a skill depends on the skill and on what you ask it to do.

**Is vibe.md free?**
Yes. vibe.md is free and open source under the MIT License. Your coding agent may have its own costs.

**How can I contribute?**
Add a skill, improve an existing one, fix a bug, improve the documentation, or report problems. Start with [CONTRIBUTING.md](CONTRIBUTING.md).

## Community

vibe.md grows through its contributors. You can help by:

- **Contributing skills** for the workflows you rely on.
- **Opening Pull Requests** to improve skills, tooling, and documentation.
- **Reporting bugs** with a [bug report](https://github.com/vibe-md/vibe.md/issues/new?template=bug_report.yml).
- **Requesting features** with a [feature request](https://github.com/vibe-md/vibe.md/issues/new?template=feature_request.yml).
- **Proposing skills** with a [new skill proposal](https://github.com/vibe-md/vibe.md/issues/new?template=skill_proposal.yml).
- **Sharing feedback** in [issues](https://github.com/vibe-md/vibe.md/issues) about what works and what does not.

Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) in all project spaces.

## License

vibe.md is released under the [MIT License](LICENSE). Individual skills may declare a different license in their `license` field; when they do, that license applies to the skill.
