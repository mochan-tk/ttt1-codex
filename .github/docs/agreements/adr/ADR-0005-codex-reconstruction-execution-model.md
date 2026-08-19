# ADR-0005: Codex reconstruction execution model

- Status: accepted by the agreement merge
- Date: 2026-08-19
- Owners: repository owner and agreement reviewers
- Source baseline: mochan-tk/agentic-dev-kit-for-copilot at fd265ddef150fab86cd54d0e383c2c25fe297ffb
- Target baseline: mochan-tk/ttt1-codex at 0f114d2d98f8e906bf924a4fab873897c38963e1
- Planning authority: Task #59 and its draft Planning PR

## Context

The current source has advanced from a single Task writer into a four-layer
Project conductor, Epic conductor, Task supervisor, and PR worker model. A Task
supervisor owns the work order, Plan, risk gate, worker dispatch, verification,
Outcome, and report. Each active PR worker owns one isolated worktree, branch,
PR, and implementation boundary. Replacement requires a durable release, and a
small Task may avoid a worker only when the supervisor declares that exception
in the Plan before the first commit.

The source also defines stacked PR mechanics, but explicitly keeps them off
until a post-GA evaluation recorded at `#89` passes. The live source record
`#89` is instead an unrelated closed, unmerged governance PR. The intended
activation record and current activation state are therefore UNKNOWN; the
defined shape is not evidence that multi-PR Tasks are enabled.

The target currently uses a simpler literal contract: one Task session is the
sole implementing writer and ordinary subagents are read-only. That contract is
safe, but it cannot represent the active source supervisor/worker lifecycle and
contains no separately gated stacked-PR shape.

Codex does not supply the durable ADLC hierarchy. Current stable Multi-Agent V2
does allow descendants, but ordinary subagents share one CWD and filesystem.
App Server ancestry and lifecycle methods are experimental. Exact V2 depth,
failure propagation, orphan handling, budgets, and cross-surface continuity are
not stable architecture authority. Desktop managed worktrees provide separate
working copies, but multiple chats can use a permanent worktree and therefore
still need an active-writer rule.

The target also contains controls stronger than the source: base-owned
admission, exact-head and repository identity binding, public-fork
authorization, fail-closed status publication, source-bound disabled-only
ruleset proposals, collision/symlink/provenance/staging installer safety,
plugin synchronization and degradation, stronger Plan chronology, and explicit
release-proof limits. Reconstruction must not weaken them.

## Decision

### 1. Separate six planes

The reconstruction uses six explicitly separate planes:

1. Durable work plane — GitHub Issues, comments, sub-issues, dependencies,
   commits, PRs, checks, reviews, and closing links.
2. Execution topology plane — Codex threads and surface-specific controls used
   to transport Project, Epic, Task-supervisor, reviewer, and worker roles.
3. Writer workspace plane — one isolated worktree, branch, PR, ownership set,
   and active writer lease for each writing worker.
4. Verification plane — deterministic local checks, isolated candidate
   workers, exact-head statuses, independent review, and human acceptance.
5. Governance plane — agreements, CODEOWNERS, effective-rule sensors, disabled
   proposals, risk gates, and human Settings authority.
6. Learning plane — measured Outcome, deviations, retro candidates, capability
   drift, and source-update synchronization.

No thread, UI sidebar, local plan cache, or hidden runtime state may replace a
durable GitHub/Git record.

### 2. Use a logical role hierarchy, not a required thread shape

The logical roles are:

- Project conductor: coordinates sibling phase Epics; never decomposes Tasks or
  implements.
- Epic conductor: decomposes only its phase just in time, controls the frontier,
  and verifies Task Outcomes; never implements.
- Task supervisor: owns one Task lifecycle, Plan, risk gate, PR decomposition,
  worker dispatch/release, verification, Outcome, and one-hop report; normally
  does not implement.
- PR worker: owns exactly one PR, isolated worktree, branch, active writer lease,
  and disjoint File ownership.
- Read-only auditor/reviewer: receives no writer lease or File ownership and
  reports one hop for independent ground-truth verification.

