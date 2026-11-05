---
name: google-gemini
description: Adds Google's Gemini AI to a website or app with the key kept on the server. Gets a Gemini API key from Google AI Studio typed into .env by the user, restricts it to the Gemini API, adds a server route that the browser calls (never Google directly), and puts limits in place so a busy or abused feature cannot run up a bill, such as login or a per-visitor rate limit, a daily cap, input length and output token limits, and a budget alert. Reads the current models, prices, free-tier terms and rate limits live. Ends with one real request through the server. Use when the user says "add Gemini to my app", "add an AI chatbot with Google Gemini", "use the Gemini API", "where do I put my Gemini key?", "my Gemini key is in the frontend", "תוסיף את Gemini לאפליקציה", or "תחבר את האתר ל-AI של גוגל". Not for reviewing prompts or comparing models (use llm-prompt-review, llm-eval-builder, llm-model-migration-check), not for a security review of AI code (use security-agent-guard), and not for other AI providers.
license: MIT
compatibility: Needs read and write access to the project, an app with server code (API routes, server actions or functions), network access for the live docs, and a Google account. The user creates the key in Google AI Studio and types it into .env. Paid use needs billing on the linked Google Cloud project, with a budget alert first.
metadata:
  collection: vibe.md
  group: google
  author: NirGeron98
---

# Google: Gemini in your app, key on the server

Read [the shared google contract](../GOOGLE.md) and [the keys guide](../KEYS.md)
first, and follow them.

## Purpose

A Gemini key lets anyone who has it send requests that the key's owner pays
for. If it is in the browser code, anyone who opens the site can copy it. This
skill keeps the key on the server, puts the AI behind the app's own route, and
adds limits so one user, a bot, or a bug cannot run up a bill.

## When to Use

- The user wants an AI feature powered by Gemini: a chatbot, a summary, a
  writing helper, image description.
- The Gemini key is in browser code or a public variable.
- The user asks what Gemini will cost or how to limit it.
- Examples: "Add Gemini to my app", "Make a chatbot with Google Gemini",
  "Where do I put my Gemini key?", "My Gemini key is in the frontend",
  "תוסיף את Gemini לאפליקציה", "תחבר את האתר ל-AI של גוגל".

Do not use this skill:

- to improve prompts, build tests for the AI's answers, or switch models. Use
  `llm-prompt-review`, `llm-eval-builder` or `llm-model-migration-check`.
- for a security review of the AI feature (prompt injection, tool use). Use
  `security-agent-guard` after building it.
- for a static site with no server code. Suggest adding a serverless function
  first.
- for Vertex AI on Google Cloud. Mention it exists for businesses already on
  Google Cloud, and that this skill covers the Gemini API from AI Studio.

## Prerequisites

- A Google account. Google AI Studio creates or links a Google Cloud project
  for the key.
- For the paid tier: billing on that project and a budget alert
  (`google-setup`).
- Server code in the app.

## Instructions

