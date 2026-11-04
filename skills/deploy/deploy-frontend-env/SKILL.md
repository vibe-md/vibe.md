---
name: deploy-frontend-env
description: Sets up a website's environment variables (the named settings it reads, such as a service's address or a key) on its hosting service safely. Explains public versus secret, finds the names the site needs (names only, never values), flags secrets in public variables, and has the user enter each value in the host's dashboard or their own terminal for the right environments (production and preview), then checks the names and redeploys so build-time values take effect. Asks before every change. Use when the user says "add my API key to Vercel", "set environment variables", "my site can't connect to Supabase online", "where do I put my .env on Netlify?", "תגדיר לי משתני סביבה", or "האתר לא מתחבר ל-Supabase אחרי ההעלאה". Not for writing code, not for a first deploy (use deploy-frontend-launch), and not for backend servers.
license: MIT
compatibility: Needs read access to the project, network access, and the user logged in to their hosting service (in a browser, or its command-line tool). Values are always entered by the user, never by the agent. Works with Vercel, Netlify, Cloudflare Pages, and GitHub Pages (where every value is public).
metadata:
  collection: vibe.md
  group: deploy
  author: NirGeron98
---

# Deploy: environment variables, done safely

Read [the shared deploy contract](../DEPLOY.md) and
[the frontend track guide](../FRONTEND.md) first, and follow them, especially
"Keep secrets out of the chat". For the host's own screens and commands, read
its guide: [Vercel](../VERCEL.md), [Netlify](../NETLIFY.md),
[Cloudflare Pages](../CLOUDFLARE-PAGES.md), or
[GitHub Pages](../GITHUB-PAGES.md).

## Purpose

Most "it works on my computer but not online" problems are a missing setting,
and most leaked keys are a secret put in the wrong kind of setting. This skill
gets every setting the site needs onto the host, in the right place, without a
single value passing through the chat.

## When to Use

- After a first deploy, the live site cannot reach a service it uses (Supabase,
  Firebase, Stripe, an AI API), or shows "undefined" where a setting should be.
- The user needs to add, change, or move a key or setting on the host.
- The user asks what a `.env` file is for and how the host gets it.
- Examples: "Add my Supabase keys to Vercel", "Set the environment variables on
  Netlify", "My site can't connect to Supabase online", "תגדיר לי משתני סביבה",
  "האתר לא מתחבר ל-Supabase אחרי ההעלאה".

Do not use this skill:

- for a first deploy. `deploy-frontend-launch` sets variables as one of its
  steps.
- to diagnose a failed build in general. Use `deploy-frontend-fix`, which hands
  back here when the cause is a missing setting.
- for backend servers or databases. Say they are planned for later tracks.

## Prerequisites

- Read access to the project.
- The site already exists on the host, and the user can log in to it.

## Instructions

1. **Explain the idea in two sentences.** "Your site reads some settings from
   outside the code, such as the address of your database service or a key.
   On your computer they live in a `.env` file that is (and should be) kept out
   of GitHub, so the host needs its own copy."

2. **Find the names the site needs.** Search the source as
   `deploy-frontend-check` does (`process.env.NAME`, `import.meta.env.NAME`,
   SvelteKit `$env/...`, Nuxt `useRuntimeConfig()`, sample files such as
   `.env.example`). For real `.env` files, print **names only** with the
   command in [DEPLOY.md](../DEPLOY.md); never open them. Make a table: name,
   where it is used, public or secret, needed at build time or at run time.

