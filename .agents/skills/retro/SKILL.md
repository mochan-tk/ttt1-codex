---
name: retro
description: Turns repeated project or agent-system friction into the smallest traceable improvement to guidance, skills, templates, tests, or gates while controlling always-on context and upstream flow. Use on a first occurrence that needs a retro candidate, a second occurrence of the same class that warrants promotion, or an applicable PR that must record one upstream result.
---

# Retro

Treat the first occurrence as information and the second occurrence of the same
class as a system-change trigger. Keep both occurrences in GitHub, not session
memory.

## Record the first occurrence

1. Search before filing:

```bash
gh issue list --state open --label "retro:candidate" --search "<failure class>"
```

2. If absent, file `retro-candidate: <friction>` with the occurrence link, root
   cause signature, affected asset, and origin `#N`; add `retro:candidate`.
3. If present, add one occurrence comment with the new evidence link. Do not
   promote unrelated symptoms merely because their titles look similar.

Keep issue-body edit-diff automation as the seeded candidate until a second
occurrence justifies it.

## Promote on the second occurrence

At two durable occurrences of the same class:

1. Gather both links and reproduce or inspect the common root-cause signature.
2. Choose the most deterministic asset that could prevent recurrence:

| Cause | Preferred asset |
|---|---|
| Wrong or missing project truth | Dedicated agreement Issue and agreement PR |
| Always-needed durable rule | Root or nested `AGENTS.md` |
| Repeated multi-step procedure | `.agents/skills/` |
| Brief permits the mistake | Task or Epic template |
| A machine can detect it | Test, lint rule, workflow, or required gate |

3. Write the smallest preventive diff. Prefer a gate over advice when both can
   express the same rule.
4. Open one `retro: <prevention>` PR, link the candidate and occurrences, and
   append one row to `docs/agreements/retro-log.md`.
5. Let human review decide the system change. Close the candidate only after the
   retro PR merges.

## Control the always-on budget

Inspect the always-on context budget during every promotion. When adding to an
`AGENTS.md`, remove, compress, or demote stale guidance in the same PR. Keep
Task facts and long procedures out of always-on files. A one-off scar-tissue
rule is not a budget exception.

## Record one upstream result

Ask once on every applicable project PR whether the learning is generic to the
template. Record exactly one result:

```text
upstream: proposed <url>
upstream: not-applicable — <reason>
```

Land the project-local fix first. Preserve project truth when preparing an
upstream PR, link the originating Issue, and leave acceptance to the template
owner. Do not push template changes downstream or overwrite instance-specific
agreements.