These roles may use nested threads only where a versioned runtime spike proves
the required controls. The safe default is independent or resumable Codex
sessions linked by GitHub records. A writing worker must never be an ordinary
same-CWD subagent.

### 3. Change the cardinality at the Task boundary

REQ-018's old literal equation is superseded by REQ-046, REQ-048, and REQ-049
for this reconstruction.

- One Task equals one Task supervisor and one authoritative Plan.
- One writing PR equals one PR worker, one isolated worktree, one branch, one
  active writer lease, and one disjoint ownership boundary.
- By default, one Task has at most one writing PR. Released replacement workers
  may act sequentially on that same PR.
- At most one active worker may write a given PR, worktree, branch, or ownership
  boundary.
- The supervisor does not write while any PR worker is active.
- Conductors and read-only auditors never receive implementation ownership.

GitHub Task and PR records, not thread ancestry, prove these relations.

Stacked or otherwise multi-PR Task execution remains disabled under REQ-053.
Task #71 must first resolve the source's broken `#89` activation reference. A
later human agreement, deterministic negative/positive coverage, and live
evidence must explicitly activate any multi-PR mode; this ADR does not do so.

### 4. Make dispatch and release durable

Before a worker writes, the Task supervisor posts an immutable dispatch record
containing:

- Task and Plan URL;
- explicit provider, Codex surface, and versioned runtime reference;
- monotonically increasing attempt number plus durable Task-supervisor and
  worker references;
- repository and PR number, or the planned PR identity before creation;
- exact branch, base SHA, worktree/managed-worktree stable name, and ownership;
- lease identifier, dispatch timestamp, and predecessor release when replacing;
- expected verification and stop conditions.

Personal absolute paths, credentials, and product-only hidden identifiers are
not recorded.

A worker may start only after the Plan and dispatch record. Before replacement,
the supervisor must stop or fence the old worker, inspect Git/process/worktree
state, preserve partial work, and post an immutable release. If the old writer
cannot be proven stopped, the supervisor pauses for human adjudication; elapsed
time or thread disappearance never releases a lease.

### 5. Preserve crash-only recovery

A fresh supervisor reconstructs state from the Task, immutable Plan history,
dispatch/releases, branches/worktrees, commits, PR heads/diffs, checks, reviews,
and process inspection where local work may remain. It records Resume and any
ownership transfer before action.

Thread lineage, archived transcripts, or sidebar state may assist diagnosis but
are never required to recover or authorize a writer.

### 6. Require a pre-commit small-Task exemption

A Task supervisor may implement a genuinely small Task without a separate PR
worker only when the authoritative Plan, posted before every Task commit,
contains the exact declaration no worker will be spawned and explains why one
PR and one writer are sufficient.

The exemption:

- is unavailable to Project or Epic conductors;
- does not bypass risk approval, ownership, worktree, branch, PR, Evidence,
  review, or human merge;
- becomes invalid if scope expands, a second PR is needed, or another writer is
  dispatched;
- is checked by the future Task-ritual wall.

### 7. Permit read-only acceptance Tasks without a fake PR

A Task whose body explicitly states File ownership: None and whose acceptance
criteria require only read-only inspection may complete with measured Outcome
and Evidence in the Issue and no worktree, branch, commit, or PR. It receives no
writer lease and may not modify repository files, product state, Issues other
than its authorized evidence record, Settings, rulesets, releases, or tags.

This amends REQ-007 only for the missing completion-PR edge: the Task must still
retain its Origin cross-reference, parent/sub-issue relation, dependencies, and
immutable measured Outcome/close record. It cannot fabricate an empty
`Closes #N` PR, and no other tracking or human-authority gate is removed.

This narrow exception supports post-merge acceptance Tasks #66 through #71
without manufacturing empty changes. Any required mutation converts the work
to an ordinary writing Task with a Plan, isolated writer, branch, and PR.

### 8. Gate runtime-dependent choices

Issues #72 through #78 own bounded disposable experiments for topology,
checkout sharing, managed worktrees, permissions, failure, recovery,
replacement, cross-surface continuity, concurrency, budgets, and observability.
Until their evidence is human-reviewed:

