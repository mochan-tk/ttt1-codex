# ADR-0007: Bounded agent merge invocation

- Status: accepted only by the agreement merge
- Date: 2026-08-23
- Owners: repository owner and agreement reviewers
- Origin: Task #81, derived from Task #80
- Narrowly supersedes: REQ-004, REQ-021, and ADR-0002 section 8 only
  when every exception condition in this decision is satisfied
- Bootstrap exclusions: this agreement PR and the first always-on
  constitution-alignment PR

## Context

The accepted operating model concentrates human judgment in agreement,
license, and completion merge events. REQ-004 and ADR-0002 describe all three
as human merge events, and REQ-021 requires non-author human approval before
completion. Those are the secure defaults and remain authoritative outside the
complete exception defined here.

Task #80 exposed a solo-maintainer release failure mode. Deterministic checks,
Task Evidence, and a reviewed temporary pull-request-only bypass could all be
present while the final merge still depended on a human being available for a
short UI window. Repeating the window added Settings churn without improving
the evidence or reducing risk.

The initially proposed exception applied only to completion PRs and relied on
a human and executor sharing one GitHub login. Independent review found two
blocking defects:

- PR #79 changes accepted-agreement candidates as well as completing its Task,
  so a completion-only exception could not achieve the motivating result; and
- GitHub records could not distinguish a human authorization from executor
  text when both used `mochan-tk`.

The requester therefore selected a narrower trust boundary with broader merge
classification. A distinct human GitHub principal makes the durable decision;
the primary executor may perform only one exact mechanical invocation for an
agreement or completion merge. License merges stay human-executed. The first
agreement and guidance changes that establish this mechanism also stay
human-executed, so the exception cannot bootstrap itself.

The owner prioritizes a repeatable, low-friction path through the first public
OSS release. Speed comes from Codex preparing each exact authorization and
handling the preflight, one merge call, restoration, and receipt. It does not
come from a standing bypass, wildcard approval, or skipped check.

## Decision

### 1. Default, eligible classes, and bootstrap

- Agreement, license, and completion merge decisions remain human-governed.
- License merges are always human-executed.
- Agreement and completion merges are human-executed by default.
- After the two bootstrap merges below, a primary Task executor may perform
  one exact mechanical invocation for an agreement or completion merge under
  a valid bounded agent merge-invocation license.
- This ADR's own agreement PR and the first PR that aligns root `AGENTS.md` and
  operational guidance are non-delegable bootstrap merges. Both require
  non-author human review and human merge under the prior constitution.
- The exception becomes executable only in a fresh session after both
  bootstrap PRs are merged and the aligned guidance is loaded.

This explicitly and narrowly supersedes REQ-004, REQ-021, and ADR-0002 section
8 for a fully compliant invocation. Outside that invocation, their existing
requirements remain authoritative. REQ-033 remains the secure default
ruleset; the exception may use only the identity-specific temporary bypass
defined below without changing that default.

### 2. One merge-execution Task and two principals

Every invocation begins with one requester-owned `risk:high` merge-execution
Task. Its body and exact approved Plan must bind the same:

- repository and canonical pull-request URL;
- merge class (`agreement` or `completion`);
- base branch and exact 40-character head SHA;
- merge method and expiration;
- authorizer and executor GitHub logins;
- formal-review choice;
- ruleset, bypass actor, bypass mode, and restore digest; and
- encoded conditions.

The authorizer is a human GitHub principal whose credential and signed-in
session are unavailable to the executor environment. The executor must not
request, access, operate, or receive that identity. The authorization-comment
author must equal the named authorizer, while the active GitHub credential
must equal the named executor. Those logins must differ.

Fresh API reads must prove both principals still have the permissions required
by the approved Plan. If formal non-author review is waived, the authorizer
must also differ from the PR author. A same-login process convention, chat
message, or executor assertion is not a distinct-principal boundary.

### 3. Exact authorization record

After final exact-head checks, durable Outcome/Evidence, and independent Codex
review exist, the authorizer must post one unedited single-line comment in
exactly this field order, with no leading, trailing, or additional text:

```text
Approved agent merge: <full-PR-URL> @ <40-lowercase-hex-SHA> — base=<ref>; method=<merge|squash|rebase>; merge-class=<agreement|completion>; expires=<YYYY-MM-DDTHH:MM:SSZ>; authorizer=<github-login>; executor=<github-login>; non-author-review=<required|waived>; ruleset=<none|decimal-id>; bypass-actor=<none|User:decimal-id>; bypass-mode=<none|pull_request>; restore-digest=<none|sha256:64-lowercase-hex>; conditions-b64url=<unpadded-base64url>
```

