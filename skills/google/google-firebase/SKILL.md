---
name: google-firebase
description: Adds Firebase to a web app safely, covering Firestore (the database), Cloud Storage (file uploads) and Firebase Hosting. Writes security rules that start closed and give each user only their own data (never allow-all or a "test mode" that expires), tests them on the Firebase emulator before anything goes live, restricts the web API key, and deploys rules or the site only with the user's yes. Explains which parts need the pay-as-you-go plan, from the live pricing page. Use when the user says "add Firebase", "set up Firestore", "my Firestore rules are in test mode", "Firebase says my database is insecure", "upload images to Firebase Storage", "deploy to Firebase Hosting", "תחבר את האפליקציה ל-Firebase", or "תכתוב לי חוקי אבטחה ל-Firestore". Not for Google login with Firebase Auth (use google-sign-in), not for hosting on Vercel, Netlify, Cloudflare Pages or GitHub Pages (use deploy-frontend-*), and not for Supabase.
license: MIT
compatibility: Needs read and write access to the project, Node.js, and network access. Uses the Firebase CLI (firebase-tools) through npx; the user logs in to it themselves. The emulator needs Java installed. A Firebase project, and for Storage the pay-as-you-go (Blaze) plan, which the user turns on only after a budget alert.
metadata:
  collection: vibe.md
  group: google
  author: NirGeron98
---

# Google: Firebase with safe rules

Read [the shared google contract](../GOOGLE.md) and [the keys guide](../KEYS.md)
first, and follow them.

## Purpose

In a Firebase web app, the browser talks to the database directly. The web
config in the code (including its `apiKey`) is public by design, so the
**security rules** are the only thing that decides who can read or change
data. Rules that allow everything, or the "test mode" that allows everything
until a date, are how Firebase data leaks. This skill sets up Firestore,
Storage and Hosting with rules that start closed, proves them on the emulator,
and only then puts them live.

## When to Use

- The user wants a database, file uploads or hosting with Firebase.
- Firebase warned that the rules are insecure or test mode is ending.
- The app has `allow read, write: if true;` or a `request.time <` rule.
- Examples: "Add Firebase to my React app", "Set up Firestore", "My Firestore
  rules are in test mode", "Let users upload a profile photo", "Deploy to Firebase
  Hosting", "תחבר את האפליקציה ל-Firebase", "תכתוב לי חוקי אבטחה ל-Firestore".

Do not use this skill:

- for "Log in with Google". Use `google-sign-in` (it covers Firebase Auth).
  Rules here assume users log in somehow.
- to host on Vercel, Netlify, Cloudflare Pages or GitHub Pages. Use
  `deploy-frontend-choose` and `deploy-frontend-launch`.
- for Supabase or another database.

## Prerequisites

- A Firebase project (create it in the Firebase console, or add Firebase to the
  Google Cloud project from `google-setup`).
- Node.js. The emulator also needs Java; check with `java -version`.
- For Cloud Storage: Firebase now asks for the pay-as-you-go **Blaze** plan for
  new Storage buckets. Read <https://firebase.google.com/pricing> live and
  confirm. Blaze needs billing, so set a budget alert first (`google-setup`).

## Instructions

1. **Find what is there.** Look for `firebase.json`, `.firebaserc`,
   `firestore.rules`, `storage.rules`, the `firebase` package and the web config
   (`initializeApp({...})`). Read any existing rules and flag at once:
   `if true`, `allow read, write;` with no condition, or `request.time <`
   (test mode). Ask what data the app stores and who should see it, in plain
   words: "Should a user see only their own notes, or everyone's?"

2. **Explain the plan and the cost.** Firestore and Hosting work on the no-cost
   Spark plan within its limits; Storage for a new bucket needs Blaze. Read the
   pricing page live and tell the user what it says and the date. Ask before any
   plan change; the user makes it in the console after a budget alert exists.

3. **Set up the CLI, with a yes.** Add `firebase-tools` as a dev dependency
   (`npm install --save-dev firebase-tools`), so it runs with `npx firebase`.
   The user runs `npx firebase login` in their own terminal; it opens a browser.
   Then, with a yes, `npx firebase init` for only the parts needed (Firestore,
   Storage, Hosting, Emulators). Explain each question as it comes. If the
   console asks for a Firestore location, explain that it cannot be changed
   later, and pick one near the users.