- ordinary subagents remain read-only;
- one-hop reporting and leaf-first cleanup remain conservative kit policy;
- deep nesting is optional transport, never required;
- experimental App Server identifiers are advisory only;
- provider-neutral GitHub/Git recovery is mandatory;
- no implementation or spike Task is ready.

### 9. Preserve stronger target extensions

Later phases must retain or strengthen:

- base-owned candidate admission and bootstrap denial;
- exact repository, head/base SHA, changed-file, rename, and diff-digest binding;
- public-fork exact authorization, revocation, and cancellation;
- isolated no-credential candidate workers;
- exact-head fail-closed status publishing and source-bound checks;
- disabled-only, exact-compatible ruleset proposals and human enablement;
- dual CODEOWNER review paths and non-author human acceptance;
- collision-, symlink-, immutable-ref-, provenance-, and stage-safe installation;
- upgrade preservation of adopter truth;
- plugin byte/mode synchronization and partial-install degradation;
- consent-gated privacy-minimized feedback;
- immutable Plan chronology, fresh Evidence, and truthful release limits;
- the Codex-owned secure Dev Container namespace and the existing #33/#49-#52
  proof chain.

Source behavior is not allowed to downgrade an existing target control.

## Rejected alternatives

### Copy the source thread topology directly

Rejected. Product-specific Copilot tools are not portable, current Codex
ordinary subagents share a checkout, and depth/lifecycle behavior is not a
durable contract.

### Keep one Task session as the permanent writer model

Rejected as the final reconstruction. It is safe but cannot express the active
source Task-supervisor/per-PR-worker lifecycle. It remains the fallback until
the new model is implemented and proved; its one-Task/one-PR bound also remains
in force until REQ-053 is deliberately replaced.

### Make App Server or thread ancestry the control plane

Rejected. The relevant API is experimental, lifecycle operations may partially
succeed, and product state cannot replace Issue/PR/check/review history.

### Allow parallel writers on disjoint files in one checkout

Rejected. Disjoint path intent does not isolate the Git index, branch, hooks,
processes, or accidental writes.

### Weaken target admission to match conventional source CI

Rejected. Reconstruction is behavioral parity plus retained extensions, not
lowest-common-denominator copying.

## Consequences

- The architecture defines one-writer safety per PR while keeping multi-PR Task
  activation explicitly off pending source clarification and a later human gate.
- Ordinary Codex subagents remain useful for read-only audit and review.
- Writing workers require explicit worktree allocation and a durable lease.
- The system remains recoverable when thread history or a product surface is
  unavailable.
- More GitHub comments and validation are required for dispatch, release, and
  replacement.
- Runtime spikes may choose an optimized topology, but cannot change durable
  authority or writer invariants.
- Evidence-only acceptance work no longer needs fake branches and PRs.
- Existing #33, #40, and #49 through #52 remain authoritative dependencies and
  are integrated rather than superseded.
- This Planning PR changes only agreements and planning artifacts; it does not
  implement any role, adapter, sensor, workflow, installer, hook, or runtime.

## Validation gates

Before implementation readiness, human reviewers must verify:

1. exact source and target inventory closure;
2. every parity row and retained extension;
3. official capability claims and all remaining UNKNOWN links;
4. the phase/sub-issue/dependency graph and lack of ai:ready on future work;
5. no overlap with #33, #40, or #49 through #52;
6. the current capability-map compatibility appendix is clearly historical;
7. all repository deterministic checks and actual draft-PR head checks;
8. no P0-P2 finding in the independent read-only planning review.

Before lifecycle rollout, phases #60 through #64 must supply runtime,
implementation, governance, Windows, and distribution evidence. Phase #65
supplies live adoption and release-readiness evidence. Human review, Settings,
merge, tag, release, and publication remain separate decisions.

## References

- [Parity ledger](../../planning/codex-reconstruction/parity-ledger.json)
- [Codex capability research](../../planning/codex-reconstruction/codex-capability-research.md)
- [Runtime spike program](../../planning/codex-reconstruction/runtime-capability-spikes.md)
- [Architecture guide](../../guides/architecture.md)
- [Official subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Official worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [Official App Server](https://learn.chatgpt.com/docs/app-server)
