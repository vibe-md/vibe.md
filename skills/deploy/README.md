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
service has its own guide:

| Host | Good for | Guide |
| --- | --- | --- |
| Vercel | Next.js (including server features) and most other frameworks, with previews | [VERCEL.md](VERCEL.md) |
| Netlify | Static sites, single-page apps, and Next.js, with previews | [NETLIFY.md](NETLIFY.md) |
| Cloudflare Pages | Static sites and single-page apps, especially when the domain is already on Cloudflare | [CLOUDFLARE-PAGES.md](CLOUDFLARE-PAGES.md) |
| GitHub Pages | Free, personal static sites straight from a GitHub repository; no server code and no secrets | [GITHUB-PAGES.md](GITHUB-PAGES.md) |

Not sure which one? Ask "where should I host my site?" and the agent compares
them for your project, reading each host's current prices and rules.

## Skills

| Skill | What it does |
| --- | --- |
| `deploy-frontend-check` | Checks whether a site is ready to go online. It finds the framework (the toolkit your site is built with, such as React or Next.js) and runs the build on your computer. It lists the settings the site needs, by name only. It flags secrets in public settings, file names that differ only in capital letters, unsaved or unpushed work, and backend or database parts that are not covered yet. It does not edit your code or settings (the build only makes its usual output files), and ends with a plain ready or not-ready report. |
| `deploy-frontend-choose` | Helps you pick a host (Vercel, Netlify, Cloudflare Pages, or GitHub Pages) for this site. It checks whether the site needs server code or secrets, what you plan to use it for, and which accounts you already have, reads each host's current free-plan rules, and recommends one, with the reason. It changes nothing. |
| `deploy-frontend-launch` | Puts the site online for the first time on any of the four hosts. It runs the check, helps you log in safely, and connects your GitHub repository (or uses the host's command-line tool, which you type commands into, or a GitHub Actions workflow for GitHub Pages). It sets the settings, asks before going public, and deploys. It opens the live address and its main pages before saying it is done. |
| `deploy-frontend-env` | Puts the settings your site needs (environment variables) on the host safely. It explains public and secret settings, finds the names the site uses, and has you type each value into the host yourself, so no value ever passes through the chat. Then it redeploys and checks. |
| `deploy-frontend-domain` | Connects your own domain (such as `my-site.com`). It looks at the domain's current settings first, explains each DNS record in plain words, protects your email settings, waits for the change to spread, and checks the padlock (HTTPS). It asks before every change and never buys anything. |
| `deploy-frontend-update` | Publishes your later changes. It builds them, uses a test address (a preview) first where the host offers one, asks before changing the live site, and checks it afterwards. |
| `deploy-frontend-fix` | Finds out why a deploy failed or the live site is broken, from the host's logs. It explains the cause in plain words, proposes the smallest fix, and asks before changing anything. |
| `deploy-frontend-rollback` | Gets a broken live site back to the last version that worked, using the host's own rollback or Git, then checks the live address. It asks first and tells you what happens with your next update. |

## Related skills

- `gitly-setup`, `gitly-save`, `gitly-github-connect`, and `gitly-sync` (from
  the Gitly package) set up Git, save your work, put it on GitHub, and keep it
  up to date there. Deploy hands off to them when your code is not saved or not
  on GitHub yet.
- `gitly-branches`, `gitly-merge`, and `gitly-restore` make a test branch for a
  preview, combine it when it is ready, and undo a bad change in Git. The update
  and rollback skills hand off to them.
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
`VERCEL.md` or `GITHUB-PAGES.md`) with one section per track.
