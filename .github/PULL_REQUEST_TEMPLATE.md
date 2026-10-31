## Summary

<!-- What does this Pull Request change, and why? -->

## Type of change

- [ ] New skill in an existing package
- [ ] New package
- [ ] Improvement to an existing skill
- [ ] Installer, validator, or CI
- [ ] Documentation
- [ ] Other

## Skill checklist

<!-- For skill contributions. Delete this section if your PR does not touch skills/. -->

- [ ] `SKILL.md` has valid YAML frontmatter with `name` and `description`.
- [ ] The skill name is unique, lowercase kebab-case, matches its directory name, and starts with its package name (for example `security-audit`).
- [ ] New package: `skills/<package>/README.md` explains the package (frontmatter: `categories` is required; title, summary and maintainers are optional).
- [ ] The description says what the skill does **and** when an agent should use it.
- [ ] Resources live inside each skill or as top-level group Markdown documents/`LICENSE`; relative links resolve after installation.
- [ ] Prerequisites (tools, accounts, network access) are documented in `SKILL.md`.
- [ ] No secrets, tokens, credentials, or personal data are included.
- [ ] Bundled scripts perform no unexpected, destructive, or hidden operations, and `SKILL.md` explains what they do.
- [ ] I tested the skill with at least one coding agent. Agents tested: <!-- e.g. Claude Code, Codex -->
- [ ] Existing skills are unaffected; group installation also preserves other installed groups.
- [ ] Third-party material is properly licensed and attributed.

## Validation

- [ ] `python3 scripts/validate-skills.py` passes.
- [ ] `python3 -m unittest discover -s tests` passes.

## Notes for reviewers

<!-- Anything reviewers should know: design decisions, open questions, screenshots. -->
