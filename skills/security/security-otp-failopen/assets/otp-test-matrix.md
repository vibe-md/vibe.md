# Verification code test matrix

Fill this in for one flow before writing code.

```
flow:
contract source:                 # file, doc, or product owner statement
issued by:
verified by:
protected action:

code: length        value space        generator
storage: hashed / plaintext / external
time to live:                       measured from:
single use: yes / no / unclear
max attempts per code:              per account:
resend behaviour:                   invalidates previous: yes / no / unclear
attempts extension:                 does a failure extend the window:
delivery adapter:                   fake used in tests:
offline behaviour:                  documented: yes / no

# Selected cases
[ ] replay
[ ] concurrent redemption
[ ] expiry boundary
[ ] resend supersession
[ ] account binding
[ ] purpose binding
[ ] session binding
[ ] attempt limit per code
[ ] attempt limit per account
[ ] issuance limit
[ ] provider error
[ ] provider timeout
[ ] malformed provider answer
[ ] delivery failure invalidates code
[ ] log leakage

# Mutation check
defect introduced:                  test that failed:

# Not exercised
```
