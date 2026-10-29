# Maintainer guide

This page is for the people who review and merge contributions. It explains how
publication works and lists the GitHub settings the workflow in
[CONTRIBUTING.md](../CONTRIBUTING.md) depends on. **Settings live in GitHub, not
in this repository**, so a maintainer with admin access has to apply them.

## How publication works

> **Status:** the publication workflow is implemented but has not run on GitHub yet. No release
> exists, and the website deploy hook is not configured. Treat publication as unverified until
> a maintainer has completed the checklist at the end of this page and one real merge has
> produced a release.

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

Read from GitHub on 2026-10-28 (read-only), so this table is a snapshot: check the
settings pages before relying on it.

An active repository ruleset named **`block`** applies to the default branch, with **no
bypass actors** (administrators are bound by it). It requires a Pull Request with one
approval and blocks deletion and force pushes. The older branch protection rule also
requires the `CI passed` check and resolved conversations. When both apply, the stricter
rule wins.

| Setting | Now | Required |
| --- | --- | --- |
| Pull request required before merging | yes (ruleset and branch protection) | yes |
| Required approving reviews | **1** (ruleset). The branch rule says 0 | 1 |
| Block force pushes and deletions | yes | yes |
| Rules apply to administrators | yes (the ruleset has no bypass actors) | yes |
| Required status check `CI passed` | branch protection only | also add it to the ruleset, or keep the branch rule |
| Resolve conversations before merging | branch protection only | yes |
| Dismiss stale approvals when new commits are pushed | **no** | **yes** |
| Require review from Code Owners | **no** | **yes** (see `.github/CODEOWNERS`) |
| Require approval of the most recent reviewable push | **no** | **yes** |
| Restrict who may merge | **no** (the organization has no teams) | **yes**, to a `maintainers` team |
| Fork pull request workflows need approval | first-time contributors only | all outside collaborators |
| Require actions to be pinned to a full commit SHA | **no** | yes (the workflows already pin every action) |

Still incomplete: every **bold** row above, and the website hook below. Until they are
applied, a pushed approval can go stale without being dismissed, and no setting ties
approval to the people listed in CODEOWNERS.

Set them in **Settings → Rules → Rulesets** (edit `block`) or **Settings → Branches**.
A ruleset can also name bypass actors explicitly, which is clearer than administrators
bypassing a rule. With no bypass actors, even an emergency fix needs a second
maintainer's approval; add a bypass actor if you want an emergency path, and say so in the PR.

Because GitHub never counts an author's own approval, a maintainer's Pull Request
needs a second maintainer. With two maintainers that is the intended behavior.

**Approval is not permission to merge.** Contributors from forks cannot merge in any
case, because they have no write access. Collaborators with Write access can merge an
approved Pull Request unless merging is restricted, so grant Write access only to
maintainers. Today the only collaborators are the two administrators. To make this
explicit and durable, create a `maintainers` team (**Organization → Teams**) and restrict
who may merge to it.

**CODEOWNERS** does nothing by itself. It is only enforced when "Require review from
Code Owners" is on. To add a package maintainer, add their username to the package
line in `.github/CODEOWNERS` and to `maintainers` in the package README.

## Actions settings

In **Settings → Actions → General**:

| Setting | Now | Recommended |
| --- | --- | --- |
| Fork pull request workflows | approval for first-time contributors | **approval for all outside collaborators** |
| Workflow permissions | read repository contents | keep read-only |
| Allow Actions to create and approve pull requests | off | required for the automated skills README PR |
| Require actions to be pinned to a full commit SHA | off | **on** (the workflows already pin every action) |

The skills README workflow needs **Allow GitHub Actions to create and approve
pull requests** enabled at both organization and repository level. GitHub uses
one setting for both abilities; enabling it also permits appropriately scoped
workflows to approve PRs. The README workflow itself only creates or updates a
PR, uses a dedicated automation branch, and never approves or merges it. The
default token permissions remain read-only; write permissions are limited to
its trusted-main job. A GitHub-token-created PR may require a maintainer to
approve its CI run before merging. After enabling the setting and merging the
workflow, use **Actions → Update skills README → Run workflow** to verify setup;
a PR is created only when the index differs from main.

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

## Before relying on automatic publication

1. Apply the settings marked **bold** above.
2. Create the Vercel deploy hook and the `VERCEL_DEPLOY_HOOK_URL` secret (optional but recommended).
3. Merge a small change to `main` and confirm in **Actions → Publish catalog** that a `catalog-<sha>` release appears with `catalog.json` and the ZIPs.
4. Check that the website rebuilt and shows the same source revision as `catalog.json`.
5. Only then tell contributors that merged contributions are published automatically.
