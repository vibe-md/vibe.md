---
name: google-sheets
description: Uses a Google Sheet as a simple database or as the place a website form sends its entries, safely. Sets up a service account (a robot Google account) with no project roles, shares only that one Sheet with it, keeps its key on the server in environment variables typed by the user, and adds a server route that validates input, limits requests, writes rows as plain text so formulas cannot be injected, and reads with the narrowest access. Explains when a Sheet stops being a good database. Ends by writing and reading a test row. Use when the user says "save my form to a Google Sheet", "use Google Sheets as a database", "read data from a Google Sheet on my site", "contact form to Google Sheets", "תשמור את הטופס בגוגל שיטס", or "תחבר את האתר לגוגל שיטס". Not for exporting files by hand, not for Google Forms itself, and not for a real database (use Firestore with google-firebase, or Supabase).
license: MIT
compatibility: Needs read and write access to the project, a Google Cloud project (no billing needed for normal use), and an app with server code (API routes, server actions or functions). A static site with no server cannot keep the key secret. The user creates the service account key and types it into .env themselves.
metadata:
  collection: vibe.md
  group: google
---

# Google: Sheets as a simple database or form backend

Read [the shared google contract](../GOOGLE.md) and [the keys guide](../KEYS.md)
first, and follow them.

## Purpose

A Google Sheet is an easy place for a small site to keep form entries or a
short list the owner edits by hand. The safe way to connect it is a **service
account**: a robot Google account the server uses, which can open **only** the
Sheet that was shared with it. Its key is a powerful secret, so it stays on the
server. This skill sets that up with the least access that works.

## When to Use

- The user wants a contact or sign-up form to add rows to a Sheet.
- The user wants the site to show data from a Sheet they edit (a menu, a price
  list, opening hours).
- Examples: "Save my form to a Google Sheet", "Use Google Sheets as my
  database", "Show the menu from my Google Sheet", "תשמור את הטופס בגוגל שיטס",
  "תחבר את האתר לגוגל שיטס".

Do not use this skill:

- when the data is large, private per user, changes many times a second, or
  needs search and relations. Suggest Firestore (`google-firebase`) or another
  real database.
- for a static site with no server code. The key cannot be hidden there.
  Suggest adding a serverless function first, or Google Forms.
- to audit keys already in the project. Use `google-keys-check`.
- to put the keys on the host. This skill names them; `deploy-frontend-env`
  puts them on the host.

## Prerequisites

- A Google Cloud project (`google-setup`). The Sheets API has no charge for
  normal use; check the quota page live for the current request limits:
  <https://developers.google.com/sheets/api/limits>.
- An app with server code: Next.js route handlers or server actions, a Netlify
  or Vercel function, an Express server.

## Instructions

1. **Agree on what goes in the Sheet.** Ask which columns are needed and
   whether the site only **writes** (a form), only **reads** (a menu), or both.
   This decides the access level. Explain the limits in one or two sentences: a
   Sheet is fine for hundreds or thousands of rows edited by one person; it has
   request limits per minute, no per-user privacy, and two writes at once can
   land in any order.

2. **Turn on the Google Sheets API** in the project. Ask first; it has no charge,
   but it is a project change. Verify it is enabled.

3. **Create the service account, with no roles.** Tell the user what to do on
   the **Service Accounts** page in the Google Cloud console: create one named
   for its job, such as "website-sheets". When the console offers to grant it
   roles on the project, **skip that**: it needs none to open a Sheet shared
   with it. A role such as Editor would let its key change the whole project.
   Official guide:
   <https://cloud.google.com/iam/docs/service-accounts-create>. Verify: ask the
   user to check the project's IAM page lists no role for the service account,
   or, with `gcloud`, run the read-only
   `gcloud projects get-iam-policy <PROJECT_ID> --flatten="bindings[].members" --filter="bindings.members:<SERVICE_ACCOUNT_EMAIL>" --format="value(bindings.role)"`,
   which should print nothing.
   Its email looks like `website-sheets@<project-id>.iam.gserviceaccount.com`
   and is not a secret.

4. **Share only that one Sheet with it.** For a form, use a Sheet that holds
   only the form's rows, not one with other business data, because a robot
   with Editor access can change or clear everything in it. The user opens the
   Sheet, presses Share, and adds the service account email:
   - **Viewer** if the site only reads.
   - **Editor** if the site writes.
   Turn off "Notify people". In the Share settings, also turn off "Editors can
   change permissions and share", so the robot cannot share the Sheet onward.
   Do not make the Sheet "Anyone with the link" just for this.

