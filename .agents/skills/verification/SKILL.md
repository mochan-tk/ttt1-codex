---
name: verification
description: Proves a Task against test-first acceptance criteria using fresh Evidence, deterministic required checks, four-part mismatch diagnosis, Codex review, and non-author human review. Use when writing a work order's Verification section, validating a change before completion, triaging a failed check, auditing an Evidence claim, or recording outcome before reporting.
---

# Verification

Treat an agent statement as a claim, never as Evidence. Build the verification
wall before implementation and preserve failures as information.

## Detect the distribution boundary

Before running a command that writes workspace artifacts or performing a live
GitHub step, check for root `AGENTS.md`, a readable Task with Acceptance,
Verification, and File ownership, its authoritative Plan comment, and the
repository PR/check controls. If any are absent, name the missing controls and
treat this as a plugin-only or partial installation. Inspect supplied files,
logs, diffs, and existing results read-only and return a draft verification
matrix with proposed commands and expected results. Do not edit code, generate
test artifacts, post an Outcome, change a label, approve, merge, or claim a
required gate passed. Never fabricate Evidence or enforcement. Offer the
full-kit installation when durable verification is required. Any live write
requires every missing control to be restored and verified first, then
separate explicit authority.

## Write a test-first work order

For every acceptance criterion, state an executable command or observable check
and its expected result in the Task Issue before implementation. Include
negative cases where meaningful. Route hardware, signed-in UI, or local-only
checks to a surface that can execute them; split incompatible criteria into a
linked Task rather than marking them untested.

If no objective measure can be written, stop planning, sharpen the requirement,
or request human judgment explicitly. Never weaken, skip, delete, or rewrite a
measure merely to obtain green status.

## Verify in layers

Run layers in order and do not substitute a later layer for an earlier one:

1. Deterministic local checks: formatting, lint, types, tests, build, and exact
   Task-specific commands.
2. Security checks: secret, dependency, and code scanning without unexplained
   suppressions.
3. Required checks on the actual PR commit. Inspect them with `gh pr checks`
   or the GitHub tool and confirm the checked SHA.
4. Codex or designated reviewer analysis of scope, design, claim/evidence, and
   silent deviations.
5. Approval by a non-author human with merge authority. Human judgment and the
   completion merge cannot be replaced by automation.

## Diagnose a mismatch at four addresses

Classify before changing anything:

1. **Work-order body:** the requester asked for the wrong or incomplete result.
2. **Plan comment:** the executor selected the wrong approach or sequence.
3. **PR diff:** the implementation diverged or is defective.
4. **Evidence/checks:** the measure, environment, observation, or gate is wrong.

Intervene at that address: requester body change plus change comment, revised
plan comment, code correction, or a check/environment repair. Route a bad
agreement through a derived agreement Issue and PR. Do not patch code to satisfy
a test that encodes an unaccepted premise.

## Record fresh Evidence

Run every Verification command and map every criterion to a fresh result:

```markdown
| Criterion | Evidence (command, check, diff, or link) | Result |
|---|---|---|
| <criterion> | `<exact command>` -> <observed output> | pass |
```

Use `deferred` only with a linked follow-up Issue whose routing can execute the
criterion. Any `deferred` result blocks `Outcome: completed` and the completion
merge; a follow-up link alone is insufficient. The requester must first revise
the original requester-owned work-order body to remove the criterion or move it
into a linked, separate Task, then record that body change. Merely creating the
follow-up or split Task does not unblock completion. Until the body is revised,
record `blocked` or `needs-replan`. The executor may propose the change in a
comment but never edits the body. Confirm the diff stays inside File ownership
and the worktree is clean. Record failures and deviations; do not summarize
them away.

## Enforce outcome-before-report

Post the outcome and Evidence table to the Task Issue before a session reports
completion. Link the authoritative plan comment and PR. Keep the PR as the
change artifact, require its body to contain `Closes #N`, and require all
deterministic required checks plus non-author human review before the completion
merge.
