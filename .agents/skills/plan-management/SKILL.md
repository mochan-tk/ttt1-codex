---
name: plan-management
description: Builds and maintains the executable GitHub Issue graph of Epics, Task sub-issues, dependencies, origin links, and the actionable frontier. Use when creating or splitting work, wiring blockers, planning a rolling wave, deciding what can run next or in parallel, or propagating a recorded deviation through downstream Tasks.
---

# Plan Management

Treat the Issue graph as planning truth and Projects as a derived view. Treat
session plans and local `plan.md` files as replaceable caches.

## Model the graph

Preserve all four tracking edges:

1. Add every Task as a sub-issue of one Epic.
2. Represent ordering with GitHub blocked-by dependencies, not prose alone.
3. Add one `Origin: #N` reference to every derived Issue.
4. Require the completion PR body to contain `Closes #N` for its Task.

Use `type:epic` for Epics and `type:task` for Tasks. Add exactly one `exec:*`
label to each Task. Add `ai:ready` only when its requester-owned body is
self-contained, traceable, bounded, test-first, path-partitioned, and routed.

## Plan as a rolling wave

1. Keep the whole Epic coarse enough to preserve direction.
2. Detail only the next executable wave or replenish it when the frontier is
   nearly empty.
3. Start bodies from [templates/epic-body.md](templates/epic-body.md) and
   [templates/task-body.md](templates/task-body.md).
4. Partition parallel Tasks by disjoint File ownership. Add a dependency when
   paths overlap or one Task consumes another's result.
5. Use the deterministic helper to create a fully wired Task:

```bash
.agents/skills/plan-management/scripts/new-task.sh \
  --title "Task: <outcome>" --body task-body.md --parent 12 \
  --origin 12 --exec app --blocked-by 10,11 --ready
```

The helper adds the parent, dependency, origin, routing, and ready records in
one creation flow and prints the required completion link.

## Calculate the frontier

Define the frontier as `open AND type:task AND ai:ready AND all blockers
closed`. Calculate it from GitHub rather than session memory:

```bash
.agents/skills/plan-management/scripts/frontier.sh
.agents/skills/plan-management/scripts/frontier.sh --all --repo owner/repo
```

Before dispatch, recheck disjoint ownership and limit the count to available
human review capacity.

## Preserve plan-comment authority

Keep the requester-owned Task body as the work order. Before implementation,
the executor adds the authoritative working plan as a new Task comment. Never
edit a plan comment. If approach, ownership, scope, or verification changes,
add a revised-plan comment and apply the applicable risk gate.

Only the requester or planner changes a Task body. Immediately add a timeline
comment stating what changed, why, and whether an active executor must replan.

## Replan from a durable trigger

1. Read the recorded outcome, deviation, check, or `needs:replan` state. Record
   a verbal trigger on the Issue before acting.
2. Walk the trigger's blocking edges, remaining Epic sub-issues, owned paths,
   and references.
3. Decide `keep`, `modify`, `split`, `add`, or `close-as-obsolete` for every
   affected Issue. Never delete history.
4. Apply one of the three intervention paths at the cause:
   - add a revised-plan comment for execution sequencing;
   - have the requester change a bad work-order body and add its change comment;
   - file an issue-first agreement repair and block implementation until its
     agreement PR merges.
5. Remove `ai:ready` from stale briefs. Restore it only after repair.
6. Add one Epic rationale comment listing changed Issues and why, then clear
   `needs:replan` only when the graph is coherent again.
