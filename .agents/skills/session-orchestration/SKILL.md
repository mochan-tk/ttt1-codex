---
name: session-orchestration
description: Runs, delegates, coordinates, and crash-resumes GitHub Tasks and sibling Epic phases through Codex subagents while keeping ownership, plans, evidence, and outcomes authoritative on GitHub. Use when starting or delegating a Task, conducting a program or Epic, steering or stopping subagents, diagnosing cloud-task versus PR-CI state, transferring orphaned work, or escalating repeated failures.
---

# Session Orchestration

Use `1 Task = 1 session = 1 worktree = 1 branch = 1 PR`. That Task session is
the sole implementing writer. Codex subagents may support it only with bounded,
independent, parallel **read-only** exploration, review, or test observation;
they receive no File ownership and make no edits. Keep concurrent Task path
sets disjoint. Session messages, subagent threads, and local plans are caches;
GitHub is the durable ledger.

## Detect the available control plane

Before claiming the full ritual, check for root `AGENTS.md`, the Task and Epic
Issue templates, agreements, and the repository validators named by that
guidance. If any are absent, name the missing controls and treat this as a
plugin-only or partial installation:

1. Follow the repository's existing conventions and the user's explicit Task.
2. Use the delegation, verification, and one-hop reporting practices below,
   but do not claim that this kit enforces Issue, PR, review, or check gates.
3. Limit output to read-only assessment or draft text while any full-kit
   control is missing. Separate authority alone does not make a partial
   installation safe for live GitHub or repository writes. Never fabricate a
   missing helper, label, agreement, worktree, or check. Offer the full-kit
   installation when the durable control plane is required. Any live write
   requires every missing control to be restored and verified first, then
   separate explicit authority.

## Map the Codex layers

| Plan scope | Codex session or thread | Responsibility |
|---|---|---|
| Whole project / Epic set | Program session | Starts and coordinates sibling Epic-parent sessions; never decomposes or dispatches Tasks. |
| One Epic phase | Epic-parent session | Decomposes just in time, computes the Task frontier, dispatches sole-writer Task sessions, steers, and verifies. |
| One Task | Sole-writer Task session | Owns the ritual, implementation, worktree, branch, PR, Evidence, and optional read-only subagents. |
| Bounded Task support | Read-only subagent thread | Explores, reviews, or observes tests without File ownership or edits and reports one hop to the Task session. |

Neither program nor Epic-parent sessions implement Task-owned changes. An
Epic-parent session may create and dispatch Tasks through `$plan-management`;
the program session may start Epic parents but must not reach through them to
dispatch a Task.

## Run the Task start ritual

Before implementation or file changes:

1. Read applicable `AGENTS.md`, the complete requester-owned Issue body, every
   linked agreement or artifact, and the latest comments.
2. Inspect Issue state, labels, parent, blockers, routing, and path ownership.
3. Inspect Git status, branch, worktree, remotes, linked PR, commits, and checks.
4. Add a Start comment claiming ownership and recording the derived state,
   session/worktree, branch, expected paths, and any protected worktrees.
5. Add a new authoritative Plan comment with the goal, approach, owned files,
   verification commands, and expected results. Never edit a Plan comment.

If the work order is incomplete, contradictory, blocked, or already owned,
stop and record the condition instead of guessing or creating another writer.

## Apply plan authority and consensus

Use lazy consensus for a normal Task: proceed after the Plan is durable. Add a
Revised Plan comment when approach, scope, ownership, or tests materially
change; never rewrite history.

For a Task labeled exactly `risk:high`, stop after the Plan. Proceed only after
a human with repository merge authority posts this approval for that exact
comment:

```text
Approved plan: <plan-comment-url> — <scope/conditions>
```

Reject an approval for another Plan, an agent-authored approval, or one without
the required scope. A revised high-risk Plan requires fresh exact approval.

## Delegate bounded read-only Codex subagents

Delegate only work that is genuinely independent and read-only: codebase
exploration, focused review, or observation of existing test commands, logs,
and results. Subagents receive no File ownership. They do not edit files, run
commands that write workspace artifacts, commit, push, open PRs, or implement
any part of the Task. The Task session remains the sole writer and applies any
change itself after evaluating the reports.

Each subagent kickoff is complete and bounded:

```markdown
You are a read-only Codex subagent supporting the sole-writer session for Task
#<n> in <owner>/<repo>.
- Issue: <URL>; read the body and latest comments.
- Authoritative Plan: <exact Plan comment URL>.
- Read scope: <exact files, logs, or evidence to inspect>. You have no File
  ownership; make no edits and create no generated workspace artifacts.
- Assignment: <one independent read-only outcome and explicit non-goals>.
- Observation: <existing test/log/check evidence to inspect; no mutating run>.
- Report one hop to the Task session: findings, inspected evidence, commands
  that were observed, uncertainty, and blockers.
- Do not post Task ritual comments, expand scope, merge, or report past the
  Task session. Do not commit, push, open a PR, or implement. Stop after the
  report.
```