1. **Read the current facts live.** Before choosing anything, open and tell the
   user what you read, with addresses and the date:
   - Models: <https://ai.google.dev/gemini-api/docs/models>. Pick a current
     model for the job; do not pick one from memory.
   - Prices: <https://ai.google.dev/gemini-api/docs/pricing>.
   - Rate limits: <https://ai.google.dev/gemini-api/docs/rate-limits>.
   - Terms: <https://ai.google.dev/gemini-api/terms>. Point out what they say
     about how data sent on the free tier may be used, so the user can decide
     whether the free tier fits (for example, not for customers' private data).

2. **Fix a leaked key first.** If a Gemini key is in browser code, a public
   variable (`NEXT_PUBLIC_`, `VITE_` and so on), or Git history, stop and say
   so, masked. It must be replaced, not just moved ([KEYS.md](../KEYS.md), "If
   a key leaked"). Continue with a new key.

3. **Get the key, typed by the user.** The user creates a key at
   <https://aistudio.google.com/apikey> in the right project, and types it into
   `.env.local` as `GEMINI_API_KEY` (no public prefix). Check `.gitignore` first
   and the name after. Never ask for the key in the chat.

4. **Restrict the key.** In the linked Google Cloud project's Credentials page,
   the key should have an **API restriction** to the Gemini API (listed as
   "Generative Language API"). A server on Vercel or Netlify has no fixed
   address, so the key usually has no application restriction: keeping it
   secret, the API restriction and the limits below are what protect it.
   Verify as in [KEYS.md](../KEYS.md).

5. **Budget and paid tier, only with a yes.** If the user wants the paid tier,
   check a budget alert exists first (`google-setup`), then the user turns on
   billing for the project in AI Studio or the console. Explain again: the
   budget emails, it does not stop spending.

6. **Add the server route, with a yes.** Show the plan, then:
   - Install the official SDK (`@google/genai` for JavaScript, `google-genai`
     for Python). Docs: <https://ai.google.dev/gemini-api/docs/quickstart>.
   - Create the client in **server code only** (a route handler, server action
     or function), reading `GEMINI_API_KEY`. Keep the model name in one setting
     such as `GEMINI_MODEL`, so it can change without touching code.
   - The browser sends only the user's text to this route. The route builds the
     request; the browser never chooses the model, the system instructions or
     the limits.
   - Stream the answer back if the feature is a chat, still through the route.

7. **Add the limits, with a yes.** Ask the user for the numbers; suggest small
   ones to start:
   - **Who may use it:** require login if the app has it; otherwise a per-visitor
     rate limit (for example 10 requests per minute per IP), with a store that
     works on their host (the host's KV, Upstash, or the database they already
     use; in-memory only for local testing).
   - **A daily cap** per user and for the whole app, after which the route
     answers "Try again tomorrow".
   - **Input size:** reject messages over a length (for example 2,000
     characters), and keep only the last few chat turns.
   - **Output size:** set `maxOutputTokens` in the request config.
   - **Timeout** on the request, and a friendly error.
   - Optionally lower the API's requests-per-day quota in the console, as a hard
     stop ([GOOGLE.md](../GOOGLE.md), section 2).

8. **Handle the AI's input and output safely.** Treat what users type as data:
   keep the system instructions in the server code, not mixed into user text.
   Show the answer as text, not as raw HTML. If the feature can do things (call
   tools, read files, send email), stop and suggest `security-agent-guard`
   before it goes live. Do not log full conversations with personal data; log
   counts and errors.

9. **Test.** Run the dev server and send one short request through the app's own
   page or route. Check the reply arrives, the browser's network list shows the
   call going to the app's route and **not** to
   `generativelanguage.googleapis.com`, and the built browser files contain no
   `AIza` key (`google-keys-check` step 4). Try one over-long message and one
   burst over the rate limit, and confirm both are refused.

10. **Live site.** Hand off to `deploy-frontend-env` for `GEMINI_API_KEY` (as a
    secret) and the rate-limit store's settings on the host, deploy, and repeat
    one test on the live site.

11. **Report.** Where the key lives, the model and why, the limits in plain
    words ("each visitor can send 10 messages a minute and 50 a day"), the
    budget, and what was tested. Suggest `llm-eval-builder` for testing answer
    quality, and `security-agent-guard` for a security pass.

## Examples

**User:** "Add a Gemini chatbot to my Next.js site."

**Agent:** Reads the models, pricing, rate limits and terms pages, and reports
them with the date. Explains the free tier's data terms; the user chooses the
paid tier, so the agent confirms a budget alert of 20 exists first. The user
creates the key, types `GEMINI_API_KEY` into `.env.local`, and restricts it to
the Generative Language API. With a yes, the agent adds `@google/genai`, a route
handler with login required, 10 requests a minute and 50 a day per user, a
2,000-character input cap and `maxOutputTokens`, and a streaming chat box.
Tests one message and one over-long one, and checks the network list shows only
the app's own route.

**User:** "המפתח של Gemini נמצא אצלי ב-VITE_GEMINI_API_KEY, זה בסדר?"

**Agent:** Answers in Hebrew. Explains that every `VITE_` value is sent to all
visitors, so the key is public. Asks the user to replace it in AI Studio and
delete the old one once the new one works, and moves the call to a serverless
function with limits, after a yes.

**User:** "Which Gemini model is the cheapest?"

**Agent:** Opens the current pricing page and answers from it, with the address
and date, instead of from memory.
