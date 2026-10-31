---
title: Gitly
summary: "Git and GitHub workflows for people who build with AI agents: save, compare, restore, branch, merge, and back up in everyday language."
categories: Version Control
maintainers: [NirGeron98, AdiBer1]
---

# Gitly

Twelve independently discoverable skills for Git, project checks, recovery, and
GitHub workflows, with everyday English and Hebrew examples.

## Install the group

From a vibe.md checkout:

```bash
bash scripts/install.sh --group gitly --agent codex --project /path/to/project --dry-run
bash scripts/install.sh --group gitly --agent codex --project /path/to/project
```

Use `claude-code`, `cursor`, `gemini`, or `copilot` for another agent. Installation
places the shared `vibe` router and all twelve `gitly-*` skill directories directly
in the chosen agent's skills directory. Each workflow has its own `SKILL.md`. The operating contract, license, and
group documentation are installed once in the adjacent `gitly/` directory. No project-level `AGENTS.md` or `.gitly/GITLY.md` is needed.

After the reload steps printed by the installer, say "Set up Gitly", "Save my
progress", or "Is everything backed up?" You can also select an individual skill
through your agent's skill UI, such as `$gitly-status` in Codex, or use `$vibe`
when you want the router to choose. Automatic activation remains the host agent's
decision.

To install only one workflow with the shared router:

```bash
bash scripts/install.sh --skill gitly-status --agent codex --project /path/to/project
```

## Included skills

| Skill | Purpose |
| --- | --- |
| `gitly-setup` | Prepare Git, local identity, and ignore rules |
| `gitly-status` | Explain saved, unsaved, online, and at-risk work |
| `gitly-check` | Investigate project health and run approved existing checks |
| `gitly-save` | Save reviewed changes as a local commit |
| `gitly-history` | Find previous versions |
| `gitly-compare` | Explain changes between versions |
| `gitly-restore` | Recover files or undo commits after explicit recovery intent |
| `gitly-branches` | Create and switch safe experiments |
| `gitly-merge` | Combine work without guessing through conflicts |
| `gitly-github-connect` | Authenticate, create a repository, or link a remote |
| `gitly-sync` | Fetch, fast-forward pull, or push without force |
| `gitly-settings` | Read or update project preferences |

## Requirements

Git is required for version workflows. GitHub connection and sync also require
GitHub CLI (`gh`), an appropriate account, and network access. Project checks use
the project's existing tools. Changes and checks follow the bundled contract's
approval rules; read-only status, history, and comparison need no approval.

Preferences stay in the project's `.gitly/config.md`, if present. Missing
preferences use defaults without creating a file. Installing skills does not
modify project configuration or run Gitly workflows.

Remove installed `gitly-*` directories and the shared `gitly/` documents directory to remove the group. Keep `vibe/` if other
groups use it, and keep project preferences if you want to retain them.

## Source

Gitly is maintained here as part of vibe.md. Installation, ZIP generation, tests,
and documentation use this repository; the former Gitly repository is retained
only as attribution. No sibling Gitly checkout is required.

The complete operating contract is maintained once in [GITLY.md](GITLY.md),
with one [LICENSE](LICENSE) for the group. Workflow source folders contain only
`SKILL.md` and reference `../GITLY.md`. No contract or license copies are maintained
inside the twelve workflows.

The installer keeps all workflows directly discoverable and copies group-level
Markdown documents and `LICENSE` once into `<agent-skills>/gitly/`. It resolves
source links such as `../GITLY.md` to `../gitly/GITLY.md` in installed workflows.
Even `--skill gitly-status` includes these common documents and the `vibe` router.
Do not copy a workflow source folder alone; use the installer or the prepared ZIP.

For example, a full Codex installation contains:

```text
.agents/skills/
├── vibe/SKILL.md
├── gitly/
│   ├── GITLY.md
│   ├── LICENSE
│   └── ...                 # shared documentation
├── gitly-status/SKILL.md
├── gitly-save/SKILL.md
└── ...
```

See [Architecture](ARCHITECTURE.md), [Compatibility](COMPATIBILITY.md),
[Security](SECURITY.md), and [Troubleshooting](TROUBLESHOOTING.md).

## Downloads and frontend

Generate the website's ZIPs and source-version manifest from this checkout:

```bash
python3 scripts/build-packages.py --group gitly --output-dir /path/to/vibe-website/public/downloads
```

This generates a package for each of the five supported agents. Each archive
contains the router, twelve Gitly workflows, one shared documents directory, a
file-hash inventory, and an
agent-specific `INSTALL.md`. End users download the ZIP, leave it in Downloads,
open their project in the matching agent, and ask it to read `gitly-install/INSTALL.md`
and install. They do not need Python, Node.js, or a cloned source repository.

The frontend lives in the separate vibe.md website repository, with Gitly at
`/skills/gitly`. Its terminal commands and ZIP downloads use the same source
commit from the generated manifest. Commit and push skill changes before building
the release packages so that source commit is available for terminal downloads.

## Provenance

Adapted from [NirGeron98/Gitly](https://github.com/NirGeron98/Gitly), commit
`fe33bbae13552ed8973c6949b1d21e1ce2b746c9`. Workflow instructions are preserved,
with their shared-contract paths changed to local relative links and attribution,
group, and license metadata added. The shared contract is unchanged and is
automatically included when installing a group or a single workflow. This contribution
uses vibe.md's [MIT license](LICENSE).

Gitly is agent guidance, not an executable security boundary.
