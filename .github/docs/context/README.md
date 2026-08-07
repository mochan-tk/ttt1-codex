# Context intake

`.github/docs/context/` holds only the minimum notes and provenance references needed
to distill project truth. It is background, not authority; implementation must
follow reviewed agreements in `.github/docs/agreements/`.

Keep source originals in their governed external locations. Do not commit raw
archives, exports, recordings, credentials, PII, or controlled business data.
For sensitive material, record only the minimum access-controlled reference
needed by an authorized reader.

Create one directory per topic with an `INDEX.md`. Every intake entry must
record provenance and the minimum extracted notes needed for distillation:

- source title and stable URL, record ID, or other governed locator;
- source owner or publisher;
- retrieval date and collection method;
- collector;
- sensitivity classification and access constraints;
- intake status (`raw` or `distilled`);
- the minimum extracted facts needed for distillation;
- why each extracted fact matters; and
- conflicts, uncertainty, and open questions without silently resolving them.

Paraphrase instead of copying long passages. If even a paraphrase would expose
controlled information, keep only the governed locator and access note. A
distillation pass may propose requirements, non-goals, glossary entries, or
ADRs, but those become authoritative only through a dedicated agreement PR.
