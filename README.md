# Agentic Dev Kit for Codex

A Codex-native, evidence-driven development lifecycle built on GitHub's durable
ledger. It turns intent, plans, changes, verification, and lessons into records
that a fresh agent session can reconstruct without chat history.

This is a deliberate reconstruction of
[`agentic-dev-kit-for-copilot`](https://github.com/mochan-tk/agentic-dev-kit-for-copilot)
for current Codex concepts. It is not a filename substitution: Copilot
instructions, agents, prompts, skills, setup, and MCP assumptions are mapped to
`AGENTS.md`, repo skills, project custom agents, portable config, GitHub
controls, plugins, connectors, and safe optional integrations.

## What is included

- A concise root `AGENTS.md` constitution and support for nested instructions.
- Nine workflows under `.agents/skills/`: context collection, distillation,
  onboarding, planning, routing, orchestration, verification, retro, and safe
  Codex automation design.
- Four focused custom agents under `.codex/agents/`: explorer, planner,
  orchestrator, and reviewer. They have read-only defaults and explicit
  no-write instructions; parent and user runtime policy remains authoritative.
- GitHub Issue forms, plan/outcome chronology, PR Evidence, CODEOWNERS,
  Dependabot, required-check scaffolding, ruleset/Project/label helpers, and
  retro hygiene.
- Pluggable builtin and spec-kit context connectors.
- A collision-safe Bash installer, Windows Git Bash launcher, upgrade
  preservation, provenance marker, and LF-safe distribution.
- A validated skills-only Codex plugin artifact.
- Deterministic validators, regression tests, CI, migration guidance,
  capability traceability, examples, limitations, and maintenance procedures.

## Quick start

Prerequisites are Git, Bash 3.2+, Ruby with its standard YAML parser, `jq`,
Python 3.11+, and a current Codex surface. Live GitHub setup also needs an
authenticated `gh` session for `github.com`; optional Projects and rulesets
need their corresponding account permissions. Windows uses Git for Windows
and the included PowerShell launcher.

### New repository

Use this repository as a GitHub template, clone the result, and open its root in
Codex app, CLI, IDE, or cloud. Confirm the copied instance is visibly untuned:

```bash
.github/scripts/tuning-status.sh
```

Preview and then explicitly apply the canonical labels:

```bash
.github/scripts/setup-labels.sh --dry-run
.github/scripts/setup-labels.sh --apply
```

Create a setup Epic and Task with the Issue forms. Give the Task to Codex and
invoke `$context-collection`, `$context-distillation`, and then
`$project-onboarding`. Do not enter measured setup until a human agreement
merge accepts the project truth.

### Existing repository

Preview from a local kit checkout without network access:

```bash
SCAFFOLD_SOURCE_DIR=/absolute/path/to/agentic-dev-kit-for-codex \
  bash /absolute/path/to/agentic-dev-kit-for-codex/.github/scripts/scaffold-init.sh \
  --dry-run /absolute/path/to/target-repository
```

Remove `--dry-run` only after reviewing the plan. A fresh install refuses
collisions and all symlink paths, stages the result, and never commits. For an
adopted instance, use `--upgrade --dry-run` first; upgrades refresh kit-owned
machinery and preserve project agreements, context, workflows, ownership,
constitution, and Codex config for manual reconciliation.

See the [complete quickstart](.github/docs/guides/quickstart.md).

### Skills-only plugin

[`plugin/agentic-dev-kit-for-codex/`](plugin/agentic-dev-kit-for-codex/)
contains the same nine skills as a valid plugin artifact. It intentionally does
not install the repository constitution, custom project agents, GitHub
controls, config, or scripts. Its `LICENSE` and `NOTICE.md` make the directory
self-contained for packaging. This repository does not alter a personal/team
marketplace; marketplace publication or registration is a separate maintainer
step.

## Lifecycle

| Phase | Result | Durable home |
|---|---|---|
| 0α. Minimum receptacle | The project can receive reviewed context without guessed setup | Issue forms, context and agreement directories |
| 1. Collect | Sources and minimum extracts are captured with provenance | `.github/docs/context/`, connector pins |
| 2. Distill and agree | Requirements, decisions, boundaries, and terms become reviewed truth | Agreement PR and merge |
| 0β. Measured setup | Codex guidance and CI use commands actually run in the target environment | `AGENTS.md`, skills, config, CI, evidence PR |
| 3. Plan and orchestrate | Epic/Task dependencies expose the actionable frontier | GitHub Issue graph and plan comments |
| 4. Route and execute | One owner changes one bounded Task | Task session, worktree, branch, PR |
| 5. Verify and learn | Evidence passes checks/review and recurring friction improves the system | Checks, outcome comment, completion merge, retro |

## The Three Merges

Human judgment is concentrated in three durable events:

| Merge | Human accepts | Evidence |
|---|---|---|
| Agreement | What to build and the constraints | Reviewed requirements, ADRs, non-goals, glossary |
| License | The measured repository setup is safe enough to delegate | Setup evidence plus one complete trial Task |
| Completion | One Task meets its work order | Fresh Evidence, required checks, Codex review, non-author human approval |

A chat approval is not a merge. Agents do not approve their own high-risk plan,
enable enforcement, merge a PR, or declare the repository licensed.

## Operating invariants

- GitHub commits, Issues, comments, PRs, reviews, and checks are the durable
  ledger. Session state and Projects views are replaceable caches.
- `1 Task = 1 session = 1 worktree = 1 branch = 1 PR` with one active writer.
- The requester owns the Task body. The executor records Start, Plan, Revised
  Plan, Resume, and Outcome as append-only comments.
- Acceptance criteria and measures precede implementation. An agent statement
  is never Evidence.
- Parallel Tasks own disjoint paths; overlap becomes a dependency.
- A high-risk Task stops after the exact Plan comment until an authorized human
  approves it. Normal Tasks use lazy consensus.
- Credentials, PII, controlled data, private endpoints, personal paths, and
  concrete model pins do not belong in the generic kit or public ledger.
- After three same-command, same-root-cause attempts at a level, escalate
  rather than grind until green.

## Codex-native structure

```text
AGENTS.md                           repository constitution
.agents/skills/                    nine canonical workflows
.codex/agents/                     four agents with read-only defaults
.codex/config.toml                 portable trusted-project settings
.github/connectors/                context source contract and definitions
.github/docs/                      agreements, context, and operating guides
.github/scripts/                   setup, installer, validators, and tests
.github/workflows/                 deterministic CI and hygiene
plugin/agentic-dev-kit-for-codex/  synchronized skills-only package
```

The architecture follows current official guidance for
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[skills](https://learn.chatgpt.com/docs/build-skills),
[custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[plugins](https://learn.chatgpt.com/docs/build-plugins), and
[hooks](https://learn.chatgpt.com/docs/hooks).

No active hook, organization-specific MCP server, app automation, or
secret-bearing Codex Action is enabled by default. Use `$codex-automation` to
select and review the smallest supported mechanism.

## Safe setup helpers

The label, Project, and source helpers are preview-first and require explicit
`--apply` before mutation:

```bash
.github/scripts/setup-labels.sh --dry-run
.github/scripts/setup-project.sh init --dry-run
.github/scripts/setup-ruleset.sh --dry-run --integration-id 123456
.github/scripts/setup-sources.sh --source builtin --dry-run
```

The ruleset helper requires exactly one of `--dry-run` or `--apply`, a reviewed
positive GitHub App integration ID, and the exact three source-bound contexts
`quality`, `scaffold-self-check`, and `secure-devcontainer`. Dry-run is
hermetic. Apply targets GitHub.com, shows the exact repository, name, and
integration ID, then requires an exact confirmation before its first GitHub
call. It may create or reuse only a fully compatible enforcement-disabled
proposal; it cannot activate, overwrite, update, or delete a ruleset and never
falls back to an any-source check. A human must independently prove the trusted
publisher identity before deciding whether to enforce the proposal. The source
activation helper writes only a local registry; its activation PR remains the
durable decision.

## Base-owned Actions admission boundary

The repository's base-owned CI workflow listens only to default-branch
`pull_request_target` and `issue_comment` activity. Its no-checkout admission
controller re-fetches the open pull request, exact repository identities and
SHAs, every paginated file and rename origin, and the complete live human
authorization set before it can release an isolated candidate worker. It
classifies runtime controls separately from bootstrap-only Actions,
CODEOWNERS, ruleset, and controller-test paths. Public-fork code is never
checked out from a `pull_request_target` run. Workers use a fresh runner,
read-only contents, a pinned checkout of the accepted repository and SHA, and
no credentials, environments, OIDC, cache, or artifact handoff to the
write-capable publisher.

The external, human-applied GitHub Actions Policy allows exactly
`pull_request_target`, `issue_comment`, `issues`, and `schedule`. The `issues`
exception exists only for the unchanged default-branch adopter-feedback
receiver on `types: [opened]`; `schedule` exists only for monthly Retro hygiene.
Candidate-selected `pull_request`, `push`, `workflow_dispatch`, `merge_group`,
and every other event stay denied. A blocked event is evidence only when an
Active Policy capture and a GitHub-hosted `startup_failure` record bind the
exact event, actor, trusted SHA, denial annotation, zero jobs, zero steps, and
no side effect. Branch-ruleset API output is not Actions Policy evidence.

Only the isolated publisher can write the exact commit-status contexts
`quality`, `scaffold-self-check`, and `secure-devcontainer`. It establishes a
failure/pending exact-head baseline before workers start, revalidates live
identity, diff, and authorization on a fresh runner, rejects a newer run's
status ownership, and treats failure, cancellation, or skipped applicable work
as failure. Commit statuses are not atomic, so a complete source-bound ruleset
and hosted same-repository/public-fork proof remain mandatory before these
contexts are enforced.

Hosted Retro is schedule-only. Run a local report with
`.github/scripts/retro-hygiene.sh -R owner/repo`; create the idempotent monthly
Issue explicitly with
`.github/scripts/retro-hygiene.sh --create-issue -R owner/repo`. A future
remote manual route requires its own reviewed,
default-branch-owned receiver. Future bootstrap-only controller changes are
high-risk and human-only; they must not fall back to candidate-triggered code.
CODEOWNERS on this bootstrap PR is still evaluated from the base branch, so the
separate non-author review on the exact final SHA remains the merge gate.

## Validation

Run scaffold checks before every kit change:

```bash
git diff --check
git diff --cached --check
bash -n .github/scripts/*.sh .agents/skills/plan-management/scripts/*.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s .github/scripts/tests -p 'test_*.py' -v
.github/scripts/tests/run-portable-tests.sh
python3 .github/scripts/check_action_pins.py
.github/scripts/check-md-links.sh
.github/scripts/check-template-sync.sh
.github/scripts/check-skills.sh
.github/scripts/check-connectors.sh
.github/scripts/check-changelog-refs.sh
.github/scripts/check-escalation-wording.sh
.github/scripts/check-workflow-permissions.sh
.github/scripts/retro-hygiene.sh
.github/scripts/tuning-status.sh --ci
```

The copied project also runs the exact install, format, lint, type-check, test,
build, and security commands measured by `$project-onboarding`.

## Documentation

- [`.github/docs/agreements/`](.github/docs/agreements/README.md) — reviewed
  requirements, decisions, boundaries, terminology, and retrospectives
- [Architecture](.github/docs/guides/architecture.md)
- [Copilot source capability map](.github/docs/guides/copilot-capability-map.md)
- [Migration from Copilot and earlier Codex versions](.github/docs/guides/migration-from-copilot.md)
- [Examples](.github/docs/guides/examples.md)
- [Limitations](.github/docs/guides/limitations.md)
- [Maintenance and release procedure](.github/docs/guides/maintenance.md)
- [Context connector contract](.github/connectors/README.md)
- [Adopter feedback privacy boundary](.github/docs/adopter-feedback.md)
- [Installed-kit license and attribution](.github/docs/AGENTIC-DEV-KIT-NOTICE.md)
- [Security policy](SECURITY.md)
- [Attribution](NOTICE.md)

## Source, license, and status

The reconstruction audits the Copilot source at commit
`f466c7e169243e2bea03b4b33a20f8c557328d96`. The detailed mapping records a
Codex implementation or an explicit non-port reason for every major source
surface. Existing Codex-native work was retained where it was stronger; the
source was not copied as a compatibility tree.

Licensed under the [MIT License](LICENSE). Copyright (c) 2026 Takashi Kawamoto
(Mr.Mo). See [NOTICE.md](NOTICE.md) for source attribution.

Until a reviewed tag/release and live adoption trial exist, use an exact commit
SHA for repeatable installation and treat the current version as a release
candidate rather than a published marketplace package.
