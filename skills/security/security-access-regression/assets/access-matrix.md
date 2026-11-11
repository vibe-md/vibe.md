# Access contract

Fill this in before writing tests. This is a template, not a default product policy.

- Boundary: `<handler or service entry point, with source reference>`
- Policy evidence: `<product rule or approved policy test>`
- Isolation evidence: `<test database, storage, queue and external-service substitutes>`
- Fixtures: Alice and Bob, distinct sessions and synthetic resource markers.
- Missing decisions: `<explicitly undecided, not silently assumed>`

| Actor | Resource | Operation | Expected result | Assertion |
| --- | --- | --- | --- | --- |
| Owner Alice | Alice's fixture | Read item | Allowed fields | Alice marker present |
| Owner Alice | Both fixtures | List | Only permitted records | Alice present, Bob absent |
| Alice | Bob's fixture | Read item | Contract-specific denial | No Bob fields, bytes or usable access URL |
| Alice | Bob's fixture | Update | Contract-specific denial | Bob unchanged; no fake side effect |
| Anonymous | Private fixture | Read | Contract-specific denial | No private content |
| Scoped admin, if one exists | Outside admin scope | Named operation | Actual policy | Check permitted and forbidden controls |

Do not copy the rows blindly. Some products intentionally share records across owners; some administrators are tenant-scoped. Use the application's intended rules. Add a same-tenant non-owner when that distinction matters. Treat untested export, file, and background paths as coverage gaps rather than expanding one test into an entire audit.
