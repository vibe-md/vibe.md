# Reporting rules

## Separate the three kinds of statement

Use distinct labels in the report:

- **Confirmed**: read directly from the project's own files, with path and line, or reproduced from a lockfile version.
- **Claimed**: stated by a vendor, a document or a colleague, with the source named. Not verified here.
- **Inferred**: your reasoning from what you read. Say what would confirm it.

## Do not produce a verdict you cannot defend

Avoid "PQC-ready", "compliant", "migration complete", and numeric readiness scores that are not derived from a stated rubric the reader can recompute. A static read cannot establish what a running deployment negotiates.

If a rubric is wanted, publish the rubric next to the score and mark every input as confirmed, claimed or inferred. A score built mostly from claims is a summary of the claims.

## Never include

- Private keys, keystores, JKS/PKCS#12 contents, tokens, or passphrases.
- Full certificate dumps where the fingerprint and subject suffice.
- Customer identifiers, internal hostnames if the report leaves the team, or anything copied from a secret store.

## Useful closing sections

- **Not determined**: the specific questions a human must answer, each phrased so it can be answered yes or no.
- **What would change the priority**: the evidence that would move an item up or down.
- **Sequence**: what can start today without external dependencies, and what is blocked on a third party.
