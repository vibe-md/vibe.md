---
name: deploy-frontend-choose
description: Helps pick a hosting service for a website (Vercel, Netlify, Cloudflare Pages, or GitHub Pages) and explains why. Read-only. Looks at the framework, whether the site is static or needs server code, the free plan's current limits and rules (read live, with the date), custom domain plans, commercial use, and accounts the user already has, then ends with one recommendation, the reason, and a runner-up. Use when the user asks "where should I host my site?", "Vercel or Netlify?", "which host is free for my project?", "can I put this on GitHub Pages?", "איפה כדאי לי לארח את האתר?", or "מה עדיף, Vercel או Netlify?". Not for deploying (use deploy-frontend-launch), not for backend servers or databases, and not for Docker or VPS hosting.
license: MIT
compatibility: Needs read access to the project. Reading prices and terms needs network access to the hosts' websites; if it is not available, the skill says so instead of quoting prices from memory. No hosting account is needed, and nothing is created or changed.
metadata:
  collection: vibe.md
  group: deploy
  author: NirGeron98
---

# Deploy: choose a host for a website

Read [the shared deploy contract](../DEPLOY.md) and
[the frontend track guide](../FRONTEND.md) first, and follow them. The hosts
this package has guides for are [Vercel](../VERCEL.md),
[Netlify](../NETLIFY.md), [Cloudflare Pages](../CLOUDFLARE-PAGES.md), and
[GitHub Pages](../GITHUB-PAGES.md).

## Purpose

Most people pick a host because a tutorial used it, then find out it cannot run
their site or does not allow their use. This skill matches the site to a host
that can actually run it, under rules that fit the user's plans, and explains
the choice in plain words. It changes nothing: no accounts, no settings, no
files.

## When to Use

- The user is about to put a site online and does not know where.
- The user asks to compare hosts, or whether a specific host can run their site.
- The user's current host does not fit any more (it cannot run a feature, or the
  site became commercial).
- Examples: "Where should I host my site?", "Vercel or Netlify?", "Can I put
  this on GitHub Pages for free?", "איפה כדאי לי לארח את האתר?", "מה עדיף,
  Vercel או Netlify?".

Do not use this skill:

- to deploy. When the user has chosen, hand off to `deploy-frontend-launch`.
- to host a separate backend server or a database. Say these are planned for
  later tracks.
- for Docker, VPS, or Kubernetes hosting. That is not this package.

## Prerequisites

- Read access to the project.
- Network access to read the hosts' pricing and terms pages. Without it, say so
  and recommend on technical fit only.

## Instructions

1. **Understand the site.** If `deploy-frontend-check` already ran, use its
   findings. Otherwise detect the framework, build command, and output folder
   with the tables in [FRONTEND.md](../FRONTEND.md), without building. The key
   question: **does the site need code running on the server?** It does if it
   uses Next.js API routes, route handlers, server actions, or server
   rendering; Astro, SvelteKit, or Nuxt in server mode; or Pages Functions or
   Netlify Functions folders. Plain HTML, Vite apps, Create React App, and
   static exports do not. Also note any secret the site needs at run time (only
   server code can keep it secret). If you find a separate backend server or a
   database, say they are planned for later tracks and choose for the website
   only.

2. **Ask what matters to the user**, in one short message, skipping anything
   already known:
   - Is it for a business, a client, or anything that earns money?
   - Do they want their own domain (such as `my-site.com`) now or later?
   - Which accounts do they already have: GitHub, Vercel, Netlify, Cloudflare?
     (A domain already on Cloudflare matters too.)
   - Do they want automatic test addresses for each change (previews)?

3. **Rule out hosts that cannot run it**, using the table in
   [FRONTEND.md](../FRONTEND.md) and the platform guides:
   - Server features: not GitHub Pages. For server-rendered Next.js, prefer
     Vercel or Netlify; Cloudflare's current path for it runs on Workers, which
     this package does not cover (see [CLOUDFLARE-PAGES.md](../CLOUDFLARE-PAGES.md)).
   - A secret needed at run time: not GitHub Pages, where everything is public.
   - A business, shop, or SaaS: GitHub Pages' rules exclude it (read them live,
     see [GITHUB-PAGES.md](../GITHUB-PAGES.md)). Check each remaining host's
     free-plan rules for commercial use too.
   - A private repository: GitHub Pages may need a paid GitHub plan; check live.

4. **Read prices and terms live** for the hosts that are left, from the pages
   each platform guide lists. Note what each free plan allows for this user's
   case, the address, and the date you read it. If you cannot open a page, say
   so for that host. Never quote limits or prices from memory.

5. **Recommend one host and a runner-up.** Weigh, in this order: can it run the
   site; do its rules allow the user's use; does it match accounts the user
   already has (a GitHub-only user with a static portfolio may prefer GitHub
   Pages; a domain already on Cloudflare points to Cloudflare Pages); then
   convenience (previews, dashboard, how easy the first deploy is for a
   beginner). Useful defaults when nothing else decides it:
   - Next.js, especially with server features: **Vercel**.
   - Static or single-page site, wants previews and an easy dashboard:
     **Netlify** or **Vercel**.
   - Personal static site, already on GitHub, no previews needed: **GitHub
     Pages**.
   - Domain already managed on Cloudflare, static site: **Cloudflare Pages**.

6. **Report.** In plain words: the recommendation, two or three reasons tied to
   this project and this user, what the free plan allows for their case (with
   the address and date read, or "could not check"), anything the user must
   change for that host (for example a base path for GitHub Pages, or a
   routing rule), and the runner-up with the one reason it came second. End by
   offering `deploy-frontend-launch` with the chosen host. Do not create an
   account, connect anything, or deploy in this skill.

## Examples

**User:** "Where should I host my site? It's a Next.js app with a contact form
that uses an API route."

**Agent:** Finds `app/api/contact/route.ts`, so the site needs server code.
Rules out GitHub Pages. Asks two questions; the user says it is for their small
business and they already have a GitHub account. Reads Vercel's and Netlify's
current pricing and free-plan rules, and tells the user what each says about
commercial use, with the dates. Recommends the host whose rules fit a business
site, explains why, names the other as runner-up, and offers
`deploy-frontend-launch`.

**User:** "אני רוצה לשים את תיק העבודות שלי באוויר בחינם, הוא כבר בגיטהאב"

**Agent:** Answers in Hebrew. Finds a Vite + React portfolio with no server code
and no secrets. Reads GitHub Pages' limits and rules page and tells the user what
it says and the date. Recommends GitHub Pages, notes that the site will live at
`https://<user>.github.io/<repo>/` so Vite needs a base path, and that direct
links to inner pages need the 404 workaround. Names Netlify as runner-up for
previews. Offers to launch.

**User:** "Which host is best for my Django app?"

**Agent:** Explains that a Django app is a backend server, which this package
plans for a later track, and that it cannot recommend a host for it here.
