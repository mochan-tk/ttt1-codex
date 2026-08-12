---
name: plan-management
description: Builds and maintains the executable GitHub Issue graph of Epics, Task sub-issues, dependencies, origin links, and the actionable frontier. Use when creating or splitting work, wiring blockers, planning a rolling wave, deciding what can run next or in parallel, or propagating a recorded deviation through downstream Tasks.
---

# Plan Management

Treat the Issue graph as planning truth and Projects as a derived view. Treat
session plans, chat handoffs, and local `plan.md` files as replaceable caches.

## Detect the distribution boundary

Check for root `AGENTS.md`, the Epic and Task Issue templates, the configured
labels, and the agreements or validators named by repository guidance. In a
plugin-only or partial installation, list the missing controls and restrict
work to read-only graph analysis, locally previewed bodies, or draft text. Do
not claim that the full ADLC graph is installed or enforced. Any live write
requires every missing control to be restored and verified first, then
separate explicit authority.

The plugin bundles `new-task.sh` and `frontier.sh`, but their presence is not
authority to mutate GitHub. Before `new-task.sh --apply`, separately confirm
the GitHub.com repository and authenticated account, a readable `type:epic`
parent, every origin and blocker, all required labels, compatible `gh`
features, and explicit authority for live Issue creation. If any prerequisite
is absent, keep `--dry-run` output as the handoff; never fabricate a control.

## Model the graph

Preserve all four tracking edges:

1. Add every Task as a sub-issue of one Epic.
2. Represent ordering with GitHub blocked-by dependencies, not prose alone.
3. Add one `Origin: #N` reference to every derived Issue.
4. Require the completion PR body to contain `Closes #N` for its Task.

Use `type:epic` for Epics and `type:task` for Tasks. Add exactly one `exec:*`
label to each Task. Classify every Task body as `Risk: normal` or `Risk: high`;
add `risk:high` only for the latter. Add `ai:ready` only when its
requester-owned body is self-contained, traceable, bounded, test-first,
path-partitioned, and routed.

Model a multi-phase plan as two Issue levels:

- one coarse Epic per phase, all phase Epics siblings;
- Task sub-issues under exactly one Epic.

Never make an Epic a sub-issue of another Epic. Encode phase order with
`blocked-by` edges between sibling Epics, not hierarchy or prose. A program
session coordinates the sibling set; each Epic-parent session owns only its
phase and reports the next phase upward instead of spawning a nested successor.

## Plan as a rolling wave

1. Create the complete phase outline as coarse sibling Epics so the durable
   graph names what comes next; wire their order with `blocked-by`.
2. Decompose only the next phase when its blockers close. Within that Epic,
   detail only the next executable Task wave or replenish it when the frontier
   is nearly empty. Distant Task detail decays and must not be pre-created.
3. Start bodies from [templates/epic-body.md](templates/epic-body.md) and
   [templates/task-body.md](templates/task-body.md).
4. Partition parallel Tasks by disjoint File ownership. Add a dependency when
   paths overlap or one Task consumes another's result.
5. Resolve `PLAN_MANAGEMENT_SKILL_DIR` to the absolute directory containing
   this `SKILL.md`. This works for both a repository skill and a plugin copy.
   Preview locally before any live GitHub action:

```bash
"$PLAN_MANAGEMENT_SKILL_DIR/scripts/new-task.sh" \
  --title "Task: <outcome>" --body task-body.md --parent 12 \
  --origin 12 --exec app --risk normal --blocked-by 10,11 --ready --dry-run
```

6. After reviewing the transformed body and intended edges, explicitly authorize
   the live GitHub action:

```bash
"$PLAN_MANAGEMENT_SKILL_DIR/scripts/new-task.sh" \
  --title "Task: <outcome>" --body task-body.md --parent 12 \
  --origin 12 --exec app --risk normal --blocked-by 10,11 --ready --apply
```

The helper refuses when neither mode is present or `--risk normal|high` is
missing. It replaces the canonical Origin and Risk placeholders and prints the
risk choice during preview. Only `--apply` may invoke `gh`; `--dry-run`
validates locally and makes no GitHub call. On apply, high risk also requires
and adds `risk:high`; normal risk never adds that label.

The applied helper adds the parent, dependency, origin, routing, and ready
records in one creation flow and prints the required completion link.

7. After every decomposition or replenishment wave, update the Epic body's
   `## Decomposition state` section. Keep exactly one current state line under
   that heading and replace the prior line rather than appending history:

```text
Phase <name> decomposed on YYYY-MM-DD into Tasks #<n>, #<n>; next trigger: <condition>.
```

Name the phase, date, current Task references, and next replenishment trigger.
Replace any onboarding draft marker when the first wave is approved. Comments
and body history preserve prior states; the visible line must describe now.

## Optionally materialize a roadmap

Projects are a convenience view, never planning authority. If the full kit's
`.github/scripts/setup-project.sh` exists and a human wants the view, preview
initialization before requesting consent:

```bash
.github/scripts/setup-project.sh init --dry-run
.github/scripts/setup-project.sh init --apply
```

Run the second command only after the exact GitHub.com repository, owner,
fields, and views have been reviewed and explicitly approved. If the helper is
absent in a skills-only plugin installation, report that the template or
installer is required; do not fabricate a substitute command.


## Calculate the frontier

Define the frontier as `open AND type:task AND ai:ready AND all blockers
closed`. Calculate it from GitHub rather than session memory:

```bash
"$PLAN_MANAGEMENT_SKILL_DIR/scripts/frontier.sh"
"$PLAN_MANAGEMENT_SKILL_DIR/scripts/frontier.sh" --all --repo owner/repo
```

Before dispatch, recheck disjoint ownership and limit the count to available
human review capacity.

An empty frontier is not permission to skip a phase dependency. If the active
Epic is incomplete, replenish or replan it. The program session may wake the
responsible Epic parent when the frontier dries up, but only an Epic parent
decomposes or dispatches its Tasks.

## Preserve plan-comment authority

Keep the requester-owned Task body as the work order. Before implementation,
the executor adds the authoritative working plan as a new Task comment. Never
edit a plan comment. If approach, ownership, scope, or verification changes,
add a revised-plan comment and apply the applicable risk gate.

Only the requester changes an existing Task body. A planner may propose exact
body changes in a new comment but must not edit the body unless that same human
is explicitly acting as the requester. Immediately after the requester edits
the body, add a timeline comment stating what changed, why, and whether an
active executor must replan.

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
7. Rewrite that Epic's single decomposition-state line so the visible body
   matches the repaired Task wave. For a cross-phase change, update every
   affected sibling Epic and its `blocked-by` edges; never nest one phase under
   another.
