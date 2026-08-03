---
name: task-routing
description: Routes a GitHub Task to the appropriate Codex app, CLI, IDE, or cloud surface and records an advisory role and reasoning tier without pinning a model. Use while drafting a Task, assigning its single exec label, changing environments after new evidence, or deciding whether ambiguity, local dependencies, sensitivity, parallelism, or risk permit unattended execution.
---

# Task Routing

Record routing in the requester-owned Task body and mirror the surface with
exactly one `exec:*` label. Keep concrete model selection in user or
organization policy; do not pin a model in the reusable repository.

## Evaluate the Task

Assess these inputs before choosing a surface:

1. Ambiguity and expected mid-task judgment.
2. Dependence on local files, credentials, hardware, or a signed-in UI.
3. Value and safety of parallel execution.
4. Data sensitivity and governed-source restrictions.
5. Reasoning depth and review risk.
6. Whether every acceptance criterion can run on the chosen surface.

## Choose one surface

| Label | Codex surface | Choose when |
|---|---|---|
| `exec:cloud` | Codex cloud task | The brief is self-contained, asynchronous work is useful, and no local-only dependency or controlled data is required. |
| `exec:app` | Codex desktop app task | The work benefits from steering, local worktrees, subagent coordination, connectors, or occasional human judgment. |
| `exec:cli` | Codex CLI | The work is terminal-first, repeatable, scriptable, or part of batch/automation while still retaining an Issue and dedicated session. |
| `exec:ide` | Codex IDE extension | The work needs an active editor, exploratory human interaction, a local toolchain, hardware, or machine-bound debugging. |

Never route physical-device verification or non-exportable data to cloud.
Reference controlled data at its source. If acceptance criteria are not
objective enough for unattended work, sharpen the brief or choose an
interactive surface.

## Suggest a role and reasoning tier

Select an existing project custom agent from `.codex/agents/` when its role
matches; otherwise use the default agent. Do not invent a role that the target
surface cannot provide.

Use advisory tiers rather than model names:

- `high-reasoning` for architecture, planning, review, or difficult diagnosis.
- `standard` for ordinary implementation from a complete brief.
- `fast` for bounded mechanical transformations.
- `local` when data or environment policy requires on-device execution.

Record whether ownership and dependencies make the Task parallel-safe. A high
parallelism value never overrides overlapping paths or an unresolved blocker.

## Apply risk and rerouting

Add `risk:high` when repository policy identifies a high-risk Task. Surface
selection does not bypass its exact plan-approval gate.

Treat rerouting as a material plan change. Update the `exec:*` label and Routing
fields through requester/planner authority, add the required work-order change
comment, and require the executor to add a revised plan comment before moving.
