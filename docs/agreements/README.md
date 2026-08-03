# Reviewed Truth

`docs/agreements/` is the authoritative, human-reviewed project memory for
Phase 2. A document becomes an agreement only when its pull request is merged.

| Artifact | Purpose |
|---|---|
| `requirements.md` | Permanent, verifiable `REQ-###` statements |
| `non-goals.md` | Explicit boundaries that prevent scope drift |
| `glossary.md` | Fixed vocabulary shared by humans and Codex |
| `adr/ADR-####-<slug>.md` | One durable architectural or operating decision |
| `retro-log.md` | Append-only operating ledger for repeated friction and the system changes that remove it |

Task Issues cite requirements and decisions by ID. Their executable acceptance
criteria trace back to these agreements. A retro-log row is durable evidence,
not an agreement by itself; it changes authority only through a resulting REQ
or ADR agreement merge.

## Change control

If implementation work reveals that an agreement is wrong:

1. Do not repair the agreement as a side effect of the implementation branch.
2. File a derived Issue that cites the discovery source as `#N`.
3. Change the agreement in a dedicated pull request.
4. Merge that agreement first, then replan the blocked implementation Task.

This separation preserves the tracking graph and makes the agreement merge a
real human decision.

## Source priority for this template

When sources conflict, use this order:

1. Explicit owner decisions that have landed through an agreement pull request.
2. [`requirements.md`](requirements.md) and accepted ADRs here.
3. The 2026-08-02 handoff deltas D1-D10 and approved source ADR-0006.
4. The pinned ADLC chapter manuscript.
5. Earlier source ADRs and the `tt1` scaffold where they are not superseded.

Current GitHub and Codex product behavior must still be verified against
official documentation and, where practical, measured in the target account.
An owner comment or session instruction is input to the next agreement PR; it
does not silently override merged truth.