Validation fails closed unless:

- the URL is exactly
  `https://github.com/<owner>/<repo>/pull/<positive-decimal>` and resolves to
  the Task's repository and PR;
- the head is exactly 40 lowercase hexadecimal characters and equals the live
  PR head;
- the base is the live PR's short branch name, and invoking
  `git check-ref-format --branch <base>` without shell evaluation succeeds and
  prints exactly the input value; normalization, `refs/heads/` prefixes,
  previous-checkout expressions such as `@{-1}`, and option-like names are
  invalid;
- the method and merge class use exactly one listed lowercase value;
- expiry uses canonical UTC `YYYY-MM-DDTHH:MM:SSZ`, is unexpired, and remains
  inside the approved Plan's window;
- both logins resolve exactly through GitHub and match the comment author and
  active executor credential as defined above;
- every numeric identifier is positive decimal, and a non-`none`
  `bypass-actor=User:<id>` uses the exact immutable GitHub user ID freshly
  resolved for the named executor;
- the restore digest is `sha256:` followed by 64 lowercase hexadecimal
  characters when Settings are used and is computed exactly as section 6
  defines;
- `conditions-b64url` is non-empty unpadded base64url that decodes as UTF-8 to
  the exact conditions accepted by the approved Plan; and
- no field is unknown, missing, duplicated, empty, reordered, or followed by
  extra text.

The authorization must be unedited, later than the final Evidence and Codex
review it accepts, consistent with the latest approved Plan and Task body,
unexpired, and unused. Agent-authored text, a reaction, chat consent, a generic
"merge when green" statement, a branch-wide approval, and a wildcard or
recurring grant are invalid.

This merge authorization must also post-date the merge-execution Task's latest
unedited Start or Resume ownership claim and is valid only inside that same
continuous primary-executor session. Every new or recovered executor session
must first post the constitutionally required Resume record. Any later Start,
Resume, ownership transfer, process replacement, or session handoff invalidates
the authorization before further action, regardless of whether a consumption
comment is visible. The authorizer must post a fresh authorization after the
new claim and fresh final Evidence. This session rule applies to the
`Approved agent merge:` record, not to the separately governed Plan approval.

After final preflight and before any Settings mutation or merge request, the
executor must consume the license durably by posting this exact unedited
single-line comment to the merge-execution Task:

```text
Agent merge license consumed: <authorization-comment-URL> — attempt=<32-lowercase-hex>; pr=<full-PR-URL>; head=<40-lowercase-hex-SHA>; executor=<github-login>
```

`attempt` is a freshly generated 128-bit cryptographically secure random
value. The executor must receive the created comment ID, then re-read the Task
timeline and proceed only when this is the sole consumption record for the
authorization, remains unedited, and exactly matches the live authorization,
PR, head, and executor, and when the comment author's login equals the named
executor. A prior, duplicate, edited, mismatched, failed, or ambiguous
consumption write stops before Settings or merge. An ambiguous consumption
write burns the authorization even when the comment cannot yet be observed;
the current session must record a durable stop when possible and may never
retry. If that session ends before the stop can be recorded, the next required
Resume record independently invalidates the old authorization. A fresh
authorization after Resume is required and may never be reconstructed from
local state.

The authorization is consumed by that durable pre-send record, whether or not
any later Settings or merge request succeeds. Consequently, a process exit
after consumption cannot make the authorization reusable. Any later attempt
requires fresh Task state, Evidence, and human authorization, plus a Revised
Plan when the premise or approach changed.

### 4. Formal review choice

`non-author-review=required` is the default. The executor must then prove the
current non-author approval and CODEOWNER state required by the live ruleset.

`non-author-review=waived` is valid only for an explicit solo-maintainer
emergency after bootstrap, for the one exact agreement or completion PR and
head named in all authoritative records. The authorizer must differ from both
the executor and PR author, and the Task must record the missing eligible
review path and concrete release impact.

The waiver never applies to:

- a license merge;
- this ADR's agreement PR;
- the first constitution-alignment PR;
- CODEOWNERS, collaborator, ruleset-enforcement, or recurring-authorization
  changes; or
- any class, branch, repository, release, or time window rather than one exact
  PR and head.

The waiver replaces only the formal non-author PR review for that invocation.
It does not waive or fabricate deterministic checks, exact-head statuses,
Outcome/Evidence, independent Codex review, security findings, mergeability,
required thread resolution, Plan approval, identity proof, authorization, or
Settings restoration. Evidence must say that formal review was waived and
name the distinct authorizer who made the human merge decision.

