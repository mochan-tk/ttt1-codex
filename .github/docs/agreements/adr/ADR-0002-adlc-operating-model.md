# ADR-0002: ADLC operating model and durable control points

- Status: accepted by the agreement merge
- Date: 2026-08-03
- Owners: repository owner and agreement reviewers
- Supersedes: source plan-location ambiguity and the former term "click"

## Context

Agent sessions are replaceable and may run in parallel. Conversation, internal
plans, and parent-child messages are useful transport but unreliable storage.
The lifecycle must preserve enough state to restart work, diagnose divergence,
and make human judgment visible without turning every agent step into a manual
approval gate.

The approved source ADR-0006 makes the Task Issue comment the sole authoritative
plan location, assigns the work-order body to the requester, and defines the
Three Merges. The v1.0.0 handoff adds the tracking graph, risk exception, resume
protocol, ledger completeness, PII reference rule, legacy path, and retro
candidate.

## Decision

### 1. Durable memory and work unit

- Apply `record-before-report`, `verify-before-done`, and `single-writer` in
  every phase.
- Use `1 Task = 1 session = 1 worktree = 1 branch = 1 PR`.
- The requester owns the Task Issue body. The executor never edits it.
- If the requester changes the body, immediately add a comment stating what
  changed, why, and whether the executor must replan.
- At Task start, perform the start ritual in this order:
  1. read applicable `AGENTS.md`, the Issue body and links, and the latest
     comments;
  2. inspect Issue state, labels, parent, blockers, and path ownership;
  3. inspect Git status, branch, worktree, remotes, linked PR, and checks;
  4. add a start comment that claims ownership and states the derived current
     state; and
  5. add the authoritative plan comment before implementation or file changes.
- At resume, repeat the inspection in steps 1-3, then add a resume comment that
  claims ownership, states the derived state, and links the latest authoritative
  plan. Add a revised-plan comment only when the plan materially changes. An
  unchanged `risk:high` plan keeps its existing approval; a revised one requires
  approval of the new plan comment.

### 2. Plan authority and intervention

- Add the working plan to the Task Issue before implementation or file changes.
- Treat an internal plan, `plan.md`, and PR-description plan as caches. Keep
  session plan files untracked and non-authoritative. The PR links to the
  authoritative Issue comment.
- Do not edit plan comments. Add a revised-plan comment when the approach,
  ownership, tests, or scope materially changes.
- Use lazy consensus by default. A normal Task proceeds after recording its
  plan without waiting for human approval.
- A `risk:high` Task stops after the plan comment. Before implementation, a
  human with repository merge authority must add `Approved plan:
  <plan-comment-url> — <scope/conditions>`. Approval of another plan or an
  agent-authored approval does not open the gate.
- Intervene at the cause: revised plan for execution sequencing, requester body
  change plus change comment for a bad work order, or a derived agreement Issue
  and agreement PR for a bad premise.

### 3. Planning and tracking graph

- Keep distant work coarse in an Epic. Detail only the next rolling wave.
- Treat the Issue graph as planning truth and Projects as a view.
- Calculate frontier as `open AND type:task AND ai:ready AND all blockers
  closed`.
- A human limits dispatch count to available review capacity.
- Preserve four edges: sub-issue parent, blocked-by dependency, origin `#N`
  reference, and PR `Closes #N`.
- Every derived Issue states its discovery source as `#N` in one line.

### 4. Test-first execution and verification

- Express acceptance criteria as executable tests or observable checks before
  implementation. Verification provides the exact command and expected result.
- The agent implements toward those pre-positioned measures and records fresh
  results in an Evidence table.
- Before reporting completion in a session, the executor adds the measured
  outcome and Evidence to the Task Issue. The PR remains the change artifact.
- Deterministic policy and required checks form the hard wall. Runtime tests,
  Codex review, and human design judgment layer on top.
- An agent's self-report is never Evidence. Do not delete, skip, or weaken a
  measure to obtain green status.
- Diagnose mismatch at four addresses: work-order body, plan comment, PR diff,
  and Evidence/checks.