5. **Create the key and put it in `.env`, typed by the user.** Explain that this
   key lets anyone who has it act as the robot. With a yes:
   - The user creates a JSON key on the service account's **Keys** tab. Some
     organizations block this; if the console refuses, say so and stop, because
     the workaround is the organization admin's decision.
   - The user opens the downloaded file **themselves** and copies two values
     into `.env.local` (check `.gitignore` covers it first):
     `GOOGLE_SERVICE_ACCOUNT_EMAIL` (the `client_email`) and
     `GOOGLE_PRIVATE_KEY` (the `private_key`, in quotes, with its `\n` kept as
     written). Also `GOOGLE_SHEET_ID`, the long ID in the Sheet's address,
     which is not a secret.
   - Then they move the JSON file out of the project folder, or delete it.
   You do not open the JSON file. Verify the three names with the names-only
   command, and that no `*.json` key file is left in the project
   (`google-keys-check` step 2 finds them).
   None of these names may have a public prefix.

6. **Write the server code, with a yes.** Show the plan first, then:
   - Use the `googleapis` package (or `google-auth-library` with
     `google-spreadsheet`) **in server code only**, never in a component that
     runs in the browser.
   - Authenticate with a JWT from the two variables, turning `\n` back into new
     lines (`key.replace(/\\n/g, "\n")`), and the narrowest scope:
     `https://www.googleapis.com/auth/spreadsheets.readonly` for read-only,
     `https://www.googleapis.com/auth/spreadsheets` only if it writes.
   - For a form: a route that checks every field (type, length, required),
     rejects anything else, adds a simple rate limit per visitor (for example
     a few submissions per minute per IP), and a hidden "honeypot" field to stop
     simple bots. Append with `valueInputOption: "RAW"`, never
     `"USER_ENTERED"`: with `RAW`, Google stores a value such as
     `=IMPORTXML(...)` as plain text, so it does not run in the Sheet. A value
     that starts with `=`, `+`, `-`, `@`, a tab or a line break can still run as
     a formula if the owner later downloads the Sheet and opens it in Excel, so
     for free-text fields the route removes those characters from the start of
     the value. A phone field may keep a leading `+` followed only by digits and
     spaces.
   - For reading: fetch on the server, and cache for a short time (for example
     a minute) so every page view is not a Sheets request. Show cell values as
     text, never as HTML, especially if visitors can write to the same Sheet.
   - Errors: log a short message on the server, never the key, and show the
     visitor a plain "Something went wrong, please try again".
   Docs: <https://developers.google.com/sheets/api/guides/values>.

7. **Test.** Run the dev server. For a form, with a yes (it writes to the
   real Sheet), submit a test entry (marked "TEST") and ask the user to confirm
   the row appears, then delete it themselves. For reading, check the page shows the Sheet's data. Also try one
   bad submission and confirm it is rejected.

8. **Live site.** Hand off to `deploy-frontend-env` to put the three names on
   the host (as secret values; the private key must keep its `\n`), deploy, and
   repeat the test on the live site.

9. **Report.** What the robot can open (one Sheet, Viewer or Editor), where its
   key lives, what the route checks, and a reminder: service account keys do
   not expire, so the user should delete it in the console when the feature is
   removed, and replace it if it ever leaks ([KEYS.md](../KEYS.md)).

## Examples

**User:** "Save my contact form to a Google Sheet. It's a Next.js site on
Vercel."

**Agent:** Agrees on columns (name, email, message, date). Has the user turn on
the Sheets API, create "website-sheets" with no roles, share the Sheet with it
as Editor, and copy the email and private key into `.env.local` themselves.
Checks the names. With a yes, adds a route handler that validates fields, rate
limits, has a honeypot, and appends with `RAW`. Submits a "TEST" row; the user
sees it and deletes it. Hands off to `deploy-frontend-env` for Vercel.

**User:** "תציג באתר את התפריט מגוגל שיטס"

**Agent:** Answers in Hebrew. Since the site only reads, shares the Sheet as
Viewer and uses the read-only scope. Reads it on the server with a one-minute
cache, and checks the menu page shows the rows.

**User:** "Can't I just call the Sheets API from the browser with an API key?"

**Agent:** Explains that only works for Sheets anyone can read, and that writing
from the browser would need the robot's key in the page, where anyone could take
it and change or delete the Sheet. Recommends the server route.