### 5. Fresh preflight and drift

Immediately before any Settings or merge write, fresh GitHub and Git evidence
must prove:

- the Task body, latest Plan, exact Plan approval, and authorization are
  intact and unedited where required;
- the authorization post-dates the latest unedited Start or Resume ownership
  claim, no later session or ownership record exists, and the same continuous
  primary-executor session is still active;
- the authorization schema, authorizer, executor, current permissions, and
  identity-separation rules all pass;
- the PR is open, ready, non-draft, mergeable, targets the authorized base,
  and still has the authorized head;
- every required status is successful on that head, with no missing, pending,
  stale, skipped, or failing required result;
- durable Task Outcome/Evidence and independent Codex review cover the final
  diff and no blocking security finding remains;
- the PR contract, closing reference, Plan link, and required thread state are
  intact;
- the selected formal-review mode is satisfied exactly as recorded; and
- the live ruleset and every protected Settings field match the approved
  preflight snapshot and authorization tuple.

Task, Plan, approval, authorization, identity, permission, head, base, check,
review, thread, mergeability, ruleset, ownership, or conflicting-PR drift
stops the operation before the merge request. The executor does not repair or
infer authority during the merge window.

### 6. Exact Settings tuple and restoration

When `ruleset=none`, `bypass-actor`, `bypass-mode`, and `restore-digest` must
all be `none`; no Settings mutation is permitted.

Otherwise the authorization must contain:

- one positive-decimal ruleset ID;
- one exact `User:<positive-decimal-id>` bypass actor whose ID equals the
  immutable GitHub user ID freshly resolved for the named executor;
- `bypass-mode=pull_request`; and
- the protected preflight `sha256` digest.

The protected ruleset projection is one JSON object with exactly the writable
REST fields `name`, `target`, `enforcement`, `bypass_actors`, `conditions`, and
`rules`, copied without semantic normalization from the fresh preflight GET.
Server-managed or read-only response fields, including `id`, `node_id`,
`source`, `source_type`, `created_at`, `updated_at`, `_links`, and
`current_user_can_bypass`, are excluded. Missing any protected field, or a
GitHub API contract that exposes another writable ruleset field, stops closed
until a later agreement defines the new projection.

`restore-digest` is `sha256:` plus the lowercase SHA-256 hexadecimal digest of
the UTF-8 bytes of that projection serialized with the JSON Canonicalization
Scheme (RFC 8785). Object keys therefore use the RFC's deterministic order,
arrays preserve their API order, and no insignificant whitespace is present.
The exact preflight projection is also retained as the restore payload; the
digest alone is never used to reconstruct it.

The same merge-execution Task and exact approved Plan must own that tuple.
After the durable consumption record exists, the executor must install
signal-safe cleanup before mutation and submit an update projection that is
byte-for-byte identical after canonicalization except that `bypass_actors`
contains one additional object with exactly `actor_type="User"`,
`actor_id=<executor-user-id>`, and `bypass_mode="pull_request"`. Every existing
bypass actor and its array order remain unchanged; the new actor is appended.
Fresh GET projections after add and restore must equal the canonical expected
projection and original preflight projection respectively. The executor must
continuously monitor the exact PR, head, ruleset, and deadline.

After success, failure, signal, timeout, or ambiguity, the temporary bypass
must be restored to the exact preflight state and digest before the executor
reports, hands off, or ends the Task session. Failed restoration is a live
incident requiring continued bounded cleanup or durable human escalation; it
is never successful completion.

No persistent, role-wide, team-wide, app-wide, branch-wide, repository-wide,
or release-wide bypass is allowed. Automation may not enable enforcement.

### 7. One mechanical merge invocation

The only permitted merge write is one invocation equivalent to:

```text
gh pr merge <N> --repo <owner/repo> --<merge|squash|rebase> --match-head-commit <40-character-head-SHA>
```

The executor must use the authorized method and exact head. `--admin`,
`--auto`, agent review submission, merge-queue manipulation, branch deletion,
another PR write, and any unlisted mutation are prohibited. The executor sends
at most one merge request and never retries an ambiguous response.

### 8. Receipt and ambiguous result

After the invocation, read-only GitHub and Git observations must record:

- the Task, Plan approval, authorization, and Codex-review URLs;
- authorizer, executor, PR author, current permission observations, comment
  creation time, expiry, consumption-comment URL, attempt value, and consumed
  state;
- repository, PR, merge class, base, exact source head, method, merge actor,
  merge commit, and timestamps;
- every final check, formal-review mode, security, and thread result;
- the complete Settings before/add/restore history and protected digest when
  applicable; and