Wait for every requested subagent whose result is required. Steer a running
subagent with a short correction when evidence shows drift. Stop or cancel it
when it attempts to write, the premise is invalid, or continuing would be
unsafe; record any material effect on the Task. Codex supports inspecting,
steering, stopping, and closing subagent threads; see the
[official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Verify reports against ground truth

Reports climb one hop at a time: read-only subagent to Task session, Task
session to Epic parent, Epic parent to program. A subagent report is a claim.
Before accepting it, the receiving Task session independently rechecks the
Issue and Plan, branch and worktree, commit and PR head, diff against the base,
File ownership, exact test outputs, PR checks, and recorded deviations. Return
an unverifiable claim to its sender instead of forwarding it.

For a Codex cloud Task, inspect three states separately:

1. the cloud Task's own output and completion state;
2. the resulting branch, commits, and PR head/diff; and
3. the PR workflow runs and checks.

A successful cloud Task does not prove CI passed. Conversely, a workflow in
`action_required`, or a PR with no reported checks because gated workflows
have not started, does not prove the Codex Task failed. It can be an
organization Actions approval boundary. Record both states, keep completion
blocked until required checks actually run, and route approval to an authorized
human; do not bypass policy or hunt for a repository switch this kit controls.

## Task session records outcome before reporting upward

The read-only subagent reports one hop to the Task session and does not post
Task ritual comments. The Task session then independently verifies the report,
stays within ownership, performs all implementation itself, runs every
pre-positioned measure, and commits only Task-scoped changes. Before the Task
session reports completion to the Epic parent, the Task session posts:

```markdown
## Outcome: <completed | blocked | failed | needs-replan>

- PR: #<number>
- Plan: <authoritative-plan-comment-url>

| Criterion | Evidence (command, check, diff, or link) | Result |
|---|---|---|
| <criterion> | `<command>` -> <observed result> | pass/fail/deferred |

- Deviations: <none or recorded difference>
- Follow-ups: <derived Issues or none>
- Scaffold friction: <retro:candidate link or none>
```

Any `deferred` criterion prohibits `Outcome: completed`. A follow-up alone does
not remove that block. The requester must revise the original work order to
remove or re-home the criterion and record the body change. The executor may
propose that change but never edit the requester-owned Task body.

## Conduct the program session

Start one program session when the phase Epics exist and keep it as the
conductor of conductors for that plan. It derives state from the GitHub graph,
not its transcript.

1. Start an Epic-parent session when that sibling Epic's `blocked-by` Epics
   close. If the actionable Task frontier dries up, start or wake the
   responsible Epic parent only when its predecessors are closed. If no Epic
   is actionable, record and replan the cross-phase blockage; never skip a
   dependency merely to create work.
2. Epic-parent sessions are siblings. An Epic parent reports the next phase
   upward; it never spawns its successor, which would create recursive nesting.
3. Watch cross-phase risks such as reversed dependencies, blockers that never
   clear, or repeated escalations. Leave within-Epic decisions to its parent.
4. Use `$plan-management` for cross-phase reordering, splitting, or removal and
   record the rationale on affected Epics.
5. On program crash/resume, reconstruct each Epic from its body, dependency
   edges, comments, Tasks, PRs, and checks. Never reconstruct from chat.

The program session never decomposes Tasks, dispatches Task sessions, edits code,
or performs an Epic parent's verification loop.

## Conduct one Epic parent

1. Keep the current phase decomposed just in time with `$plan-management`.
   Dispatch only mechanically calculated frontier Tasks within human review
   capacity and only after rechecking disjoint File ownership.
2. Pass a Task session the Issue number; the requester-owned body is its brief.
   Task-session-to-subagent delegation uses the complete read-only kickoff
   above.
3. Monitor Task sessions and PRs. Steer early, independently verify outcome and
   Evidence, and route `needs:replan` through `$plan-management`.
4. Treat infrastructure, Settings, secret, deployment, and smoke-test work as
   dedicated Tasks; never execute an inline shortcut.
5. Report phase completion upward only after its Tasks are closed, their PRs
   are merged, and the Epic's current decomposition-state line is accurate.
   Name the next sibling Epic, but do not start it. If no program session is
   live, put that next-Epic pointer in the durable Epic closing comment.

## Close subagents leaf first

Keep a read-only subagent available while its findings may need clarification.
After its result is consumed, close completed threads in this leaf-first order:
subagent descendants, read-only subagents, Task sessions, Epic parents, then
the program. Closing a parent first must never strand an active child or
discard an unrecorded report.

## Resume crash-only

Do not use resume to rotate a healthy owner. After a crash, rerun the start
inspection and derive state from the Issue timeline, branch, worktree, commits,
PR, checks, and any uncommitted artifacts. An orphan has a durable Start, no
Outcome, and no identifiable live owner. Before implementation, add a Resume
comment naming the prior owner, derived state, found artifacts, authoritative
Plan, and next action. That comment transfers ownership. Never allow two live
owners; escalate after the same resume failure occurs twice.

## Enforce the three-attempt escalation

Count the same failure only when both the command/check and root-cause
signature match. Allow three executor attempts, record Evidence, and escalate
to the parent. Allow three parent attempts, then add durable `needs:human` and
stop. Reset only after a materially different evidence-based intervention;
retry, restart, or a new session alone does not reset the count.
