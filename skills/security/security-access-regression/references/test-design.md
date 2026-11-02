# Permission test design

## Choose the real boundary

Use the project's in-process HTTP client when authentication middleware lives at the request layer. A service-level test alone does not cover middleware. If direct database access or storage policies are part of the product, test them only through the existing isolated harness and report when that boundary was not exercised.

Never mock the policy decision itself. Fake email, billing, storage and queue adapters so denied operations cannot escape the fixture environment.

## Denial has several legitimate shapes

- An item route can return 403 or conceal existence with 404, according to policy.
- A list can return 200 with only permitted rows. Check that the allowed row is present as well as the forbidden row being absent.
- A shared object can expose public fields while redacting private ones. Assert field presence and absence separately.
- A file response can be a redirect or signed URL. A denial must not mint a usable URL or deliver private bytes. Report if the isolated storage adapter cannot establish this.
- A queued operation needs both enqueue-time and worker-time checks if identity or permission can change between them. Only test that path when it belongs to the selected boundary.

## Select cases, do not multiply blindly

Use known synthetic IDs in the route, query, body or batch input actually accepted by the operation. A client-supplied owner or tenant is input, not authenticated identity. For a batch, state whether the product rejects the whole request or filters each item; test its documented behavior and inspect side effects.

For writes, snapshot the targeted fixture before and after. Also inspect the relevant fake sink if the code can send messages, create files or enqueue work. A 403 with a changed row is a failed test.

Add role-revocation cases only when the boundary uses cached permissions or a deferred job. Do not invent an administrator who can do everything. Two owners in different tenants do not prove isolation between two owners in the same tenant.

## Failure sensitivity

A controlled mutation is a temporary alteration to an isolated source copy, not a production exploit. Remove exactly the check the regression is meant to guard. If the forbidden test still passes, improve the fixture or assertion before treating the test as useful.

Record both directions: allowed operation succeeds; forbidden operation fails. A handler that denies every request must fail the allowed-control test. Remove the temporary copy when finished. If the project cannot support this safely, mark sensitivity unverified.
