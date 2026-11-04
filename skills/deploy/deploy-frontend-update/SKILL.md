---
name: deploy-frontend-update
description: Ships changes to a website that is already online, safely. Checks the change builds, saves and pushes it (Git-connected hosts) or deploys it with the host's tool, uses a preview address to check the change first where the host offers one, asks before publishing to production, and checks the live site after every deploy. Explains preview versus production in plain words. Use when the user says "update my live site", "publish my changes", "push this to production", "I changed the homepage, put it online", "תעדכן את האתר באוויר", or "תעלה את השינויים לאתר". Not for the first deploy (use deploy-frontend-launch), not for undoing a bad deploy (use deploy-frontend-rollback), not for a failed build (use deploy-frontend-fix), and not for backend servers or databases.
license: MIT
compatibility: Needs Git, network access, the project's build tools (usually Node.js and its package manager), and a site already deployed on a supported host (Vercel, Netlify, Cloudflare Pages, or GitHub Pages). Saving and pushing use the Gitly skills when installed. Uses curl to verify the live site.
metadata:
  collection: vibe.md
  group: deploy
  author: NirGeron98
---

# Deploy: update a live site

Read [the shared deploy contract](../DEPLOY.md) and
[the frontend track guide](../FRONTEND.md) first, and follow them. For the
host's preview and production behaviour, read "Production and preview" in its
guide: [Vercel](../VERCEL.md), [Netlify](../NETLIFY.md),
[Cloudflare Pages](../CLOUDFLARE-PAGES.md), or
[GitHub Pages](../GITHUB-PAGES.md).

## Purpose

After the first launch, every change the user makes has to reach the live site,
and every update is a small chance to break it. This skill makes updates
routine: build it, check it on a test address when the host offers one, publish
with the user's yes, and confirm the live site still works.

## When to Use

- The site is already online and the user changed something and wants it live.
- The user asks how updates work now, or what a "preview" is.
- Examples: "Update my live site", "Publish my changes", "Push this to
  production", "I changed the homepage, put it online", "תעדכן את האתר באוויר",
  "תעלה את השינויים לאתר".

Do not use this skill:

- for the first deploy. Use `deploy-frontend-launch`.
- to undo a bad update. Use `deploy-frontend-rollback`.
- when the build fails online. Use `deploy-frontend-fix`.
- to change only settings or keys. Use `deploy-frontend-env`, which redeploys at
  the end.

## Prerequisites

- A site already live on a supported host, and how it is deployed (Git-connected
  or the host's command-line tool). If unsure, look for the host's link folder
  (`.vercel/`, `.netlify/`) or a deploy workflow in `.github/workflows/`, and
  ask.

## Instructions

1. **See what changed.** Run `git status --porcelain` and `git log` against the
   remote to list unsaved and unpushed changes. Describe them in plain words
   ("you changed the homepage text and added a contact page"). If there are
   none, say so.

2. **Build locally.** Run the project's build (as `deploy-frontend-check` does,
   reading the scripts first). If the change adds a new environment variable
   name, a new page that needs a routing rule, or a file whose name differs only
   by case from an import, catch it now. If the build fails, stop and offer to
   fix it before anything is deployed. For a larger change, offer the full
   `deploy-frontend-check`.

3. **Choose preview first or straight to production.** Explain in plain words: a
   **preview** is a test copy at its own address; **production** is the live
   site visitors see. Recommend a preview first for anything bigger than a text
   fix, where the host offers it:
   - **Vercel, Netlify, Cloudflare Pages with Git:** push to a branch other than
     the production branch to get a preview address. On Netlify, a branch alone
     gets one only if branch deploys are turned on; otherwise also open a pull
     request (a request on GitHub to merge that branch), which gets a deploy
     preview.
     With `gitly-branches` the user can make that branch in plain words.
   - **With the host's command-line tool:** Vercel `vercel deploy`; Netlify
     `netlify deploy` (a draft); Cloudflare Pages
     `wrangler pages deploy <dir> --project-name <name> --branch <preview-branch>`.
     Check the upload list for secret files first, as the platform guide says.
   - **GitHub Pages** has no previews: check the change locally instead (for Vite,
     `npm run build` then `npm run preview`).
   A first preview is still a public address; ask before creating it.

4. **Check the preview.** Open the preview address and check it as in
   [DEPLOY.md](../DEPLOY.md), section 4, focusing on what changed. A host login
   wall on a preview is the host protecting it; that is fine. Report what works
   and anything that looks wrong.

5. **Ask before publishing to production.** In one or two sentences: what will
   change for visitors, and how to undo it (`deploy-frontend-rollback`). Wait for
   a yes. A yes for this update does not cover the next one.

6. **Publish.**
   - **Git-connected:** save and push to the production branch with Gitly
     (`gitly-save`, then `gitly-sync`), or merge the preview branch with
     `gitly-merge` and push. The host builds and publishes by itself.
   - **Command-line tool:** Vercel `vercel deploy --prod`; Netlify
     `netlify deploy --prod`; Cloudflare Pages `wrangler pages deploy` with the
     production branch. Check the upload list first. Never add flags that skip
     confirmations.
   Watch the build to the end.

7. **Check the live site.** As in [DEPLOY.md](../DEPLOY.md), section 4: the
   production address works, shows the new version (check something that
   changed), and the main pages still open directly. If something broke, say so,
   and offer `deploy-frontend-rollback` to get visitors back to the working
   version while you investigate with `deploy-frontend-fix`.

8. **Report.** What is live now, what you checked, and the preview address if
   one was used. Remind the user that changing a setting on the host needs a new
   deploy to take effect.

## Examples

**User:** "I changed the homepage and added a contact page. Put it online."

**Agent:** Lists the changes, builds locally (passes), and notices the new
`/contact` route works on Netlify thanks to the existing `_redirects` rule.
Recommends a preview: creates a branch with `gitly-branches`, and with a yes
saves and pushes it, and opens a pull request. Checks the deploy preview address, including `/contact`.
Asks before publishing; with a yes, merges into `main` and pushes. Watches the
production deploy and confirms the live homepage shows the new text and
`/contact` opens directly.

**User:** "תעדכן את האתר באוויר, שיניתי רק טקסט"

**Agent:** Answers in Hebrew. Sees one changed text file, builds locally, and
since the site is on GitHub Pages (no previews), checks it with
`npm run preview`. Asks before publishing, then saves and pushes with Gitly,
watches the Actions run, and confirms the live site shows the new text.

**User:** "Deploy my site for the first time."

**Agent:** Explains this is a first launch and uses `deploy-frontend-launch`
instead.
