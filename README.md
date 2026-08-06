# Codex ADLC Template

> Status: the v1.0.0 candidate now contains the GitHub control plane, Codex
> execution plane, repository skills, deterministic CI, and retro hygiene. The
> canonical template's agreement merge is complete; its measured license trial
> and license merge remain pending.

This is a reusable, Codex-native repository template for the **Agentic
Development Lifecycle (ADLC)**. It keeps intent, plans, changes, evidence, and
lessons in versioned GitHub records instead of ephemeral chat history.

ADLC is an operating layer on top of a team's existing software development
lifecycle. It does not replace Scrum, Kanban, release management, or product
governance. It supplies the durable memory and mechanical verification needed
when stateless agents execute work in parallel.

## Getting Started

### Prerequisites

- Git, Bash 3.2 or later, Ruby with its standard YAML parser, `jq`, and a
  Python 3.11-or-later interpreter available as `python3`, `python3.13`,
  `python3.12`, or `python3.11`.
- An authenticated GitHub CLI (`gh auth status`) with access to Issues, pull
  requests, Actions, and labels in the target repository. Ruleset setup also
  needs Administration write permission; optional Projects setup needs the
  `project` scope.
- A Codex surface with repository access, plus an eligible human code owner who
  uses a GitHub identity other than the trial PR author and can approve it.

### First 10 minutes

1. On GitHub, select **Use this template** and create the target repository.
   Do not clone this canonical source as the project repository.

2. From a terminal, confirm the local tools and GitHub identity before asking
   Codex to change anything:

   ```bash
   git --version
   bash --version
   ruby --version
   jq --version
   python3 --version
   gh auth status
   ```

   If `python3` is older than 3.11, install or expose `python3.11`,
   `python3.12`, or `python3.13` before continuing.

3. Clone the repository created in step 1, then open its root in the Codex app,
   CLI, or IDE extension. Replace `OWNER` and `REPOSITORY` first:

   ```bash
   gh repo clone OWNER/REPOSITORY
   cd REPOSITORY
   ```

4. Confirm that the copied repository fails closed instead of pretending to
   be ready:

   ```bash
   scripts/tuning-status.sh
   ```

   The expected first result is exit `1`, `NOT TUNED`, and both
   `.github/workflows/ci.yml` and `.github/CODEOWNERS` named as incomplete.

5. Create the durable Phase 0α work graph. Run the label helper, then use the
   GitHub **Epic** and **Task** Issue forms to create one setup Epic and the
   first onboarding Task. From the Epic's **Sub-issues** section, add that Task
   as a sub-issue:

   ```bash
   scripts/setup-labels.sh
   ```

6. Give Codex the onboarding Task as its work order. Replace `NUMBER`, then use
   this prompt:

   ```text
   Work from Task #NUMBER and follow AGENTS.md. Use $context-collection and
   $context-distillation to prepare only the project-specific agreement pull
   request. Stop after opening the draft PR. Do not invoke $project-onboarding,
   replace measured CI commands, or create a ruleset before the human agreement
   merge.
   ```

The first session is complete when the setup Epic and its first sub-issue Task
exist, their source links are durable on GitHub, and the repository still
reports `NOT TUNED` for the known CI and ownership placeholders. Continue with
the full onboarding gates below.

### Full onboarding

The following nine gates are the authoritative adoption sequence. Keep their
`Done when` evidence across the setup Epic and its linked Task/PR records. Where
a gate changes repository state, use a dedicated Task and one pull request;
preserve the `1 Task = 1 PR` invariant.

1. **Expose the untuned state.** Run `scripts/tuning-status.sh` in the copied
   repository. **Done when:** it returns `1` and names both
   `.github/workflows/ci.yml` and `.github/CODEOWNERS` as incomplete targets.
2. **Create the Phase 0α receptacle and labels.** Create a setup Epic with an
   onboarding Task, run `scripts/setup-labels.sh`, and collect only the source
   references needed to establish project truth. **Done when:** the Task is a
   sub-issue of the setup Epic and all 11 canonical labels exist without
   applying guessed project commands.
3. **Agree before setup.** Collect and distill the target project's actual
   requirements and decisions, then obtain the human agreement merge.
   **Done when:** the project-specific agreement PR is merged and Phase 0β may
   begin.
4. **Apply measured Phase 0β setup.** Invoke `$project-onboarding`; run the real
   install, format, lint, type-check, test, and build commands, replace the CI
   placeholder, and replace every template CODEOWNER with the eligible target
   user or team. **Done when:** the evidence PR records fresh command results,
   the non-author code-owner path is verified, and `scripts/tuning-status.sh`
   returns `0`.
5. **Propose the review wall disabled.** Run `scripts/setup-ruleset.sh` with the
   measured required checks and inspect the result. **Done when:** GitHub shows
   the ruleset as disabled and its pull-request, code-owner, and required-check
   rules match the evidence; no agent has enabled it.
6. **Run the license trial.** Carry one small Task through its Issue plan,
   implementation, checks, Evidence, and completion PR. **Done when:** required
   checks pass and an eligible non-author human code owner approves the trial
   PR.
7. **Perform the license merge.** Review the setup evidence only after the
   trial and disabled-ruleset review succeed. **Done when:** a human merges the
   setup evidence PR and its review history records the license decision.
