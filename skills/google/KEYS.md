# Google keys: what each one is, where it may live, how to lock it

Every google skill uses this page. Read [GOOGLE.md](GOOGLE.md) first.

## The kinds of Google credentials

| Credential | Looks like | Secret? | May it reach the browser? |
| --- | --- | --- | --- |
| **API key** (Maps, Places, Gemini and others) | starts with `AIza`, about 39 characters | Yes, unless restricted to your sites | Only Maps and Firebase web keys, and only when restricted. Never a Gemini key. |
| **Firebase web config** (`apiKey`, `projectId`, `appId` and so on) | an object in the app's code | Not by itself. Firebase's security comes from its rules. | Yes, by design. Still restrict the key to the APIs Firebase needs. |
| **OAuth client ID** | ends with `.apps.googleusercontent.com` | No | Yes |
| **OAuth client secret** | starts with `GOCSPX-` | Yes | Never |
| **Service account key** (a JSON file) | has `"type": "service_account"` and a `private_key` | Yes, very | Never |
| **GA4 Measurement ID** | starts with `G-` | No | Yes, by design |

The Firebase guide on its keys:
<https://firebase.google.com/docs/projects/api-keys>.
Google's guide to API keys: <https://cloud.google.com/docs/authentication/api-keys>.

## Where each one lives

- **Server-only secrets** (Gemini key, OAuth client secret, service account
  key): a `.env` file on the user's computer that Git ignores, and the host's
  secret settings for the live site (`deploy-frontend-env` does that part). The
  name must **not** start with a public prefix.
- **Public values** (Maps key, Firebase web config, OAuth client ID, GA4 ID):
  may use a public prefix so the framework sends them to the browser.

Public prefixes, which mean "send this to every visitor":

| Framework | Public prefix |
| --- | --- |
| Next.js | `NEXT_PUBLIC_` |
| Vite (React, Vue, Svelte) | `VITE_` |
| SvelteKit | `PUBLIC_` |
| Astro | `PUBLIC_` |
| Create React App | `REACT_APP_` |
| Expo | `EXPO_PUBLIC_` |
| Nuxt | values under `runtimeConfig.public` |

A secret with a public prefix, or used in a file that runs in the browser, is
leaked to everyone who opens the site. Stop and fix that before anything else.

Names the skills in this package suggest:

| Name | Holds | Public? |
| --- | --- | --- |
| `GEMINI_API_KEY` | Gemini key | No |
| `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET` | OAuth client for Auth.js v5 | The ID may be public; the secret never |
| `GOOGLE_SERVICE_ACCOUNT_EMAIL`, `GOOGLE_PRIVATE_KEY` | service account for Sheets | No |
| `<prefix>GOOGLE_MAPS_API_KEY` | Maps key | Yes, restricted |
| `<prefix>GA_MEASUREMENT_ID` | GA4 ID | Yes |

Use the names the project already has when they exist.

## Restrict every key

An unrestricted key works for anyone, from anywhere, on every API the project
has turned on. Every key gets **both** kinds of restriction:

1. **Who may use it (application restriction).**
   - A key used in the browser: **websites** (HTTP referrers). List the live
     domain and the local address, for example `https://my-site.com/*`,
     `https://www.my-site.com/*` and `http://localhost:3000/*`. Add the host's
     preview addresses only if the user needs the feature in previews.
   - A key used only on a server: **IP addresses** if the server has a fixed
     address. Most hosts for vibe coders (Vercel, Netlify) do not, so the key
     stays unrestricted here, and the API restriction, a budget alert and
     keeping it secret are what protect it.
   - Android and iOS apps have their own restriction types.
2. **Which APIs it may call (API restriction).** Only the APIs this key is for,
   for example "Maps JavaScript API" and "Places API (New)".

Use one key per job (one for Maps in the browser, another for a server API), so
each can be restricted tightly and replaced on its own.

Official guides:
- <https://cloud.google.com/docs/authentication/api-keys#adding-api-restrictions>
- <https://developers.google.com/maps/api-security-best-practices>

For a Gemini key made in Google AI Studio, the key also appears in the linked
Google Cloud project's credentials list, where the API restriction can be
checked.

## Check restrictions without seeing the key

If the user already uses the Google Cloud command-line tool (`gcloud`) and is
logged in, this lists each key's name and restrictions. It does not print the
key strings:

```bash
gcloud services api-keys list --project=<PROJECT_ID> --format="yaml(displayName,restrictions)"
```

A key with no `restrictions` block is unrestricted. A key with only
`apiTargets` has an API restriction but no website or IP restriction.

Do not install `gcloud` or log the user in just for this, unless they ask. The
other way is to have the user open the Credentials page and read back, for each
key, its name, its application restriction type, the allowed sites, and the
allowed APIs. Never the key itself.

## Show a found key masked

When you must point at a key in a file, print only its first and last 4
characters, for example:

```bash
grep -rnoE 'AIza[0-9A-Za-z_-]{35}' --exclude-dir=node_modules --exclude-dir=.git . \
  | sed -E 's/(AIza)[0-9A-Za-z_-]{31}([0-9A-Za-z_-]{4})/\1...\2/'
```

## If a key leaked

A key that was committed to Git, deployed in a public setting, or pasted into a
chat should be treated as known to others, even if the commit was removed.

1. Tell the user, masked, where it was found.
2. With their yes, they create a new key with the same restrictions, put it in
   `.env` and on the host, and check that the app works.
3. Then they delete the old key in the console. Deleting is their action, after
   a yes, because anything still using the old key stops working.
4. Removing it from Git history is a separate job. Suggest `secret-guard`.
