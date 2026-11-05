---
name: google-sign-in
description: Adds "Log in with Google" to a website or app, or fixes it when it breaks. Sets up the consent screen and the OAuth client, lists the exact redirect URLs for local and for the live site (the most common break), and wires it into Auth.js (NextAuth), Supabase Auth, Firebase Auth or Clerk with the client secret kept on the server. Ends with a real login test on local and live. Asks before code changes and before publishing the consent screen, and never asks for the client secret in the chat. Use when the user says "add Google login", "sign in with Google", "redirect_uri_mismatch", "Google login works locally but not on my site", "Access blocked, this app's request is invalid", "תוסיף התחברות עם גוגל", or "ההתחברות עם גוגל לא עובדת באתר". Not for email and password login, not for other providers, and not for reviewing who may access what after login (use security-access-regression).
license: MIT
compatibility: Needs read and write access to the project and a Google account. Works with Auth.js v5 and NextAuth v4, Supabase Auth, Firebase Auth and Clerk. The user does the console steps and types every secret themselves; the agent explains and checks.
metadata:
  collection: vibe.md
  group: google
  author: NirGeron98
---

# Google: Log in with Google

Read [the shared google contract](../GOOGLE.md) and [the keys guide](../KEYS.md)
first, and follow them.

## Purpose

"Log in with Google" uses a standard called OAuth. Google shows the user a
consent screen, then sends them back to an address in your app (the redirect
URL) with proof of who they are. Most breaks come from that address not
matching, character for character, what Google has on file. This skill sets it
up right for both the user's computer and the live site, and proves it works.

## When to Use

- The user wants a "Log in with Google" or "Continue with Google" button.
- Google login works on the user's computer but not on the live site, or shows
  `redirect_uri_mismatch`, "Access blocked" or "This app isn't verified".
- The user is moving from a test login setup to production.
- Examples: "Add Google login to my Next.js app", "Sign in with Google with
  Supabase", "I get redirect_uri_mismatch", "תוסיף התחברות עם גוגל",
  "ההתחברות עם גוגל לא עובדת באתר".

Do not use this skill:

- for email and password login, magic links, or other providers.
- to decide who may see which pages after login. Use
  `security-access-regression`.
- to set the variables on the host. This skill names them; `deploy-frontend-env`
  puts them on the host.

## Prerequisites

- A Google Cloud project (`google-setup`). Sign-in does not need billing.
- The app's local address (for example `http://localhost:3000`) and, if it is
  online, its live address (for example `https://my-site.com`).

## Instructions

1. **Find the auth library.** Look at `package.json` and the code:
   `next-auth` (v4) or `next-auth@5` / `@auth/*` (Auth.js),
   `@supabase/supabase-js` with `signInWithOAuth`, `firebase/auth` with
   `GoogleAuthProvider`, or `@clerk/*`. If there is none, recommend one that
   fits what the app already uses (Supabase Auth if it uses Supabase, Firebase
   Auth if it uses Firebase, Auth.js for a plain Next.js app, Clerk if the user
   wants a hosted login page), and ask before adding it.

