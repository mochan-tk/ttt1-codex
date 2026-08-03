---
name: context-distillation
description: Distills provenance-linked context into reviewable requirements, decisions, non-goals, and vocabulary with an explicit agreement-merge boundary. Use after collection, before planning from new project knowledge, when sources conflict, or when durable guidance must be tiered without bloating always-on context.
---

# Context Distillation

Turn collected evidence into proposed truth, then let a human agreement merge
decide whether it becomes authoritative.

## Distill one bounded topic

1. Read `docs/context/<topic>/INDEX.md`, every flagged conflict, and only the
   linked source notes needed for the topic. Follow governed links when access
   is available; do not infer missing source content.
2. Extract candidates into the appropriate artifacts:

| Candidate | Durable proposal |
|---|---|
| Verifiable behavior or constraint | `docs/agreements/requirements.md` with a permanent `REQ-###` |
| Architectural or operating choice | One `docs/agreements/adr/ADR-####-<slug>.md` |
| Explicit boundary | `docs/agreements/non-goals.md` |
| Shared project term | `docs/agreements/glossary.md` |

3. Link every candidate to provenance. Reject or return any candidate whose
   source is absent, too broad, or only an unverified AI summary.
4. Present conflicting interpretations and their consequences to the human.
   Do not choose an agreement-level premise on the human's behalf.
5. Make requirements short, declarative, and provable by a command, GitHub
   record, or observable behavior. Never reuse or renumber a requirement ID.

## Assign the context tier

- Put only stable rules needed on most Tasks in root `AGENTS.md`.
- Put path-specific durable rules in the nearest nested `AGENTS.md`.
- Put focused, multi-step procedures in `.agents/skills/`.
- Keep detailed facts and rationale in agreements or referenced context.
- Keep Task-specific facts in the Task Issue, not instruction files.

When an always-on rule is proposed, account for its context budget by removing,
compressing, or demoting stale material. Do not add implementation or measured
setup changes before the agreement is accepted.

## Enforce the agreement PR boundary

1. Open a dedicated agreement PR that lists every proposed `REQ-###`, ADR,
   non-goal, and glossary change with source links.
2. Keep unrelated product or setup work out of that PR. File derived Tasks with
   an origin `#N` for post-merge delivery changes.
3. Treat comments and draft text as negotiation, not authority. Only the human
   agreement merge changes what agents design against.
4. Mark source-note status as `distilled` only when the accepted agreement can
   be traced back to it; preserve the source reference.

If implementation later disproves an agreement, stop that Task, file a derived
agreement Issue, merge the corrected agreement first, and then add a revised
plan comment to the blocked Task.
