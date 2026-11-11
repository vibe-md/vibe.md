---
name: google-maps
description: Adds Google Maps to a website or app, safely. Shows a map or a store location, searches places, and autocompletes addresses in forms, using the Maps JavaScript API and Places API (New), or the free embed when a simple map is enough. Creates a separate key restricted to the user's own domains and to only the Maps APIs used, keeps it in an environment variable, explains costs from the live pricing page, checks there is a budget alert, and can lower daily quotas. Verifies the map loads with no key errors. Use when the user says "add a Google map", "show our location on a map", "address autocomplete", "search places", "RefererNotAllowedMapError", "the map says for development purposes only", "תוסיף מפה של גוגל לאתר", or "השלמה אוטומטית לכתובת". Not for Google Earth, mobile SDKs, or other map providers.
license: MIT
compatibility: Needs read and write access to the project, a Google Cloud project with billing and a budget alert (google-setup), and network access for the live pricing and docs. Works with plain HTML, React, Next.js, Vue and similar web apps.
metadata:
  collection: vibe.md
  group: google
  author: NirGeron98
---

# Google: maps, places and address autocomplete

Read [the shared google contract](../GOOGLE.md) and [the keys guide](../KEYS.md)
first, and follow them.

## Purpose

A Maps key has to be sent to the browser, so anyone can read it from the page.
That is fine **only** when the key is restricted to the user's own site and to
the Maps APIs the site uses; otherwise someone else can use it and the user
pays. This skill adds the map or the address search, and locks the key down
before the site goes live.

## When to Use

- The user wants a map on a page, a store or event location, a list of places
  near the user, or address autocomplete in a form.
- A map shows an error, a grey box, or "For development purposes only".
- Examples: "Add a Google map to the contact page", "Show our shop on a map",
  "Autocomplete the address field", "RefererNotAllowedMapError", "תוסיף מפה של
  גוגל לאתר", "השלמה אוטומטית לכתובת".

Do not use this skill:

- for mobile apps built with the native Android or iOS Maps SDKs.
- for a full audit of every Google key in the project. Use
  `google-keys-check`.
- to add the variable to the live host. This skill names it;
  `deploy-frontend-env` puts it on the host.

## Prerequisites

- A Google Cloud project with billing linked and a budget alert. If either is
  missing, run `google-setup` first. Maps will not work without billing, even
  for free use.
- The site's local address and live domain.

## Instructions

1. **Pick the smallest option that does the job.** Ask what they need, then
   recommend:

   | Need | Option | Key in browser? | Cost |
   | --- | --- | --- | --- |
   | Show one place on a contact page | **Maps Embed API** (an `<iframe>`) | Yes, restricted | Check the pricing page; it has been free for embeds |
   | An interactive map with markers | **Maps JavaScript API** | Yes, restricted | Charged per map load beyond the free monthly amount |
   | Address autocomplete in a form | **Places API (New)**, Place Autocomplete | Yes, restricted | Charged per session or request beyond the free amount |
   | Search places near a point | **Places API (New)** Text or Nearby Search | Prefer the server | Charged per request |

   Read the current prices live from <https://mapsplatform.google.com/pricing/>
   and tell the user what you read, the address and the date. Docs:
   <https://developers.google.com/maps/documentation>.

2. **Check the budget, then turn on only those APIs.** Confirm a budget alert
   exists ([GOOGLE.md](../GOOGLE.md), section 2). With a yes, the user turns on
   only the APIs chosen in step 1, for example "Maps JavaScript API" and
   "Places API (New)". Not every Maps API.

3. **Create a separate key and restrict it before using it.** Tell the user
   what to do on the Credentials page, or in the Maps "Keys and credentials"
   page: create an API key named for its job, such as "website maps", then
   edit it:
   - **Application restriction: Websites.** Add `https://my-site.com/*`,
     `https://www.my-site.com/*` if used, and `http://localhost:3000/*` (with
     the real port).
   - **API restriction:** only the APIs from step 2.
   Official guide: <https://developers.google.com/maps/api-security-best-practices>.
   Verify as in [KEYS.md](../KEYS.md), "Check restrictions without seeing the
   key". Do not go on until both restrictions are confirmed.

