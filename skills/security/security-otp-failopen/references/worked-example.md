# Worked example: one flow, eight cases, one mutation

A password reset by SMS code. The handler issues six digits, stores a hash with a ten-minute expiry and an attempt counter, then sets a reset token on success.

## The contract, written before any test

- Issued to one account and one destination.
- Six digits, generated with a cryptographic random source.
- Stored hashed; the plaintext exists only in the message.
- Ten minutes from issuance; a resend issues a new code and invalidates the previous one.
- Five wrong attempts end the code.
- Single use: success consumes the code and sets one reset token.
- If the SMS adapter errors, the reset must not proceed.

## The cases

| # | Case | Assertion |
| --- | --- | --- |
| 1 | Correct code, correct account | One reset token returned; card state changes once. |
| 2 | Replay of the same code | Second attempt fails; no additional token. |
| 3 | Expired code | Fails; no token. |
| 4 | Another account's valid code | Fails for this account; the other account is untouched. |
| 5 | Login code used at reset | Fails. |
| 6 | Six wrong attempts, then the right one | Code already dead; no token. |
| 7 | Adapter raises, times out, returns `5xx` | Flow ends unauthenticated in every case. |
| 8 | Delivery failed after issuance | Stored code is unusable. |

## Making the tests prove themselves

On a disposable copy, change one line in the verify handler:

```diff
- if not record:
+ if not record or provider_error:
-     return deny()
+     return allow()
```

Case 7 must fail. If it still passes, the assertion is wrong or the fake adapter never reached the error branch. Restore the copy afterwards.

A second mutation removes the `used` flag check. Case 2 must fail.

## Reporting shape

```
flow: password reset by SMS
contract source: docs/reset.md, src/verify.ts
cases: 8 selected, 8 run
result: 6 pass, 1 fail (case 7: timeout path returns 200 and sets a token)
mutation sensitivity: verified (2 mutations, both caught)
not exercised: real carrier behaviour, delivery latency, rate limiting at the edge
```