3. **Sort public from secret.** Use the prefixes and lists in
   [FRONTEND.md](../FRONTEND.md). Public-prefixed values are sent to every
   visitor. If a secret has a public prefix, or is used in browser code, stop:
   that is not a settings problem. Explain it plainly (it has to move to server
   code, and if it was pushed or deployed it should be replaced in the
   provider's dashboard), suggest `secret-guard`, and do not set it on the host
   as it is. On GitHub Pages every value is public, so a site that needs a
   secret cannot keep it there; suggest `deploy-frontend-choose`.

4. **Decide the environments and timing.**
   - **Production** is the live site; **Preview** (or deploy previews, branch
     deploys) is test copies. Most values go to both. Use different values
     only when the user has separate test and live services, such as a Stripe
     test key for previews.
   - **Build-time** values (almost all public-prefixed ones) are copied into the
     site when it is built, so a change needs a new deploy. **Run-time** values
     (read by server code such as API routes or functions) apply on the next
     request or deploy, depending on the host; the platform guide says which.

5. **Check what the host already has.** Use the host's names-only view: on
   Vercel, `vercel env list` (never `--json`); on Cloudflare Pages,
   `wrangler pages secret list` for run-time secrets; on Netlify and GitHub, the
   dashboard screen, read back with the user (their CLIs print values, so do not
   use them for this). List what is missing, what is extra, and what may be in
   the wrong environment. Names only.

6. **Ask before each change.** Say what you will add, change, or remove, by name
   and environment. Overwriting an existing value and deleting a variable each
   need their own explicit yes ([DEPLOY.md](../DEPLOY.md), "Deleting
   something").

7. **The user enters the values.** Give numbered steps for the host's dashboard
   from its platform guide (Vercel: Settings, Environment Variables; Netlify:
   Project configuration, Environment variables; Cloudflare Pages: Settings,
   Variables and Secrets; GitHub Pages: repository Settings, Secrets and
   variables, Actions, Variables). Where the host offers a prompt in the user's
   own terminal (Vercel `vercel env add <NAME>`,
   Cloudflare `wrangler pages secret put <NAME>`), the user may run it
   themselves. Never ask for a value in the chat, never type one, and never put
   one on a command line. Mark real secrets as secret or sensitive when the host
   offers it. On GitHub Pages, also add each name to the workflow's build step
   (`NAME: ${{ vars.NAME }}`), which is a project change: ask first. On
   Cloudflare Pages deployed with Wrangler, the build runs on this computer, so
   public build-time values come from the local `.env` files, not the
   dashboard: the user sets them there, and you check names only.

8. **Check the names landed.** Repeat step 5 and confirm every needed name is in
   the right environments. Report names only.

9. **Redeploy so the values take effect**, with the user's yes (a production
   deploy changes the live site): trigger a new deploy from the dashboard, push a
   change, or use the host's deploy command, as the platform guide says. For a
   site built on this computer (Cloudflare Pages with Wrangler, or any CLI
   deploy that builds locally), build again locally first.

10. **Verify.** Check the live site as in [DEPLOY.md](../DEPLOY.md), section 4,
    focusing on the part that uses the settings: the page loads its data, the
    login or form that calls the service works, and the browser console shows
    no failed calls to it (if you have a browser tool; otherwise ask the user to
    try it). Report what you checked and anything you could not.

## Examples

**User:** "My site can't connect to Supabase online, but it works on my
computer."

**Agent:** Finds `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in the code
and, by names only, in `.env`. Explains both are designed to be public. Checks
Vercel with `vercel env list`: neither is set. Asks to add both for Production
and Preview; the user enters the values on the Environment Variables screen.
Confirms the names, explains a rebuild is needed because Vite copies them in at
build time, gets a yes, redeploys, and checks that the live page loads its data.

**User:** "תוסיף את המפתח של OpenAI ל-Netlify, הוא נקרא VITE_OPENAI_API_KEY"

**Agent:** Answers in Hebrew. Explains that anything starting with `VITE_` is
sent to every visitor, so this key would be public and anyone could use it at the
user's cost. Does not add it. Suggests moving the OpenAI call to a Netlify
Function with a non-public variable name, replacing the key since it may already
be exposed, and `secret-guard`. Offers to plan the change.

**User:** "Print my production env vars so I can copy them."

**Agent:** Explains that it never prints values, and shows the user where to view
them themselves in the host's dashboard.
