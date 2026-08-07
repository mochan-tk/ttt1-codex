---
name: context-collection
description: Collects the minimum project context needed for later distillation while preserving source provenance and governed originals. Use when new documents, interviews, meetings, external-tool records, research, or contradictory source material must enter the repository without becoming agreement truth.
---

# Context Collection

Land durable references and only the minimum extracted notes needed for
distillation. Collection preserves evidence; it does not decide what is true.

## Collect one topic

1. Create or select `.github/docs/context/<topic>/` and read its `INDEX.md` first.
2. Keep the source original in its governed system. Store an access-controlled
   URL or stable identifier plus the smallest excerpt or notes required to
   evaluate candidate requirements, decisions, terms, and conflicts.
3. Start every collected Markdown file with:

```yaml
---
source: <governed URL or stable source identifier>
retrieved: <YYYY-MM-DD>
method: <verbatim | export | interview | ai-summary | web-research>
collector: <human or agent/session identifier>
sensitivity: <public | internal | confidential>
status: raw
---
```

4. Update `INDEX.md` with one line per collected file: source, purpose, and why
   it matters. List contradictions and open questions before the file list.
5. Record which GitHub, MCP, or external tool produced an export. Re-verify
   `ai-summary` and `web-research` material before proposing agreement text.

## Preserve provenance

- Quote or paraphrase only what the reference supports. Mark interpretation.
- Collect conflicting sources side by side; do not silently reconcile them.
- Capture a durable reference when a requirement or decision appears in chat.
- Prefer reference-not-paste for PII, credentials, secrets, licensed archives,
  and controlled business data. If a safe reference cannot be stored, stop and
  ask the source owner for an approved alternative.
- Do not copy a full source archive merely for completeness.

## Keep the agreement boundary

Do not write or edit `REQ-###`, ADRs, non-goals, glossary definitions, agent
guidance, or implementation during collection. Open a collection PR or commit
that states what was added and its provenance. Route interpretation through
`$context-distillation` and a dedicated, human-reviewed agreement PR.

## Completion check

Confirm that each new note has provenance, every original remains at its
governed source, `INDEX.md` exposes conflicts and questions, extracted content
is minimal, and no fact exists only in the current session.