4. **The user puts the key in `.env`.** Use the framework's public prefix,
   because this key must reach the browser, for example
   `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` or `VITE_GOOGLE_MAPS_API_KEY`. Check
   `.gitignore` covers the file, and that the name is present, by name only. The
   key never goes in the code itself.

5. **Add the map, with a yes.** Show the planned change, then:
   - Embed: an `<iframe>` with
     `https://www.google.com/maps/embed/v1/place?key=...&q=...`, the key read
     from the variable at build time, and a `title` attribute for screen
     readers.
   - React or Next.js: the `@vis.gl/react-google-maps` package (`APIProvider`
     and `Map`), which Google's own docs point to. Docs:
     <https://visgl.github.io/react-google-maps/>.
   - Other sites: the loader from Google's docs, or `@googlemaps/js-api-loader`.
   - Markers use Advanced Markers (the older `Marker` is deprecated), which
     always need a **Map ID**. It is created in the console and is not a
     secret. For local work, Google's docs allow `DEMO_MAP_ID`.
   Give the map a fixed height in CSS; a map with no height shows nothing.

6. **Add address autocomplete, with a yes.** Use the current Place Autocomplete
   widget from the Places API (New), as Google's docs show today. Older
   `google.maps.places.Autocomplete` is not offered to new projects. Ask only
   for the fields the form needs (for example the formatted address and the
   location), because extra fields can cost more. Docs:
   <https://developers.google.com/maps/documentation/javascript/place-autocomplete-new>.

7. **Search places on the server when possible.** For text or nearby search,
   call the Places API (New) from a server route with a second key that is
   **not** public and is restricted to Places API (New) only. The browser calls
   your route, not Google. Add a simple per-user limit in that route.

8. **Lower the daily quota, if the user wants a hard cap.** Explain that each
   API has a requests-per-day quota they can set lower on its Quotas page, so a
   flood of traffic stops at that number instead of growing the bill. Ask for
   the number; the user sets it. Official guide:
   <https://cloud.google.com/apis/docs/capping-api-usage>. Verify: ask them to
   read back the new value on the Quotas page.

9. **Verify.** Run the dev server and open the page (with a browser tool if you
   have one, otherwise ask the user). Check the map or autocomplete shows, and
   that the browser console has no Maps error. Then, after deploying
   (`deploy-frontend-env` for the variable), check the live page the same way.

## Fixing common errors

| Message in the browser console or on the map | Meaning | Fix |
| --- | --- | --- |
| `RefererNotAllowedMapError` | The page's address is not in the key's websites list | Add the exact address, with `/*` |
| `ApiNotActivatedMapError` | The API is not turned on in the project | Turn on the API from step 2 |
| `BillingNotEnabledMapError`, or "For development purposes only" | No billing on the project | `google-setup`, billing step |
| `InvalidKeyMapError` | The variable is empty or wrong | Check the name, rebuild after changing it |
| `ApiTargetBlockedMapError` | The key's API restriction leaves out the API used | Add that API to the key |
| Grey or empty box | The map container has no height | Give it a height in CSS |

## Examples

**User:** "Add a Google map with our bakery's location to the contact page."

**Agent:** Recommends the Maps Embed API, since one location is enough, and
checks its pricing live. Confirms a budget alert exists. The user turns on the
Maps Embed API and creates a key "website embed" restricted to
`https://bakery-tlv.com/*` and `http://localhost:5173/*` and to the Maps Embed
API only, and reads the restrictions back. The user adds
`VITE_GOOGLE_MAPS_API_KEY` to `.env`. With a yes, the agent adds the `<iframe>`
with a title, opens the page, and sees the map with no console errors.

**User:** "תוסיף השלמה אוטומטית לשדה הכתובת בטופס ההזמנה"

**Agent:** Answers in Hebrew. Explains that autocomplete is charged after a free
amount, reads the current price live, and checks the budget. Has the user turn
on Places API (New) and restrict the key. Adds the Place Autocomplete widget
asking only for the formatted address, and tests it in the browser.

**User:** "The map works on my computer but the live site says
RefererNotAllowedMapError."

**Agent:** Explains the key's websites list does not include the live address.
Has the user add `https://my-site.com/*` (and the `www` form if used), waits a
few minutes, and checks the live page again.
