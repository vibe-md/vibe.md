# Inventory guide

## Two tracks

| Track | What moves | Who controls it | Typical sequence |
| --- | --- | --- | --- |
| Key exchange (confidentiality) | Hybrid groups such as X25519MLKEM768 in TLS 1.3 | Library versions on both ends, plus configuration | Upgrade libraries, remove pinning of classical groups, verify both ends, then prefer hybrid |
| Signatures (authentication) | ML-DSA, SLH-DSA, and their use in certificates, code signing and tokens | Certificate authorities, firmware, counterparties, standards bodies | Inventory, pilot in non-public trust paths, dual-verify during transition, retire classical last |

Data that must stay secret longer than the migration window is the reason the first track matters. "Harvest now, decrypt later" means the relevant date is when the ciphertext was captured, not when the migration finishes.

## Where to look

**Transport configuration**
- Reverse proxies, ingress, service meshes, load balancers.
- Client construction in application code: options that set `minVersion`, cipher or group lists, custom verifiers, disabled verification.
- Database, cache, queue and broker connections, including their TLS mode settings.
- mTLS: who verifies whom, and where the trust anchors live.

**Application-level crypto**
- JWT and JWS algorithms, and whether the verifier restricts them.
- Signed webhooks, signed URLs, license files, licence servers.
- Encrypted columns, envelope encryption, key wrapping, backup encryption.
- Password hashing is symmetric and not affected by the quantum transition; note it so it is not mistakenly prioritised.

**Authentication dependencies**
- Certificate key types and sizes, chain length, and any pinning.
- Code signing and update verification, especially in mobile, desktop and firmware.
- Third parties who verify what you sign, or whose signature you verify.

## Prioritisation

Order by two factors, not by enthusiasm:

1. **Exposure**: how long the protected data must remain confidential, and when it was or will be captured.
2. **Feasibility**: how many independent parties must change before a given endpoint can negotiate a hybrid group.

An internal service between two systems you own is usually quick. A consumer device fleet in the field is not. A counterparty that verifies your signatures cannot move until its own software does.

## Blocker catalogue

Record each with file and line, or the document that states it.

- Explicit group or curve allow-list that excludes hybrid groups.
- TLS 1.2 only, on either side.
- Pinned certificates or public keys, by value or by algorithm.
- Handshake size limits, constrained transports, or middleboxes that mishandle larger ClientHello messages.
- Managed services, appliances or HSMs whose PQC support is unknown or unavailable.
- Embedded or on-premise clients with no update path.
- Signature verification performed by third parties or in firmware.
- Custom crypto inside the application, including hand-rolled key agreement or signature checks.
- Hardcoded algorithm strings spread across many files, which is an agility problem rather than a compliance one.

## What "agile" means here

A project is agile when the algorithm can change without changing the callers: one place to select a group or suite, one place to verify a signature format, and tests that cover both the current and the incoming algorithm while both must be accepted.

Note whether a downgrade would be noticed. A client that silently falls back to a classical group is not a hybrid deployment, whatever the configuration claims.