2. **Make the list of addresses.** Write a table the user will copy from. Every
   value must match exactly: `http` versus `https`, `www` or not, the port, and
   no trailing slash.

   | Library | Authorized JavaScript origins (in Google) | Authorized redirect URIs (in Google) |
   | --- | --- | --- |
   | Auth.js / NextAuth | `http://localhost:3000`, `https://my-site.com` | `http://localhost:3000/api/auth/callback/google`, `https://my-site.com/api/auth/callback/google` |
   | Supabase Auth | `http://localhost:3000`, `https://my-site.com` | only the **Callback URL** Supabase shows on its Google provider page, `https://<project-ref>.supabase.co/auth/v1/callback` |
   | Firebase Auth | none needed by hand | none by hand: Firebase sets up `https://<project-id>.firebaseapp.com/__/auth/handler`. Instead add the live domain to Firebase's **Authorized domains** list. |
   | Clerk | none needed by hand | development: nothing (Clerk's shared test login). Production: the **Authorized Redirect URI** Clerk shows on its Google connection page. |

   Add `www` and non-`www` both if the site answers on both. Add preview
   addresses only if the user needs login on previews.

3. **Set up the consent screen.** Tell the user what to do in the Google Cloud
   console, in the section for OAuth (now often called **Google Auth Platform**):
   - **Branding:** app name, support email, and, for the live site, the home
     page, privacy policy link and the site's domain under authorized domains.
   - **Audience:** "External" for a public app. Explain the two states:
     **Testing** lets only the test users they list log in; **In production**
     lets anyone with a Google account in. Add their own email as a test user
     for now.
   - **Data access (scopes):** only `openid`, `email` and `profile`. Asking for
     more (Gmail, Drive) needs Google's review, which takes weeks.
   Official guide: <https://support.google.com/cloud/answer/15544987>.
   For Firebase Auth and Clerk development instances, this screen is created
   for them; still check the app name and support email.

4. **Create the OAuth client (skip for Firebase and Clerk development).** In
   the same section, under **Clients**, create a client of type **Web
   application** and paste the origins and redirect URIs from step 2. Google
   then shows a **client ID** and a **client secret**. Official guide:
   <https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred>.
   Tell the user Google shows the secret only at creation on newer projects,
   so they should copy it straight to the next step.

5. **Put the ID and secret in the right place, typed by the user.** Ask before
   creating or editing any `.env` file, and check `.gitignore` covers it first.

   | Library | Where the user puts them |
   | --- | --- |
   | Auth.js v5 | `.env.local`: `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`, and `AUTH_SECRET` (the user can run `npx auth secret` in their own terminal to create it) |
   | NextAuth v4 | `.env.local`: the names the code uses, often `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, plus `NEXTAUTH_SECRET` and `NEXTAUTH_URL` |
   | Supabase Auth | Supabase dashboard, Authentication, Providers, Google: paste the client ID and secret there. Then under URL Configuration set the **Site URL** to the live address and add `http://localhost:3000/**` and `https://my-site.com/**` to the redirect allow list. Nothing secret goes in the app. |
   | Firebase Auth | Firebase console, Authentication, Sign-in method: turn on Google. Then Authentication, Settings, Authorized domains: add the live domain. Nothing secret goes in the app. |
   | Clerk (production) | Clerk dashboard, the Google connection: turn on custom credentials and paste the client ID and secret there. |

   None of these names may have a public prefix ([KEYS.md](../KEYS.md)), except
   that an OAuth client ID alone is safe to be public. Verify with the
   names-only command that the names are present.

6. **Wire the code, with a yes.** Show the planned change first, then make the
   smallest one that fits the library:
   - Auth.js: the Google provider in the `auth` config, the route handler at
     `app/api/auth/[...nextauth]/route.ts` (or `pages/api/auth/[...nextauth].ts`
     for v4), and a sign-in button that calls `signIn("google")`.
     Docs: <https://authjs.dev/getting-started/providers/google>.
   - Supabase: `supabase.auth.signInWithOAuth({ provider: "google", options: {
     redirectTo: ... } })`, with `redirectTo` built from the current site
     address, never a hard-coded `localhost`. Add the callback route the
     Supabase guide shows for server rendering.
     Docs: <https://supabase.com/docs/guides/auth/social-login/auth-google>.
   - Firebase: `signInWithPopup(auth, new GoogleAuthProvider())`. Prefer the
     popup; the redirect flow needs extra steps on sites not hosted on Firebase.
     Docs: <https://firebase.google.com/docs/auth/web/google-signin>.
   - Clerk: its `<SignIn />` component or `SignInButton` already shows Google
     once the connection is on. Docs: <https://clerk.com/docs/authentication/social-connections/google>.
   Keep the client secret in server code only.

7. **Test on the user's computer.** Start the dev server and ask the user to
   log in with Google. A browser tool can open the page, but the Google login
   itself is the user's. Then check the result from the app side where you can:
   for Auth.js, open `/api/auth/session` and confirm it shows a user (report
   the email only if the user is happy for you to); for Supabase or Firebase,
   check the app shows the logged-in state. Have them log out and in again.

8. **Test on the live site.** If the site is online, make sure the variables are
   on the host (hand off to `deploy-frontend-env`, and for Auth.js on hosts
   other than Vercel, `AUTH_TRUST_HOST=true` or `AUTH_URL` may be needed), then
   repeat the login on the live address. Google says changes to a client can
   take a few minutes, sometimes longer, to apply; wait and retry before
   changing more.

9. **Going live for everyone.** While the consent screen is in **Testing**,
   only test users can log in. When the user is ready, explain the change and
   ask; with a yes, they press **Publish app** on the Audience page. With only
   `openid`, `email` and `profile`, Google usually does not need a full review,
   but the console says if branding verification is needed. Read that screen
   back with them.

## Fixing common errors

| What the user sees | Usual cause | Fix |
| --- | --- | --- |
| `Error 400: redirect_uri_mismatch` | The redirect URL the app sent is not in the client's list | Read the `redirect_uri` value in the error details, and add exactly that to the client (step 2) |
| Works locally, fails on the live site | Only `localhost` is in the list, or the host's variables are missing | Add the live addresses; check the names on the host |
| "Access blocked: this app's request is invalid" | Missing or wrong origin, or the client is the wrong type | Use a **Web application** client with the right origins |
| Only some people can log in | The consent screen is still in Testing | Add them as test users, or publish (step 9) |
| Supabase sends users to `localhost` after login on the live site | Site URL or redirect allow list in Supabase | Fix URL Configuration in Supabase |
| Firebase `auth/unauthorized-domain` | The live domain is not in Authorized domains | Add it in Firebase Authentication settings |

## Examples

**User:** "Add Google login to my Next.js app. It's on Vercel at
bakery-tlv.com."

**Agent:** Finds no auth library and suggests Auth.js; gets a yes. Writes the
table: origins `http://localhost:3000` and `https://bakery-tlv.com`, redirect
URIs ending in `/api/auth/callback/google` for both. Walks the user through the
consent screen with `openid`, `email` and `profile`, and the Web application
client. The user types `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET` and `AUTH_SECRET`
into `.env.local`; the agent checks the names. Adds the provider, route and
button after a yes. The user logs in locally, `/api/auth/session` shows a user.
Hands off to `deploy-frontend-env` for the same names on Vercel, then the user
logs in on the live site.

**User:** "ההתחברות עם גוגל עובדת אצלי במחשב אבל באתר אני מקבל redirect_uri_mismatch"

**Agent:** Answers in Hebrew. Asks for the `redirect_uri` shown in the error
details. It is `https://www.my-site.com/api/auth/callback/google`, but the client
only has the address without `www`. Has the user add it, waits a few minutes,
and retests on the live site.

**User:** "Here's my client secret, put it in the env file for me: GOCSPX-..."

**Agent:** Asks the user not to share it in the chat and to create a new secret
for the client, since this one is now in the conversation. Then shows them how
to type the new one into `.env.local` themselves.
