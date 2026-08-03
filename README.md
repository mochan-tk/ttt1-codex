# Codex ADLC Template

> Status: v1.0.0 is being built in this repository by running the lifecycle it
> defines. The agreement set is the first human merge gate.

This is a reusable, Codex-native repository template for the **Agentic
Development Lifecycle (ADLC)**. It keeps intent, plans, changes, evidence, and
lessons in versioned GitHub records instead of ephemeral chat history.

ADLC is an operating layer on top of a team's existing software development
lifecycle. It does not replace Scrum, Kanban, release management, or product
governance. It supplies the durable memory and mechanical verification needed
when stateless agents execute work in parallel.

## This is a template — after copying

1. Run `scripts/setup-labels.sh` to create the canonical Issue labels.
2. Invoke `$project-onboarding`. It inventories the repository, asks only for
   missing facts, runs the real build and test commands, and prepares an
   evidence pull request.
3. Run one small trial Task through plan, implementation, checks, and review.
   Merge the measured setup evidence only after the trial succeeds. That is
   the **license merge**.
4. Run `scripts/setup-ruleset.sh`. It creates the proposed ruleset disabled;
   a human reviews and enables it in GitHub Settings.
5. File the first Epic, detail only its next rolling wave, and dispatch Tasks
   from the mechanically calculated frontier.

The setup scripts and skills named above are planned v1.0.0 artifacts and land
in later Tasks under [Epic #1](https://github.com/mochan-tk/ttt1-codex/issues/1).

## The Three Merges

Human judgment is concentrated in dispatch and three durable merge events.

| Merge | What the human accepts | Durable record |
|---|---|---|
| **Agreement merge** | What to build, why, and what not to build | Reviewed REQ, ADR, non-goals, and glossary pull request |
| **License merge** | That the measured repository setup is safe enough for unattended delegation | Setup evidence pull request plus one end-to-end trial Task |
| **Completion merge** | That a Task meets its executable acceptance tests, required checks, non-author human approval, and design expectations | Task pull request linked with `Closes #N` |

A chat approval is not one of the Three Merges. The merge and its review history
are the ledger entry.

## Lifecycle

| Phase | Outcome | Primary durable home |
|---|---|---|
| 0α. Minimum receptacle | A thin template instance can receive distilled knowledge | Repository template, `docs/`, Issue forms |
| 1. Collect | Source references and minimum extracted notes arrive with provenance; originals and controlled data stay outside | `docs/context/` and governed source links |
| 2. Distill & agree | Requirements, decisions, vocabulary, and boundaries become reviewed truth | `docs/agreements/` and the agreement merge |
| 0β. Measured setup | Codex guidance, skills, agents, tools, and commands are filled from agreed truth and verified by running them | `AGENTS.md`, `.agents/skills/`, `.codex/`, evidence PR |
| 3. Plan & orchestrate | Epic sub-issues and dependencies expose the actionable frontier | Issue graph; Projects is a view |
| 4. Route & execute | One Task runs in one session, worktree, branch, and PR | Task Issue timeline and Task branch |
| 5. Verify & learn | Deterministic gates, review, retro, and upstream improve the system | Checks, Evidence table, retro and template PRs |

## Codex-native architecture

- `AGENTS.md` is the small, always-on repository constitution. Nested
  `AGENTS.md` files may add narrower rules near the files they govern.
- `.agents/skills/` contains repo-scoped reusable workflows. Codex loads a
  skill's full `SKILL.md` only when its description or an explicit invocation
  selects it.
- `.codex/agents/` contains project-scoped custom subagents for focused roles.
- `.codex/config.toml` may hold trusted project settings that are safe to share;
  user-specific models, credentials, and personal defaults do not belong in
  the template.
- GitHub Issues, pull requests, Actions, rulesets, Projects, and CODEOWNERS are
  shared ledger and enforcement components, not compatibility shims.

This layout follows the current Codex documentation for
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[repo-scoped skills](https://learn.chatgpt.com/docs/build-skills), and
[project-scoped custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
Deprecated custom prompts are not part of the design.

## Operating invariants

- **Record before report:** write the start, plan, changes, outcome, and
  evidence to the Task Issue or PR before summarizing them in a session.
- **Verify before done:** an agent's statement is not evidence; commands,
  checks, diffs, and observable behavior are.
- **Single writer:** parallel Tasks do not own overlapping paths.
- **One work unit:** `1 Task = 1 session = 1 worktree = 1 branch = 1 PR`.
- **Requester-owned work order:** the executing agent never edits its Task
  Issue body. Changed instructions receive a change comment from the requester.
- **Plan authority:** the working plan lands as an added Task Issue comment
  before implementation. Revised plans are new comments, never edits. PR text
  may copy the plan but must link to the authoritative comment.
- **Outcome authority:** the executor posts the measured outcome and evidence
  to the Task Issue before reporting completion; the PR remains the change
  artifact and links both the plan and Task.
- **Tests first:** acceptance criteria land as executable tests or checks before
  implementation. Retries have a budget and an escalation path.
- **Reference, do not paste:** credentials, PII, and controlled data remain in
  access-controlled systems; Issues and PRs contain only the minimum reference.

The reviewed requirements and decisions live in
[`docs/agreements/`](docs/agreements/README.md).

## Human boundary

Humans own the work order, review bandwidth, exceptions, and the Three Merges.
Agents collect, plan, implement, run checks, record evidence, diagnose, and
propose improvements. High-risk Tasks are the exception to lazy consensus:
they stop after the plan comment until an authorized human approves it.

Every repository setting change, however small, starts from an Issue. An agent
prepares the exact action and evidence; a human performs only a non-delegable UI
or trust decision, and the observed result is recorded back on the Issue.
Automation may propose a disabled ruleset, but it must not enable enforcement
or mark the repository as a GitHub template on its own.

## Origin and comparison scope

This repository is consolidated from
[`mochan-tk/tt1` main at `74b8b65`](https://github.com/mochan-tk/tt1/tree/74b8b6500b0138c1f667262ced6894d808e73404)
(released there as v0.5.0), the proposed v0.6.0 plan-landing semantics at
[`9450b52`](https://github.com/mochan-tk/tt1/commit/9450b52874a22943d5424c5239a1ffa46c4032c7),
the 2026-08-02 ADLC design review, and the
[pinned chapter manuscript](https://github.com/mochan-tk/k-wk4-codex/blob/a7eb2629424282f9b8262e0248bed7f1879058db/manuscript/02_agentic_development.md).
It was rebuilt with fresh history after the owner's 2026-08-03 decision to
specialize this variant for Codex.

The comparison with separately built Claude and GitHub Copilot templates is
an outcome comparison, not a requirement for identical files. This repository
therefore does not carry `CLAUDE.md` or product-specific compatibility copies.
The released template uses the MIT software license and serves as the book's
Appendix C Codex-native sample repository; the agreement merge is the approval
event for that relationship.
