---
name: project-onboarding
description: Guides Codex through measured onboarding of a new or existing repository, including command characterization, legacy characterization-test work, post-agreement project tuning, and license evidence. Use when a template is first adopted, repository commands or guidance drift, onboarding is incomplete, or unattended delegation must be licensed again.
---

# Project Onboarding

Build Phase 0β from accepted project truth and measurements. Keep the reusable
template generic; never promote a guessed command, product fact, credential,
personal path, organization name, or model choice.

## Establish the boundary

1. Start from a Task Issue and use the Issue timeline as the durable ledger.
2. Read `docs/agreements/`, the repository guidance, manifests, lockfiles,
   existing CI, and linked source context.
3. Confirm the agreement merge has accepted the project truth to be applied.
   If truth is missing or disputed, stop onboarding and route it through
   collection, distillation, and a dedicated agreement PR.
4. Treat setup evidence as a proposal until a human performs the license merge.

## Measure the repository

1. Inventory languages, workspaces, manifests, runtime constraints, CI jobs,
   test locations, linters, formatters, build targets, deployment boundaries,
   hardware dependencies, and sensitive-data constraints. Detect facts before
   asking questions.
2. Produce an inventory table with area, observed evidence, candidate command,
   routed environment, and confidence.
3. Ask once, in one small batch, only for facts the inventory cannot establish.
   Reference controlled facts at their governed source; do not paste them.
4. Run every candidate install, format, lint, type-check, test, and build command
   in the environment where agents will use it. Record the exact command,
   prerequisites, exit status, meaningful output, runtime, and workaround.
   Never publish an unrun command as project guidance.

## Characterize existing behavior

For an existing codebase without behavioral tests, create and complete
characterization-test Tasks before delegating feature changes. Freeze observed
behavior without claiming that it is correct. Keep hardware-only or local-only
verification in separately routed Tasks.

## Apply measured project truth

After agreement, tune only project-dependent surfaces: root or nested
`AGENTS.md`, relevant repo skills and custom agents, portable `.codex/`
configuration, CI commands, setup automation, and repository maps. Keep each
command synchronized with its deterministic CI gate and its applicable
execution environment. Remove placeholders and inapplicable examples instead
of leaving ambiguous alternatives.

Do not weaken a check to make onboarding pass. Record a real failure, file the
derived Task with its origin `#N`, and keep unattended work inside the measured
area.

## Prepare license evidence

Open one setup-evidence PR and map every claim to a fresh observation:

| Claim | Required evidence |
|---|---|
| Project commands are usable | Exact commands and observed results |
| Guidance matches CI | Diff plus a successful deterministic run |
| Codex can discover the setup | Fresh-session discovery result |
| Delegation path works | One small Task carried from Issue plan comment through checks, Evidence, `Closes #N`, and non-author human review |
| Enforcement is ready | Proposed ruleset and review state; keep enforcement disabled until human approval |

Post the measured outcome and Evidence to the onboarding Task before reporting
completion. A human reviews the evidence and performs the license merge; the
agent does not declare or enable its own autonomy license.

## Stop conditions

Stop and create or update the durable Issue record when an agreement is wrong,
a required command cannot be measured, credentials or PII would need copying,
the routed environment cannot execute a criterion, or the proposed setup would
silently replace an official GitHub control.
