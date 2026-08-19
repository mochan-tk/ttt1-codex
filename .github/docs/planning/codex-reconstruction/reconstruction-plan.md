# Full reconstruction plan: current Copilot kit to Codex

Status: planning package awaiting human review<br>
Planning Task: [#59](https://github.com/mochan-tk/ttt1-codex/issues/59)<br>
Phase-1 Epic: [#58](https://github.com/mochan-tk/ttt1-codex/issues/58)<br>
Captured: 2026-08-19

This plan reconstructs current behavior rather than copying product-specific
files. It makes no reconstruction implementation change. The source repository
was read-only; the target changes are limited to proposed agreements, the
current capability map, and planning evidence.

## Fixed baselines

| Repository | Default branch | Full baseline SHA | Tree | Tracked files | Submodules |
|---|---|---|---|---:|---:|
| mochan-tk/agentic-dev-kit-for-copilot | main | fd265ddef150fab86cd54d0e383c2c25fe297ffb | 88f96493ec167602750c8dfec044629bd494a586 | 135 | 0 |
| mochan-tk/ttt1-codex | main | 0f114d2d98f8e906bf924a4fab873897c38963e1 | 8b431a48347a15958e5445ecd258d8f7b98573b1 | 129 | 0 |

Capture time is 2026-08-19T02:10:59Z. The source was cloned outside every
target worktree, checked out detached, and given a disabled push URL. The target
baseline is the merged default-branch state before Task #59. Later branch
movement is drift, not permission to silently move either baseline.

Exact commands and identities are in [baselines.json](baselines.json).

## Audit method and closure

Three bounded read-only audits ran in parallel:

1. Source tree and current-source behavior, including every tracked path,
   post-historical changes, tests, enforcement, open limitations, and
   distribution boundaries.
2. Target tree, merged controls, hosted/live evidence, open work, ownership,
   runtime proof, and stronger extensions.
3. Official Codex primary documentation, pinned stable openai/codex source, and
   direct versioned read-only observations.

The Task supervisor independently reconciled the reports with the pinned trees,
current GitHub APIs, and official primary sources.

- [source-inventory.json](source-inventory.json) has exactly 135 file rows.
- [target-inventory.json](target-inventory.json) has exactly 129 file rows plus
  the time-stamped open-work/live-control snapshot.
- [parity-ledger.json](parity-ledger.json) has 61 major-behavior rows.
- No open Issue, PR, draft artifact, document assertion, or fixture is treated
  as merged/runtime implementation.

Evidence is calibrated as pinned definition, deterministic fixture, hosted
observation, official documentation, version-pinned official source, direct
runtime observation, external product state, or human decision. These levels
are not interchangeable.

## Current-source delta

Historical PR #37 first pinned 110-file source
f466c7e169243e2bea03b4b33a20f8c557328d96. The later target map pinned
20637b703cbde6abd8934fc222abbe6c82bb4568
with 110 files. The current source adds 25 paths, modifies 34, deletes none (59
changed paths total), and changes the architecture materially:

- Project conductor above sibling Epic conductors;
- Task supervisor separated from one isolated worker per PR;
- exact durable dispatch/release and replacement sequence;
- a pre-commit small-Task no-worker declaration;
- Project/Epic/Task/PR session naming;
- separated review mechanisms and HOTL/HITL/Human-in-Command authority;
- ownership-overlap, governance-drift, and effective-governance sensors;
- solo/team source-bound ruleset profiles with persisted intent;
- Windows Git Bash launcher and platform capability checkpoints;
- plugin distribution no-go/unknown evidence;
- HOTL README redesign.

Current source limitations are also first-class:

- ritual session IDs are recorded but not authenticated;
- Outcome/Evidence, worktree isolation, role authorization, and complete
  actor/freshness checks are not enforced;
- source-specific ADR/context records now leak through installer-copied adopter
  namespaces, contradicting source documentation;
- onboarding still calls a legacy no-profile ruleset path;
- README lacks operator commands claimed by recent changelog text;
- run.ps1 has Windows evidence while scaffold-init.ps1 does not;
- plugin activation/update/cross-surface behavior remains unproved;
- source Issue #6 retains external-delegation threat-model work.
- stacked/multi-PR mechanics are explicitly off pending a post-GA evaluation
  at `#89`, but live source `#89` is an unrelated closed, unmerged governance
  PR, so activation is UNKNOWN.

The target preserves its stronger namespace separation instead of copying the
source regression.

## Behavioral result

| Status | Count |
|---|---:|
| PARITY | 10 |
| CODEX_NATIVE | 5 |
| EXTENSION | 14 |
| GAP | 10 |
| PARTIAL | 13 |
| NON_PORTABLE | 4 |
| UNKNOWN | 5 |
| **Total** | **61** |

The [capability map](../../guides/copilot-capability-map.md) summarizes the
rows. The JSON ledger is authoritative.

### Principal gaps

- Task-supervisor to isolated per-PR-worker lifecycle;
- separately gated stacked/multi-PR activation, whose source `#89` authority is
  unresolved and must remain off;
- dispatch/release/successor identity and deterministic validation;
- pre-commit small-Task exemption;
- provider-neutral writer lease, replacement, and stale-writer exclusion;
- ownership-overlap, governance-drift, and effective-governance sensors;
- current source profile/persisted-governance behavior;
- source agent-tool allowlist reconciliation, which has no direct Codex
  per-tool equivalent despite safer target read-only defaults;
- Windows command launcher and Codex capability drift baseline;
- live source-bound required-check enforcement.
- dangling target authority references from REQ-016/REQ-017 to nonexistent
  ADR-0006; a separately owned agreement cleanup must resolve them.

### Principal Codex-native mappings

- Copilot instructions become AGENTS.md, agreements, and focused Skills.
- Copilot agents/prompts become Codex custom-agent TOML and Skill invocation
  metadata.
- Eight lifecycle Skills move to .agents/skills; target keeps the ninth
  codex-automation Skill.
- Product session semantics become logical roles over durable GitHub records.
- Product-specific editor/workflow files are omitted with explicit rationale.

### Principal retained target extensions

- base-owned, no-checkout admission and bootstrap denial;
- exact repository/base/head/file/rename/diff-digest binding;
- exact public-fork authorization, revocation, cancellation, and no credential
  bridge;
- isolated candidate workers and fail-closed exact-head publisher;
- source-bound disabled-only exact-compatible ruleset proposal;
- immutable Plan edit history and chronology;
- dual CODEOWNER and human authority;
- collision/symlink/immutable-ref/provenance/stage-only installer;
- adopter-truth-preserving upgrade;
- plugin byte/mode synchronization and partial-install degradation;
- privacy-minimized consent-gated feedback;
- checked connector/activation boundary;
- Codex-owned secure Dev Container namespace and existing proof chain;
- explicit refusal to infer release/runtime/product state from static files.

No source parity Task may weaken these controls.

## Proposed architecture

[ADR-0005](../../agreements/adr/ADR-0005-codex-reconstruction-execution-model.md)
separates six planes:

1. GitHub/Git durable work;
2. Codex execution topology;
3. isolated writer workspace and lease;
4. deterministic and human verification;
5. agreements/effective governance;
6. measured learning and source-update tracking.

The logical flow is:

```text
Project conductor
  -> sibling Epic conductor
     -> Task supervisor
        -> isolated PR worker A
        -> sequential replacement worker B, only after A is durably released
        -> bounded read-only auditor/reviewer
```

One Task has one supervisor, one authoritative Plan, and—while REQ-053
stands—at most one writing PR. That PR has at most one active worker, isolated
worktree, branch, active lease, and ownership boundary. The supervisor does not
write while a worker is active. A later disjoint multi-PR topology requires a
separate human agreement superseding REQ-053. Ordinary Codex subagents remain
read-only because current V2 shares one CWD/filesystem.

A small Task may keep the supervisor as writer only when the pre-commit Plan
contains the exact no-worker declaration. Read-only acceptance Tasks with no
File ownership may close by measured Issue Outcome/Evidence without fabricating
an empty PR.

Every worker dispatch is provider-neutral and binds the Task/Plan, explicit
provider, surface and versioned runtime, monotonically increasing attempt,
durable supervisor and worker references, repository/PR, exact branch/base,
stable worktree identity, ownership boundary, lease/predecessor, verification,
and stop conditions. Future ritual validation must reject a missing or
ambiguous field; runtime thread identity remains only one correlated reference.

## Official Codex findings

The [current capability research](codex-capability-research.md) records primary
sources and surface/maturity limits.

Important conclusions:

- Stable Multi-Agent V2 source supports descendants.
- Current ordinary subagents share the parent container/filesystem/CWD and are
  not writer isolation.
- Exact V2 depth, queueing, budgets, heartbeat, failure/orphan propagation, and
  durable ancestry remain UNKNOWN.
- App Server lineage/lifecycle is experimental.
- Desktop managed worktrees isolate working copies but permanent worktrees may
  host multiple chats, so the active-writer lease remains necessary.
- Cloud result, branch/commit/PR, and GitHub checks are separate.
- IDE-to-Cloud delegation is documented as a new cloud chat carrying chat
  context and local source changes; identity-preserving handoff and exact Git
  continuity remain UNKNOWN.
- Hooks are incomplete lifecycle/path enforcement.
- Plugins and Scheduled tasks have surface-specific product-state boundaries.
- ChatGPT Projects, local projects, threads, and GitHub Issues are distinct.

## Runtime evidence backlog

Detailed, blocked, not-ready spike Tasks exist:

- [#72 — thread lineage, nesting, and controls](https://github.com/mochan-tk/ttt1-codex/issues/72)
- [#73 — subagent checkout sharing and collisions](https://github.com/mochan-tk/ttt1-codex/issues/73)
- [#74 — managed worktree, branch, and handoff](https://github.com/mochan-tk/ttt1-codex/issues/74)
- [#75 — permission and failure propagation](https://github.com/mochan-tk/ttt1-codex/issues/75)
- [#76 — recovery, replacement, and stale-writer exclusion](https://github.com/mochan-tk/ttt1-codex/issues/76)
- [#77 — app/CLI/IDE/cloud continuity](https://github.com/mochan-tk/ttt1-codex/issues/77)
- [#78 — concurrency, budgets, and observability](https://github.com/mochan-tk/ttt1-codex/issues/78)

The [spike program](runtime-capability-spikes.md) contains the common safety
protocol, 21 bounded experiments, evidence schema, cleanup, stop conditions,
and readiness gate. None is authorized by this plan.

## Rolling-wave phase graph

All phase Epics are siblings. Dependency arrows mean the later phase is
blocked by the earlier phase.

#58 planning
  -> #60 runtime evidence
  -> #61 supervisor/PR-worker lifecycle
  -> #62 provider-neutral isolation/replacement
  -> #63 ritual/ownership/governance/review/CI
  -> #64 onboarding/installer/plugin/Windows/distribution
  -> #65 live adoption/recovery/release readiness

Additional integration blockers:

- #63 is blocked by existing secure Dev Container Task #33, which retains the
  #49/#50/#51/#52 admission proof chain and overlapping CI/governance ownership.
- #65 is blocked by existing release Epic #40.
- Old work is integrated, not closed, repurposed, or silently superseded.

### Phase 1 — planning acceptance

Parent: [#58](https://github.com/mochan-tk/ttt1-codex/issues/58)

- [#59](https://github.com/mochan-tk/ttt1-codex/issues/59): create this
  planning package and draft PR; the sole ready Task.
- [#66](https://github.com/mochan-tk/ttt1-codex/issues/66): independently
  accept baselines and exact inventory closure.
- [#67](https://github.com/mochan-tk/ttt1-codex/issues/67): independently
  accept parity statuses and extensions.
- [#68](https://github.com/mochan-tk/ttt1-codex/issues/68): accept official
  Codex claims.
- [#69](https://github.com/mochan-tk/ttt1-codex/issues/69): accept spike
  briefs and evidence controls.
- [#70](https://github.com/mochan-tk/ttt1-codex/issues/70): post-merge
  verification of the human architecture decision, blocked by #59 and #66-#69.
- [#71](https://github.com/mochan-tk/ttt1-codex/issues/71): current-source
  drift checkpoint without moving accepted history.

Tasks #66-#71 are read-only acceptance Tasks, own no files, and remain not
ready. Proposed REQ-049 permits this narrow no-fake-PR mode only after human
agreement merge, so these Tasks are post-merge checkpoints. The independent
pre-publication review remains part of #59 and its Planning PR.

### Phase 2 — runtime evidence

Parent: [#60](https://github.com/mochan-tk/ttt1-codex/issues/60). The seven
spike briefs are created because the reconstruction Definition of Done requires
them, but they remain blocked by #58 and not ready. The Epic conductor selects
only one safe executable wave after planning acceptance.

### Phases 3 through 7

Epics [#61](https://github.com/mochan-tk/ttt1-codex/issues/61) through
[#65](https://github.com/mochan-tk/ttt1-codex/issues/65) intentionally remain
coarse. Each is decomposed just in time after predecessor Outcome, current
source-drift check, ownership reconciliation, evidence review, and available
human review capacity. [issue-graph.json](issue-graph.json) records every
created node and edge.

## Phase outcomes

### Phase 3 — supervisor and worker lifecycle

Introduce logical roles, Task-to-PR cardinality, dispatch/release records, the
complete provider/attempt/supervisor/worker identity tuple, small-Task
exemption, reviewer boundaries, and deterministic lifecycle fixtures. Keep
stacked/multi-PR Tasks disabled under REQ-053 until #71 resolves the source gate
and a later human agreement explicitly activates them. No runtime topology
assumption may exceed phase-2 evidence.

### Phase 4 — provider-neutral isolation

Implement worktree allocation, branch/PR lease, disjoint ownership, process and
Git inspection, handoff, crash recovery, release, replacement, stale-writer
refusal, and reversible cleanup across accepted surfaces.

### Phase 5 — governance and admission convergence

Add worker ritual, ownership overlap, governance manifest/status/drift,
solo/team intent, and review separation while preserving base-owned admission,
public-fork handling, exact-head/source-bound publishing, and the existing
#33/#49-#52 evidence chain. Live Settings remain separate high-risk human work.

### Phase 6 — onboarding and distribution convergence

Update Project naming, onboarding/operator mapping, installer distribution,
Windows launcher/native proof, plugin boundaries, capability drift, and source
update flow. Preserve target installer safety and do not copy source namespace
leakage.

### Phase 7 — adoption and release readiness

Run controlled fresh adoption, upgrade, recovery, replacement, rollback,
hosted checks, effective-rule inspection, Windows/plugin/cloud evidence, and
residual-risk review. Human merge, Settings, tag, release, and publication are
separate decisions.

## Risk and unknown register

| Risk | Current control | Planned resolution |
|---|---|---|
| Shared-CWD subagent writers collide | Ordinary subagents remain read-only | #73, #62 |
| Experimental/unstable lineage becomes authority | GitHub/Git fallback; ancestry advisory only | #72, ADR-0005 |
| Stale writer resumes after replacement | No replacement implementation yet | #76, #62 durable lease |
| Target security is weakened for source parity | EXTENSION rows are non-regression requirements | #67 review, REQ-051, #63 |
| Active ruleset ignores statuses | Human/code-owner review remains; no passing claim | #50-#52, #63 |
| Source distribution regression is copied | Preserve target namespace separation | #64 |
| Product/plugin/Windows/release claims are inferred | Explicit evidence levels and release limits | #77, #64, #65 |
| Source moves after audit | Fixed baselines are immutable | #71 synchronization |
| Historical semantic test blocks current map | Labeled 110-file compatibility appendix retained | Separate map/test synchronization after #59 |
| Planning artifacts placed in wrong worktree | Byte-identical recovery completed and recorded | Task #59 Revised Plan and recovery comments |

## Planning verification

Before publication:

- parse every JSON artifact;
- prove exact source and target path/blob coverage at fixed SHAs;
- validate 61 parity rows, status vocabulary, paths, evidence, links, and counts;
- verify every sub-issue/dependency edge and expected readiness;
- validate Markdown links;
- run the repository deterministic suite;
- inspect the final ownership allowlist and planning-only diff;
- obtain a separate read-only review with no unresolved P0-P2 finding.

After publication:

- inspect checks on the actual draft PR head;
- treat absent, stale, skipped-applicable, action-required, or wrong-head checks
  as non-success;
- post measured Outcome/Evidence to #59;
- do not approve or merge.

The existing semantic test intentionally requires the historical 20637b/110
table and deferred-boundary phrases. Because that test is outside #59
ownership, the current capability map keeps a clearly labeled superseded
compatibility appendix. It is not current audit authority.

## Definition of Done for the full reconstruction

The program is done only when:

1. Every GAP is implemented and accepted, every PARTIAL is either completed or
   explicitly accepted with residual risk, every UNKNOWN is experimentally
   resolved or bounded by a human-approved fallback, and every NON_PORTABLE
   row retains a reason.
2. Every EXTENSION has non-regression evidence.
3. Task supervisors and isolated PR workers recover from fresh GitHub/Git state
   and replacement cannot create concurrent writers.
4. Local and hosted tests prove ritual, ownership, governance, admission,
   installer, Windows, plugin, and distribution behavior at the actual heads.
5. Effective rules and trusted status sources are inspected, not inferred.
6. Controlled adoption, upgrade, crash recovery, rollback, and release
   readiness are observed.
7. Non-author human review accepts agreements and completion.
8. Settings, ruleset, tag, release, and publication decisions are separately
   authorized and evidenced.

A merged planning document, passing fixture, open Task, or agent report alone
does not satisfy the full reconstruction.

## Next steps

### Codex Project Conductor kickoff

1. Read every applicable `AGENTS.md`, starting at the repository root and
   following the directory chain for the work selected.
2. Open the draft Planning PR linked from #59 and read the exact PR head, full
   diff, checks, review state, Task Outcome, deviations, merged agreements,
   parity ledger, runtime-spike program, and this reconstruction plan.
3. Read Epic #58, every sibling phase Epic #60 through #65, the existing #33,
   #40, and #49 through #52 chains, and all live parent/blocker edges before
   changing readiness.
4. Recalculate the frontier from current GitHub state and recheck source and
   target default-branch SHAs; report drift to the #58 conductor and create no
   synchronization work from a read-only checkpoint.
5. Start only the first unblocked, ownership-disjoint Task selected by the
   responsible Epic conductor. A ready label is necessary but not sufficient.
6. Follow the current human-merged execution contract. Until REQ-053 is
   separately superseded, one implementation Task has at most one writing PR;
   stacked or multi-PR execution remains disabled.
7. After supervisor/worker parity is implemented and verified, use one durable
   Task supervisor and at most one active isolated worker for that writing PR,
   with one resolved worktree, branch, ownership boundary, dispatch identity,
   and release record. Sequential replacement requires prior release or human
   adjudication.
8. Do not cross Task ownership or begin later-phase implementation. Read-only
   acceptance Tasks #66 through #69 and #71 may run in parallel after #59 only
   when the #58 conductor confirms the frontier; #70 follows #66 through #69.
9. Treat Codex thread topology, lineage, resume, and handoff as runtime
   correlation only. GitHub and Git remain the durable recovery authority.
10. Record immutable claim/Start, current Plan, worker dispatch/release where
    applicable, fresh Evidence, and Outcome before reporting completion.
11. Do not approve or merge a PR, change Settings or rulesets, create a tag or
    release, publish a plugin, or expand credentials without separate explicit
    human authority.
12. Stop at every human gate or unresolved identity/ownership/cleanup state;
    report the blocker with evidence instead of guessing or weakening a wall.

After human merge closes #59, #66 through #69 and #71 form the bounded
post-merge read-only frontier. #70 follows #66 through #69 and verifies the
agreement decision. When #58 closes, wake #60 and select only the first safe
runtime spike. Keep #61 through #65 coarse until predecessor Outcomes are
accepted, and preserve the older proof/release chains.

Human review and merge of the draft Planning PR are the only next authority.