4. **Put the web config in environment variables.** The config is not secret,
   but keeping it in `.env` with the framework's public prefix
   (`NEXT_PUBLIC_FIREBASE_API_KEY`, `VITE_FIREBASE_PROJECT_ID` and so on) makes
   it easy to point local work at the emulator. Ask before editing the code.

5. **Restrict the web API key.** On the Credentials page of the same Google Cloud
   project, the key Firebase made ("Browser key (auto created by Firebase)")
   should be restricted to the user's websites (live domain, the
   `<project-id>.web.app` and `<project-id>.firebaseapp.com` addresses if
   Hosting is used, and `localhost`), and to the APIs Firebase uses. Follow
   Firebase's own list, since some Firebase features need their API on the key:
   <https://firebase.google.com/docs/projects/api-keys>. Verify as in
   [KEYS.md](../KEYS.md).

6. **Write rules that start closed.** Start from "deny everything", then open
   only what each kind of data needs. A common pattern for per-user data:

   ```text
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /users/{userId}/{document=**} {
         allow read, write: if request.auth != null && request.auth.uid == userId;
       }
     }
   }
   ```

   For public-read data (such as published posts), allow `read` to everyone and
   `write` only to the owner or an admin field. Check field values on writes
   where it matters (`request.resource.data`). For Storage, match a path with
   the user ID, and limit size and type on upload, for example
   `request.resource.size < 5 * 1024 * 1024` and
   `request.resource.contentType.matches('image/.*')`. Docs:
   <https://firebase.google.com/docs/rules/basics>. Never write `if true` for
   writes, and never use a date-based rule.

7. **Test on the emulator before anything is live.**
   - Start it: `npx firebase emulators:start` (the user can watch the emulator
     page at the address it prints).
   - Point the app at it in development with `connectFirestoreEmulator`,
     `connectStorageEmulator` and `connectAuthEmulator`, only when running
     locally.
   - Add rules tests with `@firebase/rules-unit-testing`: one test that the
     owner can read and write, one that another user **cannot**, and one that a
     logged-out visitor **cannot**. Run them with the emulator, for example
     `npx firebase emulators:exec "npm test"`.
     Docs: <https://firebase.google.com/docs/rules/unit-tests>.
   Do not go on until the "cannot" tests pass.

8. **Deploy the rules, with a yes.** Explain that this changes the live
   database's rules at once. With a yes:
   `npx firebase deploy --only firestore:rules` (and `storage` if used). Then
   check the rules shown in the console match the file.

9. **Hosting, only if they want Firebase Hosting, with a yes.** Build the site,
   check `firebase.json` points `public` at the build folder (`dist`, `out`,
   `build`), and offer a preview first:
   `npx firebase hosting:channel:deploy preview` gives a temporary address.
   After the user checks it, and with a separate yes, deploy live with
   `npx firebase deploy --only hosting`. Open the live address and its main
   pages before saying it is done. Custom domains are added in the Firebase
   console; DNS changes follow `deploy-frontend-domain`'s rules.

10. **Report.** What is set up, the rules in plain words ("each user can read and
    change only their own notes"), which tests passed, what is live, and what
    still needs doing.

## Examples

**User:** "Firebase emailed me that my Firestore rules are insecure."

**Agent:** Reads `firestore.rules` and finds a test-mode rule that allows
everything until a date. Explains that anyone with the project ID can read and
change all data now. Asks what the app stores; it is per-user to-do lists.
Writes owner-only rules, adds three emulator tests, runs them (the "other user"
and "logged out" tests are denied), then with a yes deploys only the rules, and
checks the console.

**User:** "תוסיף אפשרות להעלות תמונת פרופיל ל-Firebase Storage"

**Agent:** Answers in Hebrew. Reads the pricing page and explains Storage needs
the Blaze plan for new buckets; checks there is a budget alert and asks before
the user upgrades. Writes Storage rules allowing each user to write only
`users/<their id>/avatar`, images under 5 MB, tests on the emulator, then
deploys the rules after a yes.

**User:** "Just set the rules to allow everything for now so it works."

**Agent:** Explains that would let anyone read and delete all the data, and
offers the smallest safe rule that lets the feature work for logged-in users.
