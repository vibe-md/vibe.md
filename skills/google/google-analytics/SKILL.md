---
name: google-analytics
description: Adds Google Analytics 4 (GA4) to a website with a simple cookie consent banner, so visits are counted only after a visitor agrees. Creates the GA4 property and web stream with the user, puts the measurement ID in an environment variable, loads Google's tag only after consent using Consent Mode, adds an accessible banner with equal Accept and Reject buttons and a way to change the choice later, and checks that visits show up in Realtime. Explains in plain words what consent laws generally ask for, without giving legal advice. Use when the user says "add Google Analytics", "add GA4", "how many people visit my site?", "I need a cookie banner for analytics", "Analytics shows no data", "תוסיף גוגל אנליטיקס לאתר", or "תוסיף באנר עוגיות". Not for Google Ads or ad tracking pixels, not for Search Console data (use google-search-console), and not for other analytics tools.
license: MIT
compatibility: Needs read and write access to the project and a Google account. Works with Next.js, React and Vite apps, Astro, and plain HTML. The user creates the property in Google Analytics; the agent explains and checks.
metadata:
  collection: vibe.md
  group: google
  author: NirGeron98
---

# Google: Analytics (GA4) with consent

Read [the shared google contract](../GOOGLE.md) first, and follow it.

## Purpose

Google Analytics counts visits and shows where visitors come from. In many
places (for example the EU and the UK), sites must ask
before setting analytics cookies. This skill adds GA4 so that **nothing loads
until the visitor says yes**, with a simple banner, and checks that data
arrives.

## When to Use

- The user wants visitor numbers or GA4 on their site.
- The user needs a cookie banner for analytics.
- GA4 shows no data, or shows data before anyone agreed.
- Examples: "Add Google Analytics to my site", "Add GA4 to my Next.js app", "How
  many people visit my site?", "I need a cookie banner", "תוסיף גוגל אנליטיקס
  לאתר", "תוסיף באנר עוגיות".

Do not use this skill:

- for Google Ads conversion tracking or ad pixels.
- for search rankings and indexing. Use `google-search-console`.
- for legal advice. Say plainly this is not legal advice, and that a business
  with legal questions should ask a lawyer.

## Prerequisites

- A Google account. GA4 has no charge for normal use; it does not need a Google
  Cloud project or billing.
- The site's live address.

## Instructions

1. **Check what is there.** Look for an existing `gtag(`, `G-` ID,
   `googletagmanager.com`, `@next/third-parties`, Google Tag Manager (`GTM-`),
   or another consent tool (Cookiebot, Osano and similar). If one exists, work
   with it instead of adding a second tag or banner.

2. **Create the property and stream with the user.** Tell them what to do at
   <https://analytics.google.com/>: create a GA4 **property** for the site,
   then a **Web data stream** with the live address. Google then shows a
   **Measurement ID** starting with `G-`. It is not a secret. Official guide:
   <https://support.google.com/analytics/answer/9304153>. Keep "Enhanced
   measurement" on; it counts page changes in single-page apps too.

3. **Put the ID in an environment variable, with a yes.** Use the public prefix,
   for example `NEXT_PUBLIC_GA_MEASUREMENT_ID` or `VITE_GA_MEASUREMENT_ID`.
   The user may paste this ID in the chat; it is public. Check the name is set.

4. **Add the consent banner, with a yes.** Keep it small and plain:
   - One sentence on what is collected and why, a link to the privacy policy,
     and two buttons of equal size and weight: **Accept** and **Reject**.
   - Store the choice (for example in `localStorage` as `analytics-consent`),
     and do not show the banner again once chosen.
   - A "Cookie settings" link in the footer that shows the banner again, so the
     visitor can change their mind.
   - Accessible: a labelled region, buttons reachable by keyboard, visible
     focus, enough contrast in light and dark themes.
   Do not hide Reject, pre-tick anything, or block the page until a choice is
   made.

5. **Load GA4 only after Accept, with Consent Mode, with a yes.**
   - Before any Google tag, set the defaults to denied:
     `gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' })`.
   - Load the Google tag (`https://www.googletagmanager.com/gtag/js?id=...`)
     **only after** the visitor accepts, or on a later visit when the stored
     choice is Accept. Then call
     `gtag('consent', 'update', { analytics_storage: 'granted' })` and
     `gtag('config', '<id>')`. Leave the ad settings denied unless the user
     runs ads and asks.
   - On Reject, load nothing.
   - In Next.js, the `GoogleAnalytics` component from `@next/third-parties/google`
     can be rendered only when consent is granted. Docs:
     <https://nextjs.org/docs/app/guides/third-party-libraries#google-analytics>.
   Consent Mode docs:
   <https://developers.google.com/tag-platform/security/guides/consent>.

6. **Verify.**
   - In the browser (a browser tool if you have one, otherwise ask the user),
     open the site with a fresh profile or private window: before choosing,
     the network list shows **no** request to `googletagmanager.com` or
     `google-analytics.com`.
   - Click Reject and reload: still none.
   - Clear the choice, click Accept: the tag loads and a `collect` request is
     sent.
   - Ask the user to open GA4's **Realtime** report and confirm the visit
     appears (it can take a minute). For more detail, Google's Tag Assistant
     (<https://tagassistant.google.com/>) shows the consent state.

7. **After deploying, check again on the live site** (the variable must be on
   the host; hand off to `deploy-frontend-env`). Report what you checked.

## Examples

**User:** "Add Google Analytics to my Next.js site."

**Agent:** Finds no existing tag. Walks the user through creating the property
and web stream; the user shares the `G-` ID. Adds
`NEXT_PUBLIC_GA_MEASUREMENT_ID`, a small banner with Accept and Reject and a
footer link, and renders `GoogleAnalytics` only after Accept. Checks in the
browser that nothing loads before a choice or after Reject, and that Accept
sends a request. The user sees the visit in Realtime.

**User:** "תוסיף באנר עוגיות לאנליטיקס"

**Agent:** Answers in Hebrew. Finds GA4 already loaded on every page without
consent. Explains why that is a problem in plain words, without legal advice,
and with a yes moves the tag behind a consent banner. Verifies nothing loads
before Accept.

**User:** "Analytics shows zero visitors."

**Agent:** Checks the ID variable is set on the host, that the stream's address
matches the site, and whether the tag only loads after consent (then visitors who
reject are not counted, which is expected). Opens the site, accepts, and has the
user watch Realtime.
