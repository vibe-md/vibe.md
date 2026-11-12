---
name: deploy-frontend-rollback
description: Undoes a bad deploy of a website by switching the live site back to the last version that worked, then checks the live address. Finds the earlier working deployment on the host, explains what will change, and with the user's yes promotes or restores it using the host's own rollback (Vercel, Netlify, or Cloudflare Pages) or by re-running or reverting through Git (GitHub Pages, or any Git-connected site), and says how new pushes behave afterwards. Use when the user says "my site broke after the last update", "put the previous version of my site back online", "undo the deploy", "roll back my site", "תחזיר את האתר לגרסה הקודמת", or "האתר נשבר אחרי העדכון, תבטל". Not for finding the cause of a failure (use deploy-frontend-fix afterwards), not for restoring code files on the computer (use gitly-restore), and not for backend servers or databases.
license: MIT
compatibility: Needs network access and the user logged in to their hosting service (dashboard, or its command-line tool). Reverting through Git needs Git and, for the push, the Gitly skills or equivalent. Uses curl to verify the live site.
metadata:
  collection: vibe.md
  group: deploy
---

# Deploy: roll back a bad deploy

Read [the shared deploy contract](../DEPLOY.md) and
[the frontend track guide](../FRONTEND.md) first, and follow them. Each host
rolls back differently; read "Rolling back" in its guide:
[Vercel](../VERCEL.md), [Netlify](../NETLIFY.md),
[Cloudflare Pages](../CLOUDFLARE-PAGES.md), or
[GitHub Pages](../GITHUB-PAGES.md).

## Purpose

When an update breaks a live site, the first job is to get visitors back to a
working site, quickly and without guessing. The fix can come after. This skill
switches the live site back to the last version that worked, checks that it
really works again, and leaves the user knowing what happens with their next
update.

## When to Use

- The live site broke after a deploy, and the user wants the previous version
  back.
- The user published something by mistake and wants the earlier version live
  again.
- Examples: "My site broke after the last update, go back", "Undo the deploy",
  "Roll back my site", "תחזיר את האתר לגרסה הקודמת", "האתר נשבר אחרי העדכון,
  תבטל".

Do not use this skill:

- to find out why the deploy broke. Roll back first if needed, then use
  `deploy-frontend-fix`.
- to undo changes to files on the user's computer. Use `gitly-restore`.
- to take a site offline entirely or delete deployments. Deleting needs its own
  explicit yes and is not a rollback.
- for backend servers or databases. Say they are planned for later tracks.

## Prerequisites

- The site is on a supported host, and the user can log in to it.
- At least one earlier deployment that worked.

## Instructions

1. **Confirm what is wrong now.** Check the live production address
   (`curl -sS -L -o /dev/null -w "%{http_code}\n" "<url>"`, and the page
   content) so you know the starting point and can tell later whether the
   rollback helped. Ask the user what broke and roughly when it last worked.

2. **Find the last good deployment.** List recent production deployments with
   the host's way from its platform guide: Vercel `vercel list` or the
   dashboard's Deployments; Netlify the dashboard's Deploys list; Cloudflare
   Pages the dashboard's Deployments, or
   `wrangler pages deployment list --project-name <name>`; GitHub Pages the
   Actions tab's runs of the deploy workflow. Match them to what the user
   remembers (time, commit message). Show the candidates and agree on one.
   Only a deployment that built successfully can be a target; on Cloudflare
   Pages only production deployments can.

3. **If the bad deploy exposed a secret or private data**, say clearly that a
   rollback does not remove it: the bad deployment usually stays reachable at
   its own address, and the code stays in Git's history on GitHub. The key must
   be replaced at its provider (suggest `secret-guard`). Deleting the bad
   deployment is a separate deletion that needs its own yes
   ([DEPLOY.md](../DEPLOY.md)).

4. **Explain and ask.** In two or three sentences: which version will become
   live, that visitors will see it within moments, what happens to the next
   push (see step 6), and how to undo the rollback. Wait for a clear yes.

5. **Roll back, using the host's own mechanism:**
   - **Vercel:** `vercel rollback <deployment-url>` or
     `vercel promote <deployment-url>`, or the dashboard's rollback or promote
     option on that deployment. Never add `--yes`.
   - **Netlify:** the dashboard's Deploys list, open the deployment, **Publish
     deploy**.
   - **Cloudflare Pages:** the dashboard's Deployments, the deployment's menu,
     **Rollback to this deployment**.
   - **GitHub Pages:** in the Actions tab, open the last good deploy run and
     choose **Re-run all jobs**; the re-run rebuilds that same commit. Or revert
     the bad change in Git (step 7).

6. **Explain what happens to new pushes.** Hosts differ, and the rules change,
   so read the host's current docs and tell the user:
   - On Vercel, after a rollback, new pushes may stop going live by themselves
     until a deployment is promoted again.
   - On Netlify, check whether publishing an older deploy pauses automatic
     publishing.
   - On GitHub Pages and Cloudflare Pages, the next push to the production
     branch publishes that push, bad change included, unless the change is
     reverted first.

7. **Make it durable when needed.** If the next push would bring the bad version
   back, offer to undo the bad change in Git: `gitly-restore` (or `git revert`
   of the bad commit, which keeps history), then `gitly-save` and `gitly-sync`,
   each with the user's yes since the push publishes the site. If Gitly is not
   installed, explain the steps and ask.

8. **Verify.** As in [DEPLOY.md](../DEPLOY.md), section 4: the production address
   returns a success status, shows the user's site at the expected version
   (check something that differs between the versions if possible), and the main
   pages open directly. On GitHub Pages with the `404.html` copy, inner routes answer 404 by
   design; check them as the GitHub Pages guide's "Single-page app routing"
   says, not as a failure.
   If it still looks broken, the problem may not be the
   code: a changed environment variable, an outside service, or the browser's
   cache. Say so and offer `deploy-frontend-fix`.

9. **Report.** Which version is live now, what you checked, what the next push
   will do, and the suggested next step: finding the cause with
   `deploy-frontend-fix` before deploying again.

## Examples

**User:** "My site broke after the last update, go back to yesterday's version."

**Agent:** Checks the live address: it returns 200 but the home page throws an
error. Lists Vercel deployments, finds yesterday's production deployment, and
asks to roll back to it, explaining that new pushes may not go live by
themselves afterwards. With a yes, runs `vercel rollback <url>`, verifies the
address shows yesterday's version and that `/shop` loads, and suggests
`deploy-frontend-fix` to find the bug before the next deploy.

**User:** "האתר ב-GitHub Pages נשבר אחרי הדחיפה האחרונה, תחזיר אותו"

**Agent:** Answers in Hebrew. Finds the last successful deploy run in the Actions
tab before the bad push. Explains that re-running it brings that version back,
but the next push will publish the bad change again, so it also offers to revert
the commit. With a yes for each step, re-runs the old workflow run, checks the
live site, then reverts the commit with `gitly-restore`, saves and pushes with a
yes, and checks again after the new run.

**User:** "Restore the old version of my index.js file."

**Agent:** Explains that this is about a file on the computer, not the live site,
and suggests `gitly-restore`.
