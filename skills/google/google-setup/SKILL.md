---
name: google-setup
description: Gets a Google Cloud project ready before any Google service is added to a website or app. Creates or picks the project, explains in plain words what is free and what can cost money (reading current prices live), sets a budget with email alerts before any paid API is turned on, turns on only the APIs the app needs, and records the project ID. Asks before linking billing or anything that can cost money, and never asks for card details or keys in the chat. Use when the user says "set up Google Cloud", "I need a Google API key", "will Google charge me?", "set a budget alert on Google", "תגדיר לי פרויקט ב-Google Cloud", or when another google-* skill needs a project or budget first. Not for adding a specific feature (use google-sign-in, google-maps, google-gemini and the other google-* skills) and not for deploying the site (use deploy-frontend-launch).
license: MIT
compatibility: Needs a Google account and a web browser. The user does the console steps; the agent explains and checks. Uses the Google Cloud command-line tool (gcloud) only if the user already has it and is logged in.
metadata:
  collection: vibe.md
  group: google
  author: NirGeron98
---

# Google: set up the project and the budget

Read [the shared google contract](../GOOGLE.md) and [the keys guide](../KEYS.md)
first, and follow them.

## Purpose

Every Google service lives inside a **Google Cloud project**: one folder that
holds the app's keys, settings and bill. This skill gets that project ready the
safe way, so that the first surprise is never a bill. The other google skills
start here when the user has no project or no budget alert yet.

## When to Use

- The user wants to add any Google service and has no Google Cloud project, or
  is not sure which one to use.
- The user asks what Google will charge, or whether a service is free.
- Another google skill is about to turn on an API that can cost money and the
  project has no budget alert.
- Examples: "Set up Google Cloud for my app", "I need a Google API key", "Will
  Google charge me for Maps?", "Set a budget alert on Google", "תגדיר לי פרויקט
  ב-Google Cloud".

Do not use this skill:

- to add a feature itself. Hand off to `google-sign-in`, `google-maps`,
  `google-firebase`, `google-analytics`, `google-search-console`,
  `google-sheets` or `google-gemini` once the project is ready.
- to audit existing keys. Use `google-keys-check`.
- to put the site online. Use `deploy-frontend-launch`.

## Prerequisites

- A Google account the user is happy to own the project with. For a business,
  suggest a shared work account rather than a personal one, so the project does
  not depend on one person.
- A browser. A payment card only if a paid service is needed, and only entered
  by the user on Google's own page.

## Instructions

1. **Find out what the app needs.** Ask which Google features they want (login,
   maps, AI, a Sheet, analytics, search). Look in the project for existing
   Google use: a `firebase.json` or `.firebaserc` file, `@react-oauth/google`,
   `next-auth` or `@auth/*` with a Google provider, `@googlemaps/*`,
   `@google/genai`, `googleapis`, a `G-` measurement ID. Read `.env` files for
   names only ([GOOGLE.md](../GOOGLE.md), section 3). If a project ID is already
   there (often in `.firebaserc` or a variable such as `GOOGLE_CLOUD_PROJECT`),
   ask whether to use that project.

2. **Explain the cost picture before anything else.** Read the current pricing
   pages live for the services they want ([GOOGLE.md](../GOOGLE.md), section 5)
   and summarize in plain words, with the address and date:
   - What needs no billing at all. For example, "Log in with Google", Search
     Console and Google Analytics do not charge for normal use.
   - What needs a billing account even to start, with free monthly use. For
     example, Maps and Places.
   - What has a free tier with conditions. For example, the Gemini API's free
     tier and the Firebase no-cost (Spark) plan, and what changes on the
     pay-as-you-go (Blaze) plan.
   Pricing pages to start from: <https://cloud.google.com/pricing>,
   <https://mapsplatform.google.com/pricing/>,
   <https://ai.google.dev/gemini-api/docs/pricing>,
   <https://firebase.google.com/pricing>.

3. **Create or pick the project.** Tell the user what to do in the Google Cloud
   console (<https://console.cloud.google.com/>): open the project picker at the
   top, and create a new project with a clear name such as "my-bakery-site".
   Explain that the **project ID** (lowercase, sometimes with numbers added) is
   what code and tools use, and cannot be changed later. Official guide:
   <https://cloud.google.com/resource-manager/docs/creating-managing-projects>.
   If the app uses Firebase, the user may instead create the project in the
   Firebase console (<https://console.firebase.google.com/>); it is the same
   Google Cloud project underneath. Ask the user to tell you the project ID (it
   is not a secret) and note it for the next steps.

4. **Billing, only if needed and only with a yes.** If no service they want
   needs billing, skip this step and say so. If one does, explain what linking
   billing means (the project can now charge the card for use beyond the free
   amounts), and ask. With a yes, the user links or creates a billing account on
   the project's Billing page. They enter card details on Google's page only.
   Official guide: <https://cloud.google.com/billing/docs/how-to/modify-project>.

5. **Set a budget with alerts.** Whenever billing is linked, before any paid API
   is turned on:
   - Explain: "A budget sends you emails as spending passes the amounts you
     choose. It does not stop spending. Restricted keys and limits in your app
     do that part."
   - Ask the user for a monthly amount they would be unhappy to go past (a small
     number such as 10 or 20 in their currency is common for a new app).
   - Tell them what to do on the billing account's **Budgets and alerts** page:
     create a budget scoped to this project, with that amount, alerts at about
     50%, 90% and 100% of actual spend, and emails to the billing admins.
     Official guide: <https://cloud.google.com/billing/docs/how-to/budgets>.
   - Verify: ask them to read back the budget name, amount, scope and alert
     levels. If they use `gcloud`, you can list budgets with
     `gcloud billing budgets list --billing-account=<BILLING_ACCOUNT_ID>`
     (read-only; the billing account ID is not a secret).

6. **Turn on only the APIs the app needs.** List each one by its name in the API
   Library, for example "Maps JavaScript API", "Places API (New)", "Google Sheets
   API". Ask before turning on any that can charge money. Official guide:
   <https://cloud.google.com/apis/docs/getting-started#enabling_apis>. Verify by
   having the user confirm each is enabled, or, with `gcloud`,
   `gcloud services list --enabled --project=<PROJECT_ID>`.

7. **Write down the setup.** With the user's yes, add a short section to the
   project's README (or a `docs/google.md`) with: the project ID, which Google
   account owns it, which APIs are on, where the budget is, and which
   environment variables the app uses (names only). Never write a key or
   secret there.

8. **Hand off.** Say which google skill does the next part, for example
   `google-maps` for the map, and that it will create and restrict its own key.

## Examples

**User:** "I want to add Google Maps to my site. Will it cost me money?"

**Agent:** Opens the Maps pricing page and reports what it says today, with the
address and date: a billing account is required, and there is a free monthly
amount per type of request. Helps the user create the project "bakery-site",
asks before billing is linked, then walks them through a budget of 15 with
alerts at 50, 90 and 100 percent, and has them read the budget back. Turns on
the Maps JavaScript API after a yes, records the project ID in the README, and
hands off to `google-maps`.

**User:** "תגדיר לי פרויקט ב-Google Cloud בשביל התחברות עם גוגל"

**Agent:** Answers in Hebrew. Explains that "Log in with Google" does not need a
billing account, so it skips billing and the budget, and says it will set one
up later if they add a paid service. Helps create the project, notes the
project ID, and hands off to `google-sign-in`.

**User:** "Here is my card number, just set up billing for me."

**Agent:** Asks them not to share card details in the chat, and explains that
they enter them only on Google's own billing page. Then explains the steps.
