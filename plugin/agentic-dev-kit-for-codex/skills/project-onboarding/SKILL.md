---
name: project-onboarding
description: Guides Codex through measured onboarding of a new or existing repository, including command characterization, legacy characterization-test work, post-agreement project tuning, and license evidence. Use when a template is first adopted, repository commands or guidance drift, onboarding is incomplete, or unattended delegation must be licensed again.
---

# Project Onboarding

Follow project onboarding in this explicit order:

1. **Phase 0α — minimum receptacle:** establish only the Issue, agreement,
   ownership, and verification surfaces needed to collect project truth. Do
   not guess project-specific setup.
2. **Agreement merge:** collect and distill that truth, then obtain its human
   agreement merge.
3. **Phase 0β — measured setup:** only after the agreement merge, measure the
   repository and apply accepted project truth to its Codex setup.

Never enter Phase 0β before the agreement merge. Keep the reusable template
generic; never promote a guessed command, product fact, credential, personal
path, organization name, or model choice.

## Detect the distribution boundary

Before bootstrap, check for `.github/scripts/setup-labels.sh`,
`.github/scripts/setup-sources.sh`, `.github/CODEOWNERS`, and
`.github/docs/agreements/`. If any are absent, this is a plugin-only or partial
installation:

1. Complete a read-only repository assessment from the files that exist.
2. Report which full-kit contracts are missing and explain that GitHub control
   bootstrap and license-evidence onboarding require the template or installer.
3. Do not invoke, fabricate, or silently substitute a missing helper. Offer the
   full-kit installation path, then stop before the bootstrap and mutation
   steps below.

Any live write requires every missing control to be restored and verified
first, then separate explicit authority.


## Land an installer handoff

When `scaffold-init` has left staged files, treat them as an untrusted proposal,
not as permission to publish:

1. Inspect `git status --short`, `git diff --cached`, and
   `git diff --cached --check`; run the installed deterministic validators.
2. Explain the exact commit, branch, remote, and PR/default-branch route. Actions
   do not establish the scaffold until its reviewed change reaches the default
   branch.
3. Ask for explicit authorization before committing, pushing, opening a PR, or
   changing any GitHub setting. Invoking this skill alone grants none of those
   permissions.
4. If authorized, use a bounded branch/PR path when protection prevents direct
   landing. Otherwise stop with the staged work intact and a concrete handoff.

## Bootstrap the minimum control plane

During Phase 0α, preview each action before requesting consent:

1. Run `.github/scripts/setup-labels.sh --dry-run`, show the exact GitHub.com
   target and label plan, and run it again with `--apply` only after explicit
   approval. Labels are repository state; a preview is not authorization.
2. Choose the initial context connector from observed project needs. Preview
   `.github/scripts/setup-sources.sh --source <name> --dry-run`; after the
   source choice is accepted and the local write is approved, use `--apply`
   and carry that registry change in the onboarding PR.
3. Prepare the phase outline with `$plan-management`: one coarse Epic per
   phase, all siblings, ordered with `blocked-by`; never put an Epic under an
   Epic. Draft bodies and dependencies before any live Issue creation, which
   requires separate explicit approval. Do not decompose Tasks during
   onboarding. Once the phase Epics exist, a program session may coordinate
   their sibling Epic-parent sessions.
4. Preview the ruleset only as described below. Never enable it from onboarding.


## Establish the boundary

1. Start from a Task Issue and use the Issue timeline as the durable ledger.
2. Read `.github/docs/agreements/`, the repository guidance, manifests, lockfiles,
   existing CI, `.github/CODEOWNERS`, and linked source context.
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

Replace every template owner in `.github/CODEOWNERS` with a user or team that
has the required access in the target repository. Confirm that an eligible
human using a GitHub identity other than the trial PR author can perform the
required code-owner review. Remove the `CUSTOMIZE:` marker only after both the
ownership and non-author review path are verified. Propose the default-branch
ruleset with enforcement disabled and inspect its owned paths and required
checks; neither onboarding nor an agent enables it.

In this release candidate, `.github/scripts/setup-ruleset.sh` is owned by
separate frozen admission-boundary work. Run only its `--dry-run` path; do not
invoke its live path or treat a preview as license evidence. Record the missing
source-bound check integration as a blocker until that work lands.

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
| Review ownership works | CODEOWNERS diff plus a trial PR review by an eligible non-author human code owner |
| Enforcement is ready | Inspected ruleset with enforcement disabled, matching owned paths and required checks |

Post the measured outcome and Evidence to the onboarding Task before reporting
completion. License evidence is incomplete until review ownership and the
disabled-ruleset proposal are both proven. A human reviews the evidence and
performs the license merge; the agent does not declare or enable its own
autonomy license.

## Record the durable onboarding handoff

Before the evidence PR is complete, collect every onboarding item that remains
unrun, unverified, declined, blocked, or external. This includes missing-tool
commands, credentials, provisioning, pushes, deploys, hardware checks, skipped
consent steps, and live settings or account checks. Put them in one durable
checklist with reasons:

```markdown
## Deferred from onboarding

- [ ] <item> — <why it was not completed and the next accountable surface>
```

Append this ledger to the first-phase Epic. If no Epic was created, put it in
the evidence PR instead. A chat summary is not a carrier: a deferred item that
exists only in chat is lost and does not count as recorded.

Keep the first-phase Epic durable and actionable:

- its body has the onboarding draft marker until approval;
- its `## Decomposition state` has exactly one current line; and
- its body names the next move: review the Epic, then decompose its first Task
  wave with `$plan-management`.

Later phase Epics remain coarse siblings with `blocked-by` ordering. Hand them
off first phase first. The program session starts the applicable Epic-parent
session when predecessors close; onboarding does not recursively start a
successor phase.

The evidence PR body must end with this durable section (fill in the links):

```markdown
## Next steps

1. Review and merge this evidence PR (the license merge).
2. Review the phase Epics, first phase first: <Epic links or Epic-form pointer>.
3. When the first Epic is accepted, use `$plan-management` to decompose its
   first Task wave and `$session-orchestration` to run ready Tasks.
```

Also return the same three moves in the final chat handoff because adopters
read chat, while keeping the PR and Epic copies authoritative because chat can
disappear. Pushing a branch is not completion: the evidence PR must exist. If
PR creation lacks permission or approval, record the blocker and provide the
exact proposed PR command without implying it ran.

## Stop conditions

Stop and create or update the durable Issue record when an agreement is wrong,
a required command cannot be measured, credentials or PII would need copying,
the routed environment cannot execute a criterion, no eligible non-author
human code owner can review the trial, the proposed ruleset is not disabled,
the deferred ledger or durable `Next steps` handoff cannot be recorded, or the
proposed setup would silently replace an official GitHub control.
