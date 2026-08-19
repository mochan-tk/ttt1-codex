# Runtime capability spike program

Status: planned only; no experiment authorized or executed<br>
Parent: [Epic #60](https://github.com/mochan-tk/ttt1-codex/issues/60)<br>
Planning authority: [Task #59](https://github.com/mochan-tk/ttt1-codex/issues/59)<br>
Fixed source: fd265ddef150fab86cd54d0e383c2c25fe297ffb<br>
Fixed target: 0f114d2d98f8e906bf924a4fab873897c38963e1

The seven spike Tasks below exist because current primary evidence is
insufficient for architecture-changing runtime claims. They are blocked by
Epic #58, have no ai:ready label, and own only one future evidence file each.
Documentation evidence alone cannot make them ready.

## Common protocol

Every spike must:

1. Use a private disposable repository or fully local fixture with no production
   remote, hooks, credentials, personal data, or source/target checkout.
2. Capture UTC time, OS/architecture, exact app/CLI/IDE/cloud version, model,
   feature flags, permission profile, thread/task IDs, CWD, worktree registry,
   branch, HEAD, upstream, status, relevant process IDs, raw responses, UI
   actions, and initial/final hashes.
3. Distinguish evidence provenance (`DOCUMENTED`, `SOURCE-SUPPORTED`,
   `OBSERVED`, `INFERENCE`, `NOT TESTED`, or `UNKNOWN`) from the observed
   result (`SUPPORTED`, `PARTIAL`, `UNSUPPORTED`, or `UNKNOWN`).
4. Capture evidence before cleanup. Prefer archive to permanent deletion.
5. Resolve exact process, thread, worktree, branch, repository, and remote
   identity before stop, removal, or remote cleanup.
6. Stop on production-path selection, unexpected out-of-fixture write,
   authority expansion, credential exposure, unbounded spawning, ambiguous
   checkout/process identity, or uncertain cleanup.
7. Report a negative result as evidence. Timeout, invisibility, or absence is
   not support.
8. Never mutate repository Settings, rulesets, releases, tags, marketplace
   state, the read-only source, or the production target.
9. End with cleanup proof and a controlled decision; implementation belongs to
   a later Task.

### Replay contract imported by Tasks #72 through #78

Before a spike can become ready, its conductor must record the merged target
commit and blob SHA for this file. The executor then copies the relevant
experiment rows into the evidence report without weakening them and records:

- an environment row for every tested surface: surface/build, OS/architecture,
  model, feature flags, permission profile, isolated runtime home, disposable
  repository ID/path, and whether network or GitHub access is enabled;
- the exact setup commands below, with unavailable commands marked `NOT
  TESTED` rather than silently omitted;
- every numbered experiment command, App Server request, or UI action verbatim,
  including input IDs and bounded stop conditions; and
- one expected-versus-observed row per action, with separate `provenance`,
  `result`, raw-evidence reference, and decision fields.

Common shell snapshot (run only inside the resolved disposable fixture):

```sh
codex --version
codex features list
git rev-parse --show-toplevel
git rev-parse HEAD
git branch --show-current
git status --short
git worktree list --porcelain
```

For App Server work, record the exact JSON-RPC request and response for each
`thread/start`, `thread/list`, `thread/read`, `thread/resume`, `turn/steer`,
`turn/interrupt`, and archive action actually used. For app, IDE, web, or cloud
work without a command interface, number every click/menu/prompt action and
capture the before/after identity fields. Expected observations are bounded:
success with the documented state transition, an explicit refusal/error, an
observable partial transition, or no observable contract (`UNKNOWN`). A
timeout or missing field is never converted to `SUPPORTED`.

## Task matrix

| Task | Controlled unknowns | Evidence owner | Parallel safety |
|---|---|---|---|
| [#72](https://github.com/mochan-tk/ttt1-codex/issues/72) | Thread topology, descendant spawn, depth, lineage, input, steer, interrupt, resume, close, parent termination | Future evidence slug: thread-topology | Serial; one runtime family at a time |
| [#73](https://github.com/mochan-tk/ttt1-codex/issues/73) | Ordinary subagent CWD/index sharing, disjoint/same-file writes, native overlap behavior | Future evidence slug: subagent-workspace-isolation | Serial controller; concurrency is the subject |
| [#74](https://github.com/mochan-tk/ttt1-codex/issues/74) | Managed/permanent worktrees, detached HEAD, branch attachment, Local/Worktree handoff | Future evidence slug: managed-worktree-handoff | Serial because branch ownership is exclusive |
| [#75](https://github.com/mochan-tk/ttt1-codex/issues/75) | Permission precedence, approval denial, command failure, timeout, interrupt, process death | Future evidence slug: permission-and-failure-propagation | Serial by permission/failure scenario |
| [#76](https://github.com/mochan-tk/ttt1-codex/issues/76) | Fresh-session recovery, durable lease, release, replacement, stale-writer exclusion | Future evidence slug: recovery-and-replacement | Exclusive fixture control |
| [#77](https://github.com/mochan-tk/ttt1-codex/issues/77) | App/CLI/IDE/cloud identity, handoff/resume, cloud branch/PR/check separation, plugin/instruction surface differences | Future evidence slug: cross-surface-continuity | One sentinel moves serially |
| [#78](https://github.com/mochan-tk/ttt1-codex/issues/78) | Concurrency cap, queue/refusal, time/usage budget, heartbeat/status, stop latency and cleanup | Future evidence slug: limits-and-observability | Only active load experiment |

## Experiment catalogue

### E1 — logical roles versus native topology

Task: #72. Start Project-, Epic-, Task-, and worker-equivalent disposable
threads, using App Server only where its experimental status is recorded.
Create the minimum child relation, then record thread ID, session ID, source
kind, parent/ancestor filters, persistence after idle, and UI visibility.
Archive leaf-first. Decide whether roles use a nested family or GitHub-linked
sibling sessions; GitHub remains authoritative either way.

### E2 — child starts child

Task: #72. Ask a root to create child A and A to create read-only grandchild B.
Confirm B through independent list/read/UI evidence. Allow at most one retry
after a deterministic rejection. Stop at depth two, close leaf-first, and
decide whether the kit permits bounded nested read-only research.

### E3 — depth and concurrency refusal

Tasks: #72 and #78. In separate fixtures, compare selectable V1 and V2 behavior,
set declared limits, and spawn one child at a time to a hard maximum of four
levels or the first refusal. Separately increase siblings one at a time to a
predeclared conservative cap. Record effective config, first queue/refusal,
resource fields, and cleanup. Never infer unlimited depth.

### E4 — lineage metadata durability

Task: #72. For root, child, grandchild, and fork, collect parent, ancestor,
forked-from, session, source kind, task path, and depth before/after restart and
resume. Mark fields requiring experimental APIs. Decide whether any field may
be advisory correlation; none may become the sole lease.

### E5 — direct human input to a busy child

Tasks: #72 and #77. Start one bounded 20–30 second read-only child. While active,
try the documented app, CLI, IDE, and hosted-web controls with a unique marker.
Record accepted/rejected state, ordering, same/new turn, parent notification,
and web limitations. Stop after two minutes. Decide direct-child versus
parent-mediated communication.

### E6 — steering

Task: #72. Start a multi-step read-only turn and steer it using the exact
expected turn ID and documented UI equivalents. Record continuation versus new
turn and mismatch errors. Decide the steering adapter and fallback to
interrupt/new turn.

### E7 — interruption and process reconciliation

Tasks: #72 and #75. Run a bounded disposable process with a uniquely captured
PID, then interrupt separately through App Server, app, and CLI. Record thread
state, exact process exit, partial output, files, and parent signal. If the PID
survives, stop and terminate only that resolved PID. Decide whether interrupt
requires explicit process reconciliation.

### E8 — resume after client loss

Tasks: #72, #76, and #77. Stop the client/app without deleting rollout state,
then resume by supported API/CLI/UI. Record history, CWD, permissions, role,
instruction sources, lineage, worktree, branch, and Git status. Include one
archived-but-not-deleted fixture if supported. Decide native resume versus
mandatory GitHub/Git reconstruction.

### E9 — close order and idempotence

Tasks: #72 and #78. First archive a depth-two family leaf-first and re-list
after every action. In a fresh family archive the parent first, capturing
descendant attempts and partial failures. Repeat one safe stop/close once.
Never permanently delete before evidence. Decide reconciliation rules.

### E10 — parent termination

Tasks: #72, #75, and #76. In separate fixtures interrupt the parent turn,
archive the parent thread, and terminate only an isolated App Server process
while a child runs a bounded read-only process. Observe child thread/PID,
result delivery, orphan visibility, and restart recovery. Decide orphan fencing
and whether parent loss can ever release ownership automatically.

### E11 — managed-worktree path isolation

Task: #74. Create two desktop managed-worktree chats from one clean disposable
base. Capture CWD, Git/common directory, registry, HEAD, branch, and filesystem
identity, then add distinct sentinels. Prove sentinels do not cross working
copies. Clean only after no process owns either worktree. Decide one managed
worktree per writer.

### E12 — branch isolation and handoff

Task: #74. Attach a unique branch and sentinel commit in each managed worktree.
Attempt to check out branch A in worktree B and accept the refusal; never force.
Record detached-to-attached transition, upstream, Local/Worktree handoff, and
final registry. Decide branch lease and recovery from already-checked-out state.

### E13 — ordinary subagent shared checkout

Task: #73. Have two ordinary children independently report CWD, Git directory,
HEAD, status, and worktrees. Under explicit fixture-only authority make disjoint
sentinel edits, inspect the single index, then run one trivial same-file
collision in a fresh file. Stop after the first deterministic collision.
Decide that ordinary subagents remain read-only unless observed isolation
contradicts the pinned source.

### E14 — effective permissions

Task: #75. Matrix parent read-only/workspace-write against omitted,
read-only, and workspace-write custom-role defaults on available local surfaces.
Probe read, fixture write, pre-created sibling-boundary write, harmless network,
and one denied approval. Never test unrestricted access outside a disposable
VM. Record effective policy and parent-visible denial. Decide enforceable
restriction versus advisory default.

### E15 — failure propagation and partial writes

Task: #75. In separate clean cases run deterministic exit 7, bounded timeout,
explicit interrupt, and termination of one exact child PID. Write one sentinel
before failure. Record child terminal state, parent message, sibling state,
retained output, Git diff, and cleanup. Decide retry/escalation and partial-write
inspection.

### E16 — crash-only reconstruction

Task: #76. Create a disposable Issue/branch/PR/check ledger and isolated runtime
home. Stop a worker before write, after uncommitted write, after commit, and
after simulated push. Start fresh without transcript access and reconstruct
only from ledger, branch/worktree, commit, PR, and checks. Decide the minimum
record-before-report schema.

### E17 — release and replacement

Task: #76. Worker A receives a unique durable-record marker, writes/commits,
then stops. Before release, ask replacement B to preflight and observe whether
the current runtime supplies any refusal; do not implement a lease wall in this
spike. After an explicit manual release or human adjudication record, B
rehydrates in a new worktree under one controller. Return A in the disposable
fixture and observe whether any native control rejects its stale marker. A
missing refusal is valid GAP evidence. Define the provider-neutral protocol;
proof of enforced exclusion belongs to Phase #62 after implementation.

### E18 — bounded concurrent isolated workers

Tasks: #73 and #78. Start two actual isolated-worktree workers behind a barrier,
owning a/** and b/**. Perform one edit/test concurrently. Audit paths, commits,
branches, elapsed time, statuses, resource fields, and diffs. Stop at the
predeclared cap. Decide safe parallelism and evidence.

### E19 — overlap rejection and hook limits

Tasks: #73 and #76. Give two prospective workers shared/** and observe whether
the current runtime supplies any native preflight refusal before edit. Do not
implement the future lease/overlap wall in this spike; record absence as a GAP.
If a hook is tested, record both covered-tool blocking and uncovered paths and
never call it complete enforcement. Define the GitHub lease/preflight/hook
layering; deterministic rejection proof belongs to Phases #62/#63.

### E20 — cloud result versus GitHub checks

Task: #77. In a disposable connected repository, run a bounded cloud Task that
opens or updates a PR while a deterministic CI check fails. Capture cloud task
state, diff/result, branch, commit, PR head, and checks independently. With
separate authority fix the fixture check and show one state can change without
rewriting the others. Decide separate state machines.

### E21 — surface and handoff matrix

Tasks: #77 and #74. Run the same trivial sentinel objective through available
app Local, app Worktree, App Server, CLI interactive, CLI exec, IDE, and cloud.
Record IDs, CWD, instruction sources, sandbox, worktree, branch, diff, resume,
controls, and result transport. Exercise documented CLI /app, Local/Worktree,
remote-host handoffs, and IDE-to-Cloud delegation. For IDE-to-Cloud, verify the
new cloud-chat identity, transferred context/local source changes, Git base,
branch, diff, and return path without assuming same-thread continuity. Decide
an explicit routing table. In an isolated runtime home, install a harmless
disposable plugin through every supported surface, start the required new
session, verify instruction/Skill discovery, then perform one version update
and exact rollback/removal. Record IDE or other unsupported surfaces as
UNSUPPORTED/NOT TESTED rather than bypassing them; do not touch marketplace or
production plugin state.

## Evidence report schema

Each evidence file must contain:

- Task, Plan, version, fixture, and UTC identity;
- hypothesis and controlled architecture decision;
- initial repository/process/thread/worktree snapshot;
- exact setup and commands/UI actions;
- raw observations and timestamps;
- expected versus observed result for every numbered action;
- evidence provenance: DOCUMENTED, SOURCE-SUPPORTED, OBSERVED, INFERENCE,
  NOT TESTED, or UNKNOWN;
- observed result: SUPPORTED, PARTIAL, UNSUPPORTED, or UNKNOWN;
- unexpected writes, permission prompts, failures, retries, and deviations;
- final Git/runtime snapshot and cleanup proof;
- decision: accept, reject, constrain, or retain UNKNOWN;
- downstream Issues affected, with no implementation change in the spike.

## Readiness gate

A spike may receive ai:ready only after:

1. the Planning PR is human-merged and #58 is closed;
2. its disposable fixture and credentials are named and reviewed;
3. its surface/version is still current;
4. no owned path overlaps another ready Task;
5. review capacity exists;
6. the Epic #60 conductor selects it as the next bounded wave.

Successful documentation lookup, source inspection, or this plan is not runtime
evidence and does not satisfy that gate.
