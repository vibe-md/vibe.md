# Maintainer guide

This page is for the people who review and merge contributions. It explains how
publication works and lists the GitHub settings the workflow in
[CONTRIBUTING.md](../CONTRIBUTING.md) depends on. **Settings live in GitHub, not
in this repository**, so a maintainer with admin access has to apply them.

## How publication works

```text
merge to main ─► publish.yml ─► GitHub Release "catalog-<sha>" ─► deploy hook ─► website rebuild
                  validate, test,   catalog.json + one ZIP per       (optional)    reads the latest
                  build, verify     package and agent, checksummed                 release at build time
```

- `validate-skills.yml` runs on every Pull Request and on `main`. It has a read-only token and no secrets.
- `publish.yml` runs **only on pushes to `main`** (and manual runs of `main`). It re-runs the checks, builds every package into one directory, verifies that `catalog.json`, the manifests, and the ZIPs agree, then creates the release as a draft, uploads every file, and publishes it as the latest release. A failed step publishes nothing.
- A slower run for an older commit skips publishing when `main` has already moved, so the latest release is always the newest commit.
- The website reads `https://github.com/vibe-md/vibe.md/releases/latest/download/catalog.json` when it builds and checks every ZIP against the checksums in it. If the download or a checksum fails, the website keeps its last committed, consistent copy and logs a warning. It never mixes versions.

To check a publication: open **Actions → Publish catalog**, then the **Releases** page. From a terminal:

```bash
curl -sL https://github.com/vibe-md/vibe.md/releases/latest/download/catalog.json | python3 -m json.tool | head
```

To roll back, mark an earlier release as the latest and rebuild the website:

```bash
gh release edit catalog-<12-character-sha> --latest
```

## Required GitHub settings

Checked read-only on 2026-10-28. The first column is what is configured now.

| Setting | Now | Required |
| --- | --- | --- |
| Pull request required before merging | yes | yes |
| Required approving reviews | **0** | **1** |
| Dismiss stale approvals when new commits are pushed | no | **yes** |
| Require review from Code Owners | no | **yes** (see `.github/CODEOWNERS`) |
| Require approval of the most recent reviewable push | no | **yes** |
| Required status check | `CI passed` | `CI passed` |
| Resolve conversations before merging | yes | yes |
| Apply the rules to administrators | **no** | **yes** |
| Allow force pushes and deletions | no | no |
| Rulesets | none | optional alternative to the branch rule |

Set them in **Settings → Branches → Branch protection rules → `main`**, or in
**Settings → Rules → Rulesets** (a ruleset can also name bypass actors explicitly,
which is clearer than administrators silently bypassing a branch rule).

Because GitHub never counts an author's own approval, a maintainer's Pull Request
needs a second maintainer. With two maintainers that is the intended behavior. If an
emergency fix needs to skip review, use a ruleset bypass actor and say so in the PR.

**Who may merge.** On an organization repository, enable **Restrict who can push to
matching branches** (or the ruleset equivalent) and allow only a `maintainers` team.
Contributors from forks cannot merge in any case, because they have no write access.
Collaborators with Write access can merge an approved Pull Request unless this
restriction is set, so grant Write access only to maintainers. Today the
organization has no teams; create one in **Organization → Teams**.

**CODEOWNERS** does nothing by itself. It is only enforced when "Require review from
Code Owners" is on. To add a package maintainer, add their username to the package
line in `.github/CODEOWNERS` and to `maintainers` in the package README.

## Actions settings

In **Settings → Actions → General**:

| Setting | Now | Recommended |
| --- | --- | --- |
| Fork pull request workflows | approval for first-time contributors | **approval for all outside collaborators** |
| Workflow permissions | read repository contents | keep read-only |
| Allow Actions to create and approve pull requests | off | keep off |
| Require actions to be pinned to a full commit SHA | off | **on** (the workflows already pin every action) |

Never switch the validation workflow to `pull_request_target`, and do not add a
step that runs code from a Pull Request with a token or secret in the environment.

## Website rebuild hook (optional, one secret)

Without a hook the website still picks up the latest release the next time it
builds, but not immediately.

1. In the website's Vercel project: **Settings → Git → Deploy Hooks**, create a hook named `catalog-published` for the `main` branch, and copy its URL.
2. In this repository: **Settings → Secrets and variables → Actions → New repository secret**, name `VERCEL_DEPLOY_HOOK_URL`, and paste the URL. Treat the URL as a password.
3. The next merge to `main` triggers a rebuild after publishing. If the hook is missing or fails, the workflow warns but the release stays published; re-run the job to retry.

The website needs no other configuration. Its build runs `npm run sync:catalog`, which
downloads the release from the URL above. To test another release, set
`CATALOG_URL` for that build.

## Reviewing a Pull Request

Automated checks catch honest mistakes. They cannot judge intent. For every
contribution read the `description` (will an agent pick it at the right time?),
every instruction that changes files or runs commands, and every `scripts/` file.
The validator marks the places that need attention as warnings. Merge only when
you would be comfortable with every user running the skill.
