# Skills

This directory is the canonical home of vibe.md skills and skill groups:

```text
skills/
├── _shared/
│   └── vibe/SKILL.md    # general router, included in every installation
├── gitly/
│   ├── README.md
│   ├── gitly-status/SKILL.md
│   └── gitly-save/SKILL.md
└── <skill-name>/        # standalone skills remain supported
    ├── SKILL.md        # required: YAML frontmatter + instructions
    ├── scripts/        # optional: helper scripts the agent may run
    ├── references/     # optional: extra documentation loaded on demand
    └── assets/         # optional: templates, examples, data files
```

Gitly contains independently usable skills. Install the group with:

```bash
bash scripts/install.sh --group gitly --agent codex --project /path/to/project
```

This installs the `vibe` router and the `gitly-*` directories directly into
`.agents/skills/`. Each workflow has its own `SKILL.md`; the contract, license, and documentation
are shared once in `.agents/skills/gitly/`, including single-workflow installs.
Use `--skill gitly-status` for just one workflow plus the router. Replace `codex`
with your agent's name to use its discovery directory.

The router uses the installed skill catalog and each skill's description, so
future groups work without editing a central routing table. Project-level
`AGENTS.md` files are not created or changed. See [Gitly](gitly/README.md) for usage.

## Available skills

This list is generated from the skills in this repository. Changes to the
collection trigger a pull request to update it; do not edit the generated section
by hand. Maintainers can regenerate it with `python3 scripts/update-skills-readme.py`.

<!-- skills-index:start -->

### [gitly](gitly/)

Git and GitHub workflows for people who build with AI agents: save, compare, restore, branch, merge, and back up in everyday language.

- [gitly-branches](gitly/gitly-branches/SKILL.md) — List, create, and switch safe branches or isolated worktree experiments. Use for experiments, "try this without breaking my app", branch requests, "ניסוי", or "ענף".
- [gitly-check](gitly/gitly-check/SKILL.md) — Assess whether the current project still works and identify failures after code or AI changes. Use for broad reports of breakage, errors, failed builds or tests, unexpected behavior, or uncertainty about project health; use restore instead only when the user explicitly wants to go back.
- [gitly-compare](gitly/gitly-compare/SKILL.md) — Compare two reachable versions or a version with current work using Git evidence. Use for "what changed", "compare yesterday and today", "מה השתנה", or "השווה גרסאות".
- [gitly-github-connect](gitly/gitly-github-connect/SKILL.md) — Check GitHub CLI authentication and safely create or link a GitHub repository. Use for GitHub connection, online backup setup, "connect to GitHub", or "חבר לגיטהאב".
- [gitly-history](gitly/gitly-history/SKILL.md) — Display searchable project versions in everyday language. Use for history, previous versions, "show me the last five versions", "היסטוריה", or "גרסאות קודמות".
- [gitly-merge](gitly/gitly-merge/SKILL.md) — Inspect and safely combine an experiment branch with the current project. Use for merge/integration requests such as "put the changes into my main project", "merge", "מזג", or "שלב את הניסוי".
- [gitly-restore](gitly/gitly-restore/SKILL.md) — Safely restore files from or revert to a previous project version while preserving recovery paths. Use only when the user explicitly wants to undo work, recover earlier content, or return to a prior state; general breakage reports belong to gitly-check.
- [gitly-save](gitly/gitly-save/SKILL.md) — Review project changes and save an intentional version with a meaningful commit. Use for save/commit requests such as "save everything I did today", "save my progress", "שמור", or "שמור את ההתקדמות".
- [gitly-settings](gitly/gitly-settings/SKILL.md) — Read or update persistent Gitly project preferences through natural language. Use for settings and phrases like "from now on", "always save online", "מעכשיו", or history/language preferences.
- [gitly-setup](gitly/gitly-setup/SKILL.md) — Check Git readiness and safely prepare a project repository. Use for Gitly setup, initialization, Git identity, ignore-file, "set up Git", "הגדר גיט", or "אתחל מאגר" requests.
- [gitly-status](gitly/gitly-status/SKILL.md) — Explain whether project work is saved, backed up, current, or at risk using local Git evidence. Use when the user asks what state the project is in or whether work is safe; do not use to test application behavior.
- [gitly-sync](gitly/gitly-sync/SKILL.md) — Explain and safely synchronize local work with a Git remote using fetch, fast-forward pull, or non-force push. Use for sync, push, pull, online backup, "back it up", "סנכרן", or "גיבוי בענן".

### Standalone skills

- [readability](readability/SKILL.md) — Improves the readability, formatting, and structure of text, documentation, and markdown files. Use when the user asks to clean up text, improve clarity, or structure documentation.
- [safe-migrations](safe-migrations/SKILL.md) — Plans and reviews database schema changes so they are reversible, verified, and never silently destructive. Use when the user asks to add, change, or remove tables or columns, when a migration fails partway, or before running pending migrations in a production or shared environment.
- [secret-guard](secret-guard/SKILL.md) — Keeps credentials out of the repository by checking configuration files and staged changes for secrets before they are saved or pushed. Use when a project starts using API keys, tokens, or service credentials, before the first commit, and whenever configuration or authentication files change.

<!-- skills-index:end -->

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md` or `skills/<group>/<skill-name>/SKILL.md`. The leaf directory must match `name`; names must be unique across the collection.
2. Use lowercase kebab-case for the name, for example `git-workflow`.
3. Write a `description` that says what the skill does **and** when an agent should use it.
4. Use local resource links or `../filename` for top-level group Markdown documents and `LICENSE`. Installation includes shared documents automatically. Set `metadata.collection: vibe.md` and `metadata.group: <group>` for routing.
5. Validate your work:

   ```bash
   python3 scripts/validate-skills.py
   ```

6. Open a Pull Request. CI discovers and validates the new skill automatically.

A regular contribution stays inside its skill or group directory. You never need
to edit the router, installer, validator, or CI to add a group. `_shared/` is
reserved for common skills automatically included in every installation.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the complete format, a full example, and the review checklist.