- Escalate repeated same failures from executor to parent/orchestrator to human;
  the initial budget is three attempts at each level. An attempt belongs to the
  same failure when both the command or check and the observed root-cause
  signature match. The counter resets only after a materially different
  intervention based on new evidence, such as changing code, configuration,
  inputs, ownership, or approach; a plain retry or restart does not reset it.
  Stop with a durable `needs:human` Issue state rather than an ephemeral plea.

### 5. Resume and ownership transfer

- Do not create a separate resume store. Run the resume variant of the start
  ritual and derive current state from the Issue timeline, branch, worktree,
  commits, PR, and checks.
- A parent/orchestrator detects an orphaned Task: durable start exists, no
  outcome exists, and no live owner session can be identified.
- A successor adds a resume comment naming the prior owner state, derived
  current state, uncommitted or remote artifacts found, and the next action.
- The resume comment transfers ownership before new implementation begins.
- Escalate after the same resume failure occurs twice; do not create competing
  owners.

### 6. Ledger completeness and sensitive data

- Every change, however small, including infrastructure, deploy, secret,
  smoke-test, and repository Settings actions, begins with a Task Issue and
  runs through a dedicated agent session.
- For a non-delegable UI or trust decision, the agent prepares the exact action;
  the human performs only that action, and the observed result is recorded on
  the Task Issue before any session report.
- Humans keep hands off the implementation path and exercise judgment through
  the work order, exceptions, review, and the Three Merges.
- Reference PII, credentials, and controlled data at their access-controlled
  source. Do not paste them into Issues, PRs, logs, or agent instructions.

### 7. Learning loops and legacy entry

- Treat a first occurrence of project or agent-system friction as information.
  Record it as a `retro:candidate`; promote the same class on its second
  occurrence into a guidance, skill, template, test, or gate PR.
- Ask once on applicable changes whether the learning belongs upstream. The
  template owner alone accepts or rejects an upstream PR.
- For an existing codebase without behavioral tests, make the first delegated
  work orders characterization-test Tasks rather than feature changes.
- Keep issue-body edit-diff automation as the seeded retro candidate until a
  second occurrence justifies implementation.

### 8. Human merge events

- **Agreement merge:** accepts distilled truth and changes what agents design
  against.
- **License merge:** accepts measured setup evidence after one end-to-end trial
  proves the delegation path.
- **Completion merge:** accepts a Task PR after required checks, Evidence, and
  non-author human review.

Repository automation may prepare these events but does not substitute for the
human merge decision.

## Consequences

- A Task's Issue timeline is the single intent and recovery trail: work order,
  start, plan, changes, resume if needed, and outcome.
- Human attention moves from every plan to exceptions and merge decisions.
- Tests bound autonomy: a thin wall permits only narrow delegation; adding
  executable measures expands the licensed area.
- Silent human work, overwritten comments, unlinked Issues, and pasted secrets
  are treated as integrity defects.

## Validation

Run one trial Task that intentionally exercises plan landing, a red-to-green
check, PR Evidence, `Closes #N`, and a fresh-session state derivation. Separately
simulate a `risk:high` stop, a derived Issue origin link, and a controlled
failure escalation without merging throwaway artifacts.

## References

- [Pinned ADLC chapter](https://github.com/mochan-tk/k-wk4-codex/blob/a7eb2629424282f9b8262e0248bed7f1879058db/manuscript/02_agentic_development.md)
- [Pinned source ADR-0006](https://github.com/mochan-tk/k-wk4-codex/blob/a7eb2629424282f9b8262e0248bed7f1879058db/docs/decisions/ADR-0006_%E8%A8%88%E7%94%BB%E3%81%AE%E7%9D%80%E5%9C%B0%E5%85%88%E3%81%A8%E5%AE%8C%E4%BA%86%E8%A8%AD%E8%A8%88%E3%81%AE%E6%94%B9%E8%A8%82.md)
- [Source plan-comment landing PR #39](https://github.com/mochan-tk/tt1/pull/39)
- [Epic #1](https://github.com/mochan-tk/ttt1-codex/issues/1)
