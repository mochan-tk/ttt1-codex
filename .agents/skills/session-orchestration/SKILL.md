---
name: session-orchestration
description: Runs, coordinates, and crash-resumes one GitHub Task per Codex session, worktree, branch, and PR while keeping start, plan, ownership, evidence, and outcome authoritative on the Issue timeline. Use when starting or delegating a Task, applying lazy consensus or the exact risk gate, detecting an orphan, transferring ownership, escalating repeated failures, or recovering after an interrupted session.
---

# Session Orchestration

Use `1 Task = 1 session = 1 worktree = 1 branch = 1 PR`. Keep concurrent File
ownership disjoint. Treat session messages and any local `plan.md` as
non-authoritative caches; do not require or commit a resume store.

## Run the start ritual

Before implementation or file changes, perform these steps in order:

1. Read applicable `AGENTS.md`, the complete requester-owned Issue body, every
   linked agreement or artifact, and the latest comments.
2. Inspect Issue state, labels, parent, blockers, routing, and path ownership.
3. Inspect Git status, branch, worktree, remotes, linked PR, commits, and checks.
4. Add a start comment that claims ownership and states the derived current
   state, session/worktree, branch, and expected paths.
5. Add a new authoritative plan comment containing the goal, approach, owned
   files, verification commands, and expected results. Never edit this comment.

If the work order is incomplete, contradictory, blocked, or already owned,
stop and record the condition instead of guessing or creating a competing
writer.

## Apply plan authority and consensus

Use lazy consensus for a normal Task: proceed after the plan comment is durable.
When approach, scope, ownership, or tests change materially, add a revised plan
comment; never rewrite the previous one.

For a Task labeled exactly `risk:high`, stop after the plan comment. Proceed
only after a human with repository merge authority posts this approval for that
exact comment:

```text
Approved plan: <plan-comment-url> — <scope/conditions>
```

Reject an approval that points to another plan, lacks the required scope or
conditions, or was written by an agent. A revised `risk:high` plan requires a
new exact approval; an unchanged plan retains its approval.

## Execute and report durably

Stay within ownership, run the Task's pre-positioned checks, and commit only
Task-scoped changes. Before sending any session report, add the measured
outcome to the Task Issue:

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

Only then send a short pointer to a parent or human. An unrecorded report is not
state and must be returned to the executor for landing.

## Resume crash-only

Do not use resume to rotate a healthy owner or split one Task across sessions.
After a crash or lost session, rerun start inspection and derive state from the
Issue timeline, branch, worktree, commits, PR, and checks.

Detect an orphan when a durable start exists, no outcome exists, and no live
owner session can be identified. Before new implementation, add a resume
comment naming:

- the prior owner and why it appears inactive;
- the derived Issue, Git, worktree, PR, and check state;
- uncommitted, local-only, or remote artifacts found;
- the authoritative plan comment and next action.

That resume comment transfers ownership. Never allow two live owners. Escalate
after the same resume failure occurs twice.

## Enforce the three-attempt escalation

Count the same failure only when both the command or check and observed
root-cause signature match. Allow three attempts at the executor level, then
record the evidence and escalate to the parent/orchestrator. Allow three at the
parent level, then add durable `needs:human` state and stop for a human.

Reset a counter only after a materially different intervention based on new
evidence, such as changed code, configuration, inputs, ownership, or approach.
A retry, restart, or new session alone does not reset it.

## Parent responsibilities

Dispatch only mechanically calculated frontier Tasks within human review
capacity. Pass the Issue number as the brief, verify each outcome and Evidence
independently, and route `needs:replan` through `$plan-management`. Create an
Issue and dedicated session even for small infrastructure, Settings, secret,
deployment, or smoke-test actions.
