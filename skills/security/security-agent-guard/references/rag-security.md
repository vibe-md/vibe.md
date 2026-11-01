# Retrieval (RAG) security

Load this file when the code retrieves documents, records, or embeddings and places them in a model's input. This is often called retrieval-augmented generation (RAG).

## The risk

A retrieval system searches a store of content and adds the best matches to the prompt. Two things go wrong:

- **Cross-user leakage:** the store holds content from many users or organizations, and the search does not limit results to what the current user may see. The model then quotes another user's data.
- **Poisoned content:** someone who can add content to the store can plant instructions that the model later reads as part of the prompt (see `prompt-injection.md`).

## What to trace

1. **Ingestion.** Find where content is added to the store: who can add it, and whether owner, tenant, or permission information is saved with each item.
2. **Query.** Find the search call. Note whether it receives a filter for the current user, tenant, or permission, and where that value comes from.
3. **Separation.** Check whether the application instead uses a separate store, index, collection, or namespace per tenant, and how it picks one.
4. **Use.** Follow retrieved content into the prompt and note whether the response can reach another person.

## When it is a finding

Report a finding when the code shows:

- the application serves more than one user or organization, and
- content from different users or organizations is in the same store, and
- the search runs with no filter or separation based on the current user's identity.

Also report when the filter value comes from the request body, the prompt, or the model instead of the server-side session. A user could change it.

Mark it **confirmed** when ingestion and query are both visible. Mark it **suspected** when the filter could be applied in a layer you could not read, such as a database policy or a managed service setting, and say what to check.

## When it is not a finding

- The application has a single user, or the store holds only content every user may see.
- Each tenant has its own store or namespace, chosen from the server-side session.
- The search applies a filter built from the authenticated user on the server.
- Access is enforced by the store itself, for example row-level security, and the code uses the user's credentials.

## Severity

| Severity | When |
| --- | --- |
| High | One user can retrieve another user's or organization's private content through normal use. |
| Medium | Leakage needs an unusual query or is limited to less sensitive content, or the filter value can be changed by the user. |
| Low | Retrieved content is shared by design, but ingestion lets any user add content that others will read, with no review. |

## Fixes to recommend

1. **Save ownership at ingestion:** store owner, tenant, and access fields with every item.
2. **Filter at query time** using the identity from the server-side session, never from the request or the model.
3. **Separate tenants** with a store, index, or namespace per tenant when the data is sensitive.
4. **Check again after retrieval** if access rules are complex, and drop items the user may not see.
5. **Treat retrieved text as untrusted** and keep tools away from calls that read it, as described in `prompt-injection.md`.

## Example finding

> **Where:** `rag/ingest.js:18` (ingestion), `rag/search.js:9` (query)
> **What:** Cross-user leakage. Uploaded documents from all customers go into one collection without an owner field, and `search(question)` queries the whole collection.
> **Why it matters:** A customer asking "show me the latest invoice" can receive another customer's invoice in the answer.
> **Severity:** High. Private data of other customers is reachable through normal use.
> **Certainty:** Confirmed. Both ingestion and query are in the reviewed files.
> **Fix:** Store `tenant_id` with every chunk at ingestion, and pass a filter on `tenant_id` from the signed-in session to every search.
