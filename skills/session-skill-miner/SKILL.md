---
name: session-skill-miner
description: Looks back over the current conversation at the end of a session and proposes reusable skills from repeated steps, corrections, and conventions the user taught. Use when a session is wrapping up or when the user asks what from this chat could become a skill.
license: MIT
compatibility: Needs access to the conversation. Looks in the project and user skill directories of the agent in use, when they exist.
metadata:
  collection: vibe.md
  author: Yossi4
  categories: Productivity, AI / Agents
  maintainers: Yossi4
  title: Session Skill Miner
---

# Session skill miner

## Purpose

Turn what happened in a session into reusable skills. Work that was explained twice, corrected once, or repeated in several steps is a candidate for a skill, so the next session starts with that knowledge.

## When to Use

- The session is ending ("that's it for today", "wrap up").
- The user asks "should any of this be a skill?" or "what did we learn here?".
- The same procedure came up more than once in the conversation.

Do not use this skill to write a skill from scratch on a topic that never appeared in the chat; write that skill directly. Do not use it on a very short session with nothing repeated; say so instead.

## Prerequisites

- Access to the conversation itself. Nothing else is required.
- Permissions: read-only until the user picks a proposal. The skill lists skill directories and reads the chat, and writes a `SKILL.md` only after the user chooses and has seen the draft. It never deletes or overwrites an existing skill.

## Instructions

1. Reread the whole conversation. Collect candidates from these signals:
   - Steps the user had to repeat or re-explain.
   - Corrections: "no, do it this way", and the rule behind them.
   - Multi-step procedures that worked, especially ones with a required order.
   - Project conventions the user stated (naming, branches, commit formats, review habits).
   - Mistakes that cost time and a check that would have prevented them.
2. Filter hard. Keep a candidate only if it is repeatable (likely to come up again), non-obvious (the agent would not do it right by default), and general enough to describe without this session's one-off details. Drop everything else, including facts that belong in a project note and not in a skill.
3. Check for overlap. List the skills the user already has, in the project and user skill directories of the agent in use. Prefer extending an existing skill over adding a near-duplicate, and say which one.
4. Present at most five proposals, best first. For each: a lowercase hyphenated name, one sentence on what it does and when to use it, the evidence from the chat (what happened that suggests it), and a rough size (small rule, or full procedure). Keep client names, internal paths, and secrets out of the proposals too, since a chat is often copied elsewhere.
5. If nothing passes the filter, say so plainly. An empty list is a valid result; do not invent skills to fill it.
6. Wait for the user to choose. Create no files before they pick.
7. For each chosen proposal, draft the `SKILL.md` and show it before saving. Remove personal details, client names, internal paths, and anything confidential, since skills are often shared.

## Examples

**User:** "We're done for today. Anything worth keeping?"

**Agent:** Finds that the user explained the branch naming and commit message format three times, and that a build step was forgotten twice. Proposes `commit-conventions` (small rule, evidence: stated three times) and `pre-deploy-checklist` (full procedure, evidence: the forgotten step). Notes that a one-off bug fix from the session is not worth a skill, and waits for the user's choice.
