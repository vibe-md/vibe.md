# Verification code failure modes

Use this as a menu, not a checklist. Test the cases the product's own contract states. When the contract is silent on an important case, report it as undecided instead of inventing a rule.

## Lifecycle

| Case | What to observe |
| --- | --- |
| Replay | A code accepted once must fail the second time, through the same endpoint. |
| Concurrency | Two verifications of the same code in parallel: at most one succeeds, and the protected action happens once. |
| Expiry | A code older than its stated time to live fails. Check the boundary on the server, not in the client. |
| Expiry measured from issuance | Resending must not silently extend the life of an old code unless the product says so. |
| Superseded codes | When a new code is issued, decide and verify whether older codes die. |
| Post-success invalidation | After a successful verification, other outstanding codes for that account are invalidated, or the contract explains why not. |
| Cancellation paths | Abandoning the flow, logging out, or changing the destination mid-flow must not leave a usable code. |

## Binding

| Case | What to observe |
| --- | --- |
| Account binding | A code issued to one account cannot complete the flow for another. |
| Purpose binding | A login code cannot reset a password, and a password-reset code cannot confirm a phone change or authorize a payment. |
| Session binding | A code issued in one browser or session cannot be redeemed in an unrelated one, where the product states that binding. |
| Destination binding | A code sent to an old address cannot be redeemed after the destination changes. |
| User-supplied identity | An account identifier supplied by the request is input, not authenticated identity. It must not decide which account the code is checked against. |

## Guessing, cost and disclosure

| Case | What to observe |
| --- | --- |
| Attempt limit | The documented number of wrong attempts ends the code, not just the request. |
| Account limit | Attempts across several codes for the same account are limited, so reissuing does not reset the budget. |
| Issuance limit | One account or one address cannot trigger unlimited messages. This is a fraud and cost control as much as a security one. |
| Response difference | Wrong code and expired code should not reveal which condition applied if the product treats that as sensitive. |
| Timing | Verification should not take noticeably longer for a valid account than an unknown one, where account enumeration matters. |
| Log leakage | Codes, provider tokens and full destination addresses do not appear in application logs, fixtures or error responses. |

## Provider and transport

| Case | What to observe |
| --- | --- |
| Error response | The adapter returning an error must not authorize the action. |
| Timeout | A hung request must end in a defined state, not an open one. Check what happens when the request never returns inside the handler's budget. |
| Malformed answer | An empty or unexpected response body is not a success signal. |
| Provider outage at issuance | If delivery failed, the stored code should be unusable or invalidated, so nobody can guess a code the user never saw. |
| Retry and duplicates | Retrying a send must not create several simultaneously valid codes with unrelated values. |
| Number or address possession | A delivered code proves control of the destination at that moment. If the destination is a phone number, control can move; whether the product adds a number-verification or recent-SIM-change check is part of its contract, and this skill tests how the application treats each answer, including unavailable. |

## What not to do

- Do not brute force, enumerate real accounts, or send messages to real destinations.
- Do not use a captured production code, cookie or token.
- Do not weaken a failing case to match the current implementation; report the gap instead.