8. **Enable only after licensing.** A human may enable the reviewed ruleset in
   GitHub Settings. **Done when:** it is active and an Issue-backed, unapproved
   test pull request cannot merge.
9. **Open the first delivery wave.** File the first delivery Epic, detail only
   its next Tasks, and calculate the frontier. **Done when:** the frontier
   reports at least one open, `type:task`, `ai:ready`, unblocked Task for
   dispatch.

### You are ready when

Use the nine `Done when` clauses above as the source of truth. The repository
is licensed for ordinary delivery only when all of these summary conditions
are observable:

- the agreement and license merges are present in GitHub history;
- `scripts/tuning-status.sh` returns `0` for measured CI and review ownership;
- a human has enabled the reviewed ruleset, and an Issue-backed negative trial
  proves that an unapproved pull request cannot merge; and
- the mechanically calculated frontier contains at least one open, ready,
  unblocked delivery Task.

The setup scripts, Codex skills, Issue forms, workflows, and self-checks are
implemented v1.0.0 candidate artifacts under
[Epic #1](https://github.com/mochan-tk/ttt1-codex/issues/1). They remain a
candidate until the measured license trial is reviewed and merged.

## Measured scaffold status

`tuning-status.sh` has three stable modes:

| Command | Output | Exit behavior |
|---|---|---|
| `scripts/tuning-status.sh` | Human report and measured next steps | `0` when tuned, `1` when incomplete |
| `scripts/tuning-status.sh --quiet` | None | `0` when tuned, `1` when incomplete |
| `scripts/tuning-status.sh --ci` | GitHub warning annotations when incomplete | Always `0` so onboarding remains visible without hiding scaffold defects |

The canonical template repository intentionally retains both copied-template
sentinels and is recognized by its exact GitHub origin. A repository created
from the template has a different origin, so it remains visibly incomplete
until `$project-onboarding` replaces the CI `CUSTOMIZE` block with measured
commands and the CODEOWNERS marker with eligible review ownership.

Run the deterministic scaffold checks locally before every scaffold change:

The checks use Git, Bash, Python 3.11 or later, Ruby's standard YAML parser,
and `gh` for the live read-only retro report. Ruleset and Project setup also
use `jq`. The hosted workflow supplies its lint tools from checksum-verified
release archives.

```bash
git diff --check
bash -n scripts/*.sh .agents/skills/plan-management/scripts/*.sh
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
python3 scripts/check_action_pins.py
scripts/check-md-links.sh
scripts/check-template-sync.sh
scripts/check-skills.sh
scripts/retro-hygiene.sh
scripts/tuning-status.sh
scripts/tuning-status.sh --quiet
scripts/tuning-status.sh --ci
```

The `quality` and `scaffold-self-check` jobs in `.github/workflows/ci.yml` run
the corresponding remote gates. `.github/workflows/retro-hygiene.yml` produces
a read-only report on manual runs by default. Its repository-authorized monthly
schedule, or a manual run with the explicit creation input, may create at most
one `Retro hygiene review YYYY-MM` Issue. It never promotes a candidate or
changes instructions without a reviewed PR. Begin confirmed recurrence
comments with `Occurrence:` or `Occurrence evidence:`. A skill-produced comment
that contains a GitHub Issue/PR evidence link but lacks the prefix is surfaced
as unmarked evidence—not silently ignored or falsely counted. Confirm it with a
new marked comment; its historical unmarked count remains visible because the
ledger is append-only.

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

## GitHub control plane and Codex-native execution

- GitHub is the mandatory ADLC control, ledger, and enforcement plane. Issues,
  labels, sub-issues and dependencies hold the work graph; pull requests,
  reviews, and `Closes #N` hold change and merge history; Actions, checks,
  rulesets, CODEOWNERS, and security automation form the gates; Projects is a
  derived planning view.
- `AGENTS.md` is the small, always-on repository constitution. Nested
  `AGENTS.md` files may add narrower rules near the files they govern.
- `.agents/skills/` contains repo-scoped reusable workflows. Codex loads a
  skill's full `SKILL.md` only when its description or an explicit invocation
  selects it.
- `.codex/agents/` contains project-scoped custom subagents for focused roles.
- `.codex/config.toml` may hold trusted project settings that are safe to share;
  user-specific models, credentials, and personal defaults do not belong in
  the template.
- Codex uses its native instructions, skills, agents, tools, GitHub connection,
  and `gh` fallback to operate that GitHub plane end to end. Session-local state
  is a cache and never replaces a durable GitHub capability.

Codex-specific structure is expected in the execution plane. It must not remove
or silently reimplement an applicable official GitHub control-plane capability.
The shared scaffold therefore retains Issue forms, the PR Evidence template,
CODEOWNERS, Actions, Dependabot, and safe setup scripts for labels, Projects,
and rulesets even though its agent-facing files are Codex-specific.

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
specialize the execution plane for Codex while retaining GitHub as the
mandatory ADLC control plane.

The comparison with separately built Claude and GitHub Copilot templates is
an outcome comparison, not a requirement for identical files. This repository
therefore does not carry `CLAUDE.md` or product-specific compatibility copies.
The released template uses the MIT software license and serves as the book's
Appendix C Codex-native sample repository; the agreement merge is the approval
event for that relationship.