- the resulting base-branch observation or exact stop reason.

If the merge response is ambiguous, the executor performs no second write. It
restores temporary Settings, observes the PR and base read-only, marks the
authorization as already consumed by the pre-send record, and records either
the proven exact merge or a
`needs:human` outcome. An agent statement without those observations is not
Evidence.

### 9. Pre-release operation and sunset

Until the first public OSS release, Codex may make this path low-friction by
preparing the exact per-PR authorization line and performing every authorized
read, preflight, Settings transition, merge invocation, restoration, and
Evidence step. The distinct human authorizer still posts the prepared line for
each PR. One authorization never covers a second PR or head.

After the public release, a separate Issue-first, `risk:high` sunset Task may
remove or disable the temporary always-on alignment and its executable helper
surfaces. Because every Settings bypass is restored inside its merge Task, the
sunset must not depend on a persistent live bypass. This ADR remains reviewed
history until a later human agreement merge supersedes it.

### 10. Requirements-ledger ownership

The open reconstruction PR owns `.github/docs/agreements/requirements.md`.
This ADR records its narrow supersession explicitly without creating a second
writer. A later dedicated agreement change may reconcile requirement status
only after that ownership ends.

## Consequences

- Human judgment remains durable and attributable to a principal distinct
  from the executor, while the exact final invocation can be delegated.
- The mechanism can handle PRs that are both agreement and Task completion,
  including the motivating classification that blocked the first draft.
- License and bootstrap merges remain human-executed.
- Required checks, Evidence, Codex review, security, identity, and restoration
  gates cannot be exchanged for release speed.
- The live default ruleset and ordinary review path remain unchanged.
- A failed or ambiguous invocation consumes the license, preferring one
  visible stop over an unbounded retry loop.
- GitHub records the active credential as merge actor. The separate human
  authorization and full receipt make delegated execution explicit in the
  durable ledger.

## Negative cases

The exception is invalid for:

- any license, bootstrap agreement, or bootstrap alignment merge;
- a CODEOWNERS, collaborator, enforcement, or recurring-authorization change;
- a generic, edited, expired, reordered, incomplete, branch-wide, wildcard,
  release-wide, or chat-only authorization;
- an authorization older than the latest Start or Resume record, or use after
  a process replacement, session handoff, ownership transfer, or recovery;
- equal authorizer and executor identities, an authorizer identity available
  to the executor, or a waived review whose authorizer is the PR author;
- a different repository, PR, merge class, head, base, method, actor, or
  Settings tuple;
- a bypass actor that is not the freshly resolved executor User ID, or a
  restore digest that is not computed from the exact protected projection;
- a missing, prior, duplicate, edited, mismatched, failed, or ambiguous
  pre-send consumption record;
- missing, stale, pending, skipped, or failing required checks;
- an unresolved blocking security finding or required review thread;
- an agent-authored Plan approval, review, or merge authorization;
- `--admin`, `--auto`, branch deletion, merge-queue manipulation, or more than
  one merge invocation; or
- a temporary bypass left active at report, handoff, or session end.

## Validation

The agreement PR must show:

- an agreement-only two-path diff with no intersection with PR #79;
- the exact authorization schema, deterministic grammar, distinct-principal
  checks, eligible merge classes, bootstrap/license exclusions, review choice,
  preflight, one-write, restoration, receipt, and negative cases in this ADR;
- matching vocabulary in the glossary;
- passing Markdown, policy wording, Python, portable, and hosted checks;
- independent Codex review that resolves the prior completion-only,
  same-principal, and undefined-Settings findings; and
- non-author human review plus a human agreement merge.

The first constitution-alignment Task must add deterministic positive and
negative fixtures for authorization parsing, exact-head binding, principal
separation, permission, expiry, edit detection, review choice, Settings tuple,
canonical ruleset projection and digest, durable pre-send consumption,
Start/Resume invalidation, one-call behavior, ambiguity, and restoration before
the exception is used.

## References

- [Task #81](https://github.com/mochan-tk/ttt1-codex/issues/81)
- [Governance-change trigger](https://github.com/mochan-tk/ttt1-codex/issues/80#issuecomment-5386224996)
- [Independent review stop](https://github.com/mochan-tk/ttt1-codex/issues/81#issuecomment-5386296078)
- [Requester-body reconciliation](https://github.com/mochan-tk/ttt1-codex/issues/81#issuecomment-5386332317)
- [ADR-0002](ADR-0002-adlc-operating-model.md)
- [Requirements](../requirements.md)
- [Glossary](../glossary.md)
- [RFC 8785: JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785)
