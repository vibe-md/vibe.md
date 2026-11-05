---
title: Google services
summary: Unofficial. Add Google login, maps, Firebase, analytics, Search Console, Sheets and Gemini to your site, with restricted keys and budget alerts.
categories: Backend, Security, Frontend
maintainers: [NirGeron98, AdiBer1]
---

# Google services

**Unofficial:** vibe.md is not made by or affiliated with Google.

You built a site or app with an AI tool, and now you want "Log in with Google",
a map, a database, visitor stats, a spot in Google Search, a Google Sheet, or
Gemini AI. Each of these needs a Google account. Most also need a Google Cloud
project (the folder in Google's systems that holds your keys, settings and
bill) and a key (a password-like string that lets your app use a Google
service). Done carelessly, a key ends up in public code and someone else runs
up your bill. This package walks your coding agent through each service the
safe way.

Your agent:

- explains what is free and what costs money, reading Google's current price
  pages, and sets a budget alert before anything paid is turned on. A budget
  alert sends you an email. It does not stop spending, so the agent adds other
  limits too;
- keeps every key out of your code and out of the chat. You copy keys from
  Google straight into your own settings file;
- restricts each key to the services it needs, and to your own website when the
  key has to be visible in the browser;
- tells you exactly what to do on Google's own screens, which change often,
  then checks the result itself;
- asks before anything that costs money, deletes data, or makes something
  public;
- does not say "done" until the feature works.

New to this? Say what you want, for example "add Google login to my site", and
the agent explains each step as it goes. Start with `google-setup` if you have
never used Google Cloud.

## Skills

| Skill | What it does |
| --- | --- |
| `google-setup` | Gets your Google Cloud project ready: creates or picks the project, explains what is free and what costs money, sets a budget with email alerts before any paid service, and turns on only the services you need. The other skills send you here when you have no project or budget yet. |
| `google-sign-in` | Adds "Log in with Google". Sets up the login screen Google shows and the exact return addresses for your computer and your live site (the most common reason it breaks), for Auth.js (NextAuth), Supabase, Firebase Auth or Clerk. Ends with a real login test. |
| `google-maps` | Shows a map, searches places, or fills in addresses as people type. Needs billing turned on, with a budget alert. Uses a key that only works on your own website and only for maps, and can cap daily use. |
| `google-keys-check` | Checks the Google keys in your project without changing anything: keys in your code or its history, secret keys sent to visitors' browsers, and keys anyone could use because they have no restrictions. Shows keys partly hidden and gives a ranked list of what to fix. |
| `google-firebase` | Adds Firestore (a database), Storage (file uploads) and Firebase Hosting, with security rules that let each user reach only their own data. Tests the rules on your computer first, then puts them live with your yes. |
| `google-analytics` | Adds Google Analytics 4 with a simple cookie banner, so visits are counted only after a visitor agrees. Checks the visit shows up in Google's live report. |
| `google-search-console` | Gets your live site into Google Search: proves you own it, submits your list of pages (sitemap), and explains in plain words why a page is "not indexed" and how to fix it. |
| `google-sheets` | Uses a Google Sheet as a simple database or as the place your form sends its entries, through a robot account that can open only that one Sheet. Needs a site with server code, because a static site cannot hide the key. Ends by writing and reading a test row. |
| `google-gemini` | Adds Gemini AI to your app with the key kept on your server, plus limits per user and per day, so a busy feature is much less likely to run up a bill. Needs a site with server code. |

Shared rules every skill follows are in [GOOGLE.md](GOOGLE.md). The kinds of
Google keys, where each may live, and how to restrict them are in
[KEYS.md](KEYS.md).

## Related skills

- `deploy-frontend-env` (from the Deploy package) puts the keys and settings on
  your hosting service for the live site. `deploy-frontend-domain` changes DNS
  records; Search Console verification follows its rules.
  `deploy-frontend-launch` puts the site online first.
- `secret-guard` finds secrets and helps keep them out of Git. It changes Git
  history only with your approval.
- `security-agent-guard` (from the Security package) reviews an AI feature for
  security problems. `security-access-regression` checks who can see what after
  login.
- `llm-prompt-review`, `llm-eval-builder` and `llm-model-migration-check` (from
  the LLM package) improve and test an AI feature once Gemini is connected.

## Install the package

Open a terminal in your copy of the vibe.md repository and run these two
commands. Replace `/path/to/project` with the folder of your site. The first
command only shows what would be installed (a "dry run"). The second one
installs it.

```bash
bash scripts/install.sh --group google --agent claude-code --project /path/to/project --dry-run
bash scripts/install.sh --group google --agent claude-code --project /path/to/project
```

Use `codex`, `cursor`, `gemini`, or `copilot` instead of `claude-code` for
another agent.

## Adding to this package

Each Google service gets one skill named `google-<service>`, in its own folder
directly under `skills/google/`. Shared rules go in [GOOGLE.md](GOOGLE.md) and
key rules in [KEYS.md](KEYS.md), not copied into each skill. Describe Google's
screens by what to look for and link Google's own docs, because the screens
change often.
