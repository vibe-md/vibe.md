---
name: safe-migrations
description: Plans and reviews database schema changes so they are reversible, verified, and never silently destructive. Use when the user asks to add, change, or remove tables or columns, when a migration fails partway, or before running pending migrations in a production or shared environment.
license: MIT
metadata:
  collection: vibe.md
  author: talforsher
---

# Safe migrations

## Purpose

Turn "change the schema" requests into reviewed, reversible migrations: classified risk, one logical change per file, verification queries, and a rollback plan before anything runs.

## When to Use

- Adding, renaming, retyping, or removing tables or columns.
- Backfills or data transformations.
- A migration failed partway and the database is in a mixed state.
- Running pending migrations against a shared, staging, or production database.

Do not use this skill to design the schema itself; use it to make the change safe.

## Prerequisites

- A project with a migration system (Knex, Prisma, Django, Rails, Alembic, Flyway, or plain SQL migration files) or direct SQL access.
- Ask which system the project uses if it is not obvious; nothing here is framework-specific.

## Instructions

1. Inventory before proposing. Read the current state: which migrations exist, which are applied, the target table's columns, types, constraints, indexes, and an approximate row count for large tables.
2. Classify the change and say the class out loud:
   - Additive: new nullable column, new table, new index added concurrently where supported. Low risk.
   - Transform: type changes, backfills, adding NOT NULL to an existing column. Needs a staged plan: add, backfill in batches, then constrain.
   - Destructive: dropping tables or columns, truncation, deletions. Requires explicit user approval, a backup, and a stated rollback plan every single time. Never bundle a destructive step silently into a bigger migration.
3. Make migrations re-runnable. Keep one logical change per migration file with a clear name. Write the forward SQL and its rollback (down migration or equivalent). Prefer transactional migrations where the engine supports them, and say when it does not.
4. Review before running. Show the user the exact SQL that will run, the risk class, what happens if it fails partway, and the rollback plan. Wait for approval on transform and destructive changes.
5. Verify after applying in the development environment: the schema matches the intent, row counts are sane after any backfill, and sample rows plus the application still work. Attach one verification query per change.
6. Handle failed migrations deliberately. Identify which statements actually applied, restore the database to a consistent state explicitly, then retry. Never run a partially applied migration again blind.
7. Follow production rules. Never touch production without explicit approval. Apply in the same order validated in development, take a backup or point-in-time snapshot before transform or destructive changes, and schedule index or constraint work on large tables for a low-traffic window. Show the SQL the framework will run instead of trusting a framework summary.
8. Report. Applied changes with their verification results, rollback steps, and what remains: staging, production, and post-deploy checks.

## Examples

**User:** "Add a status field to orders and backfill it to 'pending'."

**Agent:** Inspects the orders table, then proposes: migration 1 adds a nullable column with a default; a batched backfill; migration 2 adds NOT NULL once counts match. Applies it in development, verifies with row counts, and presents the rollback plan before staging.

**User:** "Just run the pending migrations, production needs them now."

**Agent:** Lists what is pending, classifies each change, holds destructive steps for explicit approval, snapshots the database for transform or destructive items, applies the rest in order, and verifies.
