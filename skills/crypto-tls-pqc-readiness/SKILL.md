---
name: crypto-tls-pqc-readiness
description: Inventories where a project depends on quantum-vulnerable public-key cryptography and what would break when hybrid post-quantum key exchange or post-quantum signatures are enabled. Use when planning a post-quantum migration, auditing TLS and library configuration, or assessing long-lived data and device fleets. Read-only. Not for implementing the migration, benchmarking, or handling key material.
license: MIT
compatibility: Requires source code, dependency manifests and lockfiles, and readable deployment or infrastructure configuration. Reading the current standards documents (Instruction 1) needs network access; without it the agent proceeds from the documents it already has and marks every date it could not verify. No credentials or private keys required.
metadata:
  collection: vibe.md
  author: talforsher
  maintainers: talforsher
  categories: Security, Deployment
---

# TLS and post-quantum readiness

## Purpose

Produce a defensible answer to two separate questions:

1. Where does this project's confidentiality depend on key exchange that a future quantum computer could break, and for how long is that data sensitive?
2. Where does its authentication depend on signatures or certificates, which migrate on a different and usually slower schedule?

Confidentiality and authentication are not one migration. Hybrid key exchange needs both ends to support it and mostly depends on library versions. Signatures depend on certificate authorities, pinned trust, firmware and third parties. Treating them as one task produces a plan nobody can execute.

## When to Use

- Plan or review a post-quantum migration, or respond to a policy deadline.
- Check whether enabling hybrid key exchange would break an existing deployment.
- Assess a long-lived fleet, stored data, or a signed-payload contract for transition risk.
- Verify a vendor or internal claim that something "already supports PQC".

Not for implementing the change, tuning performance, generating keys, or testing live endpoints. This skill reads and reports; it does not deploy.

## Prerequisites and permissions

- Repository read access, dependency manifests and lockfiles, and any infrastructure or deployment configuration that is part of the project.
- Permission to read configuration only. Do not read, copy, print or export private keys, keystores, tokens or secret values, even to identify an algorithm. If an algorithm can only be learned from a secret file, record the file path and ask the owner.
- No scanning of live hosts, no external TLS probes, no changes to configuration. If the request implies testing a running service, keep the work static and say what was not observed.

## Instructions

1. **Pin the references.** Name the documents that decide the answer, rather than trusting this skill's dates: NIST IR 8547 for the transition schedule, FIPS 203/204/205 for ML-KEM, ML-DSA and SLH-DSA, and the IETF TLS hybrid key-agreement draft for the group names actually in use. Record the version or draft number of each.
2. **State the dates you actually read, or say you could not.** Because this area changes, report the date each reference was read. If you have no network access, or a document is unreachable, list the documents that need checking and mark their dates unverified; do not state a date you did not read. Anything this skill asserts about timing is what IR 8547 said when this skill was written, to be checked against the current text, never quoted as a deadline on its own.
3. **Inventory by dependency, not by keyword.** Search for TLS configuration, HTTP client construction, reverse proxies, load balancers, database and message-broker connections, mTLS, VPN and SSH, plus application-level crypto: JWT and JWS algorithms, signed payloads, encrypted columns, envelope encryption, and anything a third party verifies. Record file and line for each finding.
4. **Record library and runtime versions from lockfiles.** Note the exact versions of the TLS stack in use (for example OpenSSL, BoringSSL, Go `crypto/tls`, Node, the JVM, Python `ssl` and `cryptography`) and whether that version supports hybrid post-quantum key exchange at all. Do not assume a runtime is current because documentation says so; use the manifest.
5. **Find the configuration that decides negotiation.** Explicit group or curve lists, cipher strings, `minVersion`/`maxVersion` pins, legacy TLS 1.2 paths, and any place an allow-list of algorithms is hardcoded. A library that defaults to a hybrid group still cannot use it where the application pins a group list that excludes it.
6. **Classify each endpoint by what it protects.** For each connection, note the data lifetime and whether confidentiality must outlive the migration window. A session token that expires in an hour and an archive of medical records are different problems. Read [the inventory guide](references/inventory.md) before assigning priority.
7. **Enumerate authentication dependencies separately.** Certificates and their issuing chains, key types and sizes, certificate pinning, code signing, firmware verification, and signed tokens that other systems verify. Note which of these are controlled by the project and which depend on a third party that has its own schedule.
8. **List concrete blockers, with evidence.** Examples worth checking: peers that only speak TLS 1.2; embedded or on-premise clients with no update path; pinned RSA or ECDSA keys; HSMs, appliances or managed services whose support is unknown; signature verification in firmware or in a counterparty's system; handshake size limits in constrained transports or middleboxes. Mark each as confirmed from the project's own files, reported by a document, or unverified.
9. **Test crypto agility in the code, without deploying.** Identify whether the algorithm is a constant in code, a database column value, or a documented policy, and how many places must change to rotate it. Note whether the project can verify both old and new signatures during a transition, and whether a downgrade to a classical group would be detected. The only exception to read-only: if the project already has a test harness, you may propose a local test and add it after the user agrees, limited to test files. Do not invent a runtime test, and do not run anything that reaches a real host.
10. **Report.** Deliver: the pinned references and the date each was read, or that a date could not be verified; an inventory table; the two migration tracks; ordered blockers; what you could not determine and why. Fill [the inventory template](assets/pqc-inventory.md) as the working record so the evidence and the report stay in one place. Separate confirmed facts, documents' claims, and your inference. Never present a readiness score you cannot reproduce from the evidence, and do not describe the project as "PQC-ready" or "compliant" on the strength of a static read.

## Examples

**User:** "Where would post-quantum TLS break our stack?"

**Agent:** Reads the reverse-proxy and client configuration, lockfiles and any pinned group lists. Reports that the server library supports the hybrid group but that the application pins an explicit curve list that excludes it, and that one internal service only allows TLS 1.2. Does not connect to any host.

**User:** "Are we compliant with the new NIST transition timeline?"

**Agent:** Reads the current IR 8547 text and the project's dependency versions, then reports which algorithm uses fall in which category and which the project has not established. Refuses to give a compliance verdict from a static inventory alone.

**User:** "Enable ML-KEM everywhere and show me it works."

**Agent:** Explains the boundary: this skill produces the inventory and the ordered blockers. It does not change configuration or test live endpoints. Offers the concrete list of changes the migration would need and what to verify afterwards.

## Boundaries

- Read-only, with one narrow exception: a local test in test files only, and only after the user agrees. No configuration edits, handshakes against real hosts, or dependency upgrades without a separate request.
- No key material, keystores or secrets in output.
- No vendor marketing as evidence. A support claim is recorded as a claim with its source, not as a confirmed capability.
- No compliance or certification conclusion. See [the reporting rules](references/reporting.md).
