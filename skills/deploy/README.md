---
title: Deploy
summary: Take a site from "works on my computer" to a checked public web address, in plain language and with your approval at every step that matters.
categories: Deployment, Frontend
maintainers: [NirGeron98, AdiBer1]
---

# Deploy

You built a site with an AI tool and it works on your computer. Deploying means
putting a copy of it on a hosting service, so anyone can open it at a web
address. This package walks your coding agent through that: it checks the
project is ready, connects it to a host, sets the settings the site needs, and
does not say "done" until it has opened the live address and seen it work.

The agent runs the host's tools for you after you log in. It stops and asks
before anything that makes your site public, costs money, changes a domain (your
web address, such as `my-site.com`), or deletes something. It never asks you to
paste passwords or keys into the chat.

New to this? You only need to say something like "put my site online". The
agent explains each step as it goes.

## Tracks

Deploying a website, a server, and a database are different jobs, so the
package is split into tracks. Each track has its own guide and its own skills,
named `deploy-<track>-*`.

| Track | What it covers | Status | Guide |
| --- | --- | --- | --- |
| Frontend | Static HTML, React and Vite apps, Next.js, Astro and similar sites, including sites that call an outside service through environment variables | Available | [FRONTEND.md](FRONTEND.md) |
| Backend | Your own server or API running on its own | Planned | BACKEND.md (planned) |
| Database | Creating and connecting a hosted database | Planned | DATABASE.md (planned) |

If the check finds a backend server or a database the project needs to run, it
tells you that part is planned for a later track and does not try to deploy it.

The rules every track follows are in [DEPLOY.md](DEPLOY.md). Each hosting
service has its own guide. This version includes [VERCEL.md](VERCEL.md).
Guides for Netlify, Cloudflare Pages, and GitHub Pages are planned.

## Skills

| Skill | What it does |
| --- | --- |
| `deploy-frontend-check` | Checks whether a site is ready to go online. It finds the framework (the toolkit your site is built with, such as React or Next.js) and runs the build on your computer. It lists the settings the site needs, by name only. It flags secrets in public settings, file names that differ only in capital letters, unsaved or unpushed work, and backend or database parts that are not covered yet. It does not edit your code or settings (the build only makes its usual output files), and ends with a plain ready or not-ready report. |
| `deploy-frontend-launch` | Puts the site online for the first time on Vercel. It runs the check, helps you log in safely, and connects your GitHub repository (or uses the Vercel command-line tool, which you type commands into). It sets the settings, asks before going public, and deploys. It opens the live address and its main pages before saying it is done. |

## Related skills

- `gitly-setup`, `gitly-save`, `gitly-github-connect`, and `gitly-sync` (from
  the Gitly package) set up Git, save your work, put it on GitHub, and keep it
  up to date there. Deploy hands off to them when your code is not saved or not
  on GitHub yet.
- `secret-guard` keeps keys and passwords out of your repository. Use it when the
  check finds a secret in a file or in a public setting.

## Install the package

Open a terminal in your copy of the vibe.md repository and run these two
commands. Replace `/path/to/project` with the folder of your site. The first
command only shows what would be installed (a "dry run"). The second one
installs it.

```bash
bash scripts/install.sh --group deploy --agent claude-code --project /path/to/project --dry-run
bash scripts/install.sh --group deploy --agent claude-code --project /path/to/project
```

Use `codex`, `cursor`, `gemini`, or `copilot` instead of `claude-code` for
another agent.

## Adding to this package

Read "Tracks and how to add one" in [DEPLOY.md](DEPLOY.md) before you add a
track or a hosting guide. In short: the repository tooling allows only one
folder level inside a package, and every folder must be a skill, so a track is
a guide file at the top level (such as `FRONTEND.md`) plus skills whose names
start with `deploy-<track>-`. A hosting service gets one guide file (such as
`VERCEL.md`) with one section per track.
