# Repository Constitution

This repository uses Codex to execute an Agentic Development Lifecycle on top
of GitHub. Apply `record-before-report`, `verify-before-done`, and
`single-writer` in every phase.

## Authority

- GitHub commits, Issues, comments, pull requests, reviews, and checks are the
  durable ledger. Chat, session state, internal plans, and Projects views are
  replaceable caches.
- `.github/docs/agreements/` is the reviewed project truth. Do not change an agreement
  as a side effect; open a derived Issue and land a dedicated agreement PR.
- Every change starts from a Task Issue, including quick fixes, infrastructure,
  smoke tests, secrets setup, deployments, and repository Settings actions.
- Use `1 Task = 1 session = 1 worktree = 1 branch = 1 PR`. Parallel Tasks must
  have disjoint path ownership and one active writer per owned path.

## Task Lifecycle

- Before editing, read the applicable instructions, requester-owned Task Issue
  body, links, and latest comments. Inspect labels, parent, blockers, ownership,
  branch, worktree, remotes, linked PR, and checks.
- Never edit the Task Issue body. If the requester changes it, add a comment
  describing the change, reason, and whether replanning is required.
- Post a Start comment that claims ownership and records derived state, then a
  new authoritative Plan comment before implementation. Never edit plan
  comments; post a Revised Plan comment for material changes.
- Normal Tasks use lazy consensus. A `risk:high` Task stops until a human with
  merge authority approves that exact Plan comment. A revised high-risk plan
  requires fresh approval.
- On resume, repeat the repository and GitHub inspection. Detect orphaned work
  and transfer ownership with a Resume comment that records prior and current
  state, found artifacts, the latest Plan, and the next action. Never create a
  separate resume store or competing owner.
- Preserve the tracking graph: parent and blocker relations, origin `#N`
  references for derived Issues, and `Closes #N` in the Task PR.

## Execution and Evidence

- Treat acceptance criteria and Verification in the Task Issue as the
  test-first work order. Add missing measures before implementation; never
  delete, skip, or weaken a measure to get green status.
- Keep changes within owned paths. Stop and replan when scope, ownership, risk,
  or agreement assumptions materially change.
- Run the exact Task Verification plus relevant deterministic and runtime
  checks. Inspect the final diff and required GitHub checks.
- Evidence is a fresh command result, check, diff, or observed behavior mapped
  to acceptance criteria; an agent statement is not Evidence.
- Before reporting completion in a session, post a measured Outcome and
  Evidence table to the Task Issue. The PR remains the change artifact.
- Diagnose mismatch at the work order, Plan comment, PR diff, and
  Evidence/checks. After three same-command, same-root-cause attempts per
  level, escalate executor to parent/orchestrator to a durable `needs:human`
  state. Only a materially different intervention resets the count.

## Safety and Learning

- Reference PII, secrets, and controlled data at the minimum access-controlled
  source; do not paste them into repository files, Issues, PRs, logs, or agent
  instructions.
- Record the first recurring project or agent-system friction as a
  `retro:candidate`. On the second occurrence of the same class, propose a
  guidance, skill, template, test, or gate change. Offer project-agnostic
  learning upstream once when applicable.
- Agreement, license, and completion merges are distinct human decisions.
  Completion requires deterministic checks, Evidence, Codex review, and
  approval by a non-author human. Agents do not merge or enable enforcement.

## Progressive Disclosure

Use the focused repository skills under `.agents/skills/` for lifecycle
procedures, GitHub comment formats, commands, templates, and deterministic
scripts. Load only the relevant skill; this file defines invariants and does
not replace those procedures.
