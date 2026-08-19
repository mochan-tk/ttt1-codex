# Current Copilot source to Codex reconstruction map

Audit captured: 2026-08-19<br>
Source: [mochan-tk/agentic-dev-kit-for-copilot at fd265ddef150fab86cd54d0e383c2c25fe297ffb](https://github.com/mochan-tk/agentic-dev-kit-for-copilot/tree/fd265ddef150fab86cd54d0e383c2c25fe297ffb) — 135 tracked files<br>
Target: [mochan-tk/ttt1-codex at 0f114d2d98f8e906bf924a4fab873897c38963e1](https://github.com/mochan-tk/ttt1-codex/tree/0f114d2d98f8e906bf924a4fab873897c38963e1) — 129 tracked files

This map is a human index to the complete machine-readable authority:

- [fixed baselines](../planning/codex-reconstruction/baselines.json)
- [one-row-per-file source inventory](../planning/codex-reconstruction/source-inventory.json)
- [one-row-per-file target inventory](../planning/codex-reconstruction/target-inventory.json)
- [61-row behavioral parity ledger](../planning/codex-reconstruction/parity-ledger.json)
- [official Codex capability research](../planning/codex-reconstruction/codex-capability-research.md)
- [runtime spike program](../planning/codex-reconstruction/runtime-capability-spikes.md)
- [proposed execution model](../agreements/adr/ADR-0005-codex-reconstruction-execution-model.md)
- [rolling-wave reconstruction plan](../planning/codex-reconstruction/reconstruction-plan.md)

Open work and documents are not counted as merged implementation. The exact
JSON inventories, not this summary table, close file-level traceability.

## Current source inventory closure

| Source area | Tracked files | Current disposition |
|---|---:|---|
| Root files | 6 | Constitution, overview, license, lineage, ignore, and line-ending policy are traced. |
| .devcontainer/** | 3 | Product-specific contributor environment; exact payload is NON_PORTABLE. |
| .vscode/** | 1 | Unpinned and non-distributed MCP declaration; NON_PORTABLE. |
| .github root metadata | 4 | CODEOWNERS, PR template, Copilot instructions, Dependabot. |
| .github/ISSUE_TEMPLATE/** | 4 | Epic, Task, feedback, and Issue policy. |
| .github/agents/** | 3 | Copilot roles mapped to Codex custom agents and Skills. |
| .github/connectors/** | 4 | Context Contract and two provider definitions. |
| .github/docs/** | 17 | Adopter docs plus current source development records that leak across the stated distribution boundary. |
| .github/instructions/** | 3 | Product-specific scoped instructions mapped to AGENTS/Skills/agreements. |
| .github/prompts/** | 7 | Product-specific entrypoints mapped to Skill invocation metadata. |
| .github/scripts/** production/data | 25 | Setup, installer, ritual, governance, feedback, retro, Windows, and sensors. |
| .github/scripts/tests/** | 25 | Deterministic source fixture suites. |
| .github/skills/** | 12 | Eight Skills and plan-management assets. |
| .github/workflows/** | 4 | CI, feedback, retro, and Copilot setup. |
| Root docs/** | 17 | Source development ADR/context/images; correctly non-distributed. |
| **Total** | **135** | Exact path/blob coverage is proved by source-inventory.json. |

The historical target map stopped at 110 source files. The fixed current source
adds 25 files and modifies 34 existing paths (59 changed paths total), including
the two-tier Task lifecycle, durable
dispatch/release, Project naming, HOTL governance, ownership/status/drift
sensors, solo/team ruleset profiles, Windows launcher, platform capability
baseline, and plugin no-go evidence.

## Current target inventory closure

| Target area | Tracked files | Evidence calibration |
|---|---:|---|
| Root | 9 | Constitution, project docs, legal/lineage, repository hygiene. |
| .agents/skills/** | 23 | Nine canonical Skills, metadata, references, scripts, and templates. |
| .codex/** | 5 | Four read-only-default custom roles and portable project config. |
| .github Issue templates | 4 | Structured planning and feedback intake. |
| .github connectors | 4 | Contract and definitions; no live source registry. |
| .github agreements | 9 | Accepted requirements/ADRs; acceptance is not implementation proof. |
| .github context | 1 | Adopter provenance namespace only. |
| .github guides | 7 | Descriptive/operator guidance. |
| .github docs root | 3 | Kit license/notice and feedback disclosure. |
| .github root | 3 | CODEOWNERS, PR template, Dependabot. |
| .github scripts | 18 | Validators, setup, installer, feedback, retro. |
| .github script tests | 14 | Portable and Python deterministic suites. |
| .github workflows | 3 | Base-owned CI, feedback, retro. |
| Plugin | 26 | Manifest/legal files and exact Skills mirror. |
| **Total** | **129** | Exact path/blob coverage is proved by target-inventory.json. |

The target baseline has no merged Dev Container payload, no SOURCES registry,
no linked Project, no source-bound disabled ruleset proposal, no tag/release,
and no marketplace/live-adopter/native-Windows proof.
Accepted REQ-016 and REQ-017 also cite an ADR-0006 that is absent from both
pinned repositories; this pre-existing dangling authority requires a separate
agreement cleanup and is not silently repaired by Task #59.

## Behavioral status

| Status | Rows | Interpretation |
|---|---:|---|
| PARITY | 10 | Source behavior is materially preserved. |
| CODEX_NATIVE | 5 | Product-specific behavior is rebuilt using supported Codex mechanisms. |
| EXTENSION | 14 | Stronger target behavior must be retained. |
| GAP | 10 | Required current-source behavior is absent in the merged target. |
| PARTIAL | 13 | Some behavior exists, but enforcement, proof, or current detail is incomplete. |
| NON_PORTABLE | 4 | Exact source behavior is product-specific or unsafe to copy. |
| UNKNOWN | 5 | Current primary evidence cannot support an architecture claim; a spike or explicit decision gate exists. |
| **Total** | **61** | Every row contains paths, enforcement, difference, evidence, limitation, and disposition. |

## Proposed execution architecture

The durable hierarchy stays in GitHub:

```text
Project conductor
  -> sibling phase Epic conductors
     -> Task supervisor with one authoritative Plan
        -> one isolated PR worker per worktree/branch/PR/ownership lease
        -> bounded read-only auditors and reviewers
```

Codex thread nesting is transport, not authority. Stable Multi-Agent V2 can
spawn descendants, but [ordinary agents share the same CWD and filesystem](https://github.com/openai/codex/blob/3ba0f711642a888aec92a611a3f3b2211157ff89/codex-rs/core/src/session/multi_agents.rs#L53-L58).
A writing worker therefore requires an explicit desktop managed worktree,
permanent isolated worktree, cloud container with proven branch semantics, or a
provider-neutral equivalent. An ordinary subagent cannot be promoted to writer
merely because it is a different thread.

Each dispatch and release is durable. Replacement waits for a proven stop or
human adjudication; timeout or vanished UI state does not release ownership.
A small Task can avoid a separate worker only when the pre-commit Plan contains
the exact no-worker declaration. A Task owning no files and performing only
read-only acceptance may complete by Issue Outcome/Evidence without a fake PR.

See [ADR-0005](../agreements/adr/ADR-0005-codex-reconstruction-execution-model.md).

## Highest-priority gaps

| Ledger | Current difference | Planned authority |
|---|---|---|
| CAP-007 | No active Task-supervisor to isolated per-PR-worker split. | [Phase #61](https://github.com/mochan-tk/ttt1-codex/issues/61) |
| CAP-008, CAP-020 | No durable dispatch/release/successor identity or validator. | [Phases #61-#63](https://github.com/mochan-tk/ttt1-codex/issues/61) |
| CAP-009 | No pre-commit small-Task exemption in the current sole-writer model. | [Phase #61](https://github.com/mochan-tk/ttt1-codex/issues/61) |
| CAP-013 | Ordinary Codex subagents share a checkout; writing workers need explicit isolation. | [Spike #73](https://github.com/mochan-tk/ttt1-codex/issues/73), [Phase #62](https://github.com/mochan-tk/ttt1-codex/issues/62) |
| CAP-026 | No ownership-overlap sensor. | [Phase #63](https://github.com/mochan-tk/ttt1-codex/issues/63) |
| CAP-027 | No governance manifest/drift sensor. | [Phase #63](https://github.com/mochan-tk/ttt1-codex/issues/63) |
| CAP-028 | No reusable GET-only effective-governance sensor. | [Phase #63](https://github.com/mochan-tk/ttt1-codex/issues/63) |
| CAP-045 | No general Windows Git Bash launcher. | [Phase #64](https://github.com/mochan-tk/ttt1-codex/issues/64) |
| CAP-049 | No pinned official Codex capability drift baseline. | [Phase #64](https://github.com/mochan-tk/ttt1-codex/issues/64) |
| CAP-035 | Current active ruleset requires no status checks. | Existing [Task #52](https://github.com/mochan-tk/ttt1-codex/issues/52) and [Phase #63](https://github.com/mochan-tk/ttt1-codex/issues/63) |

## Retained target extensions

| Ledger | Extension that must not regress | Current proof boundary |
|---|---|---|
| CAP-019 | Immutable Plan/edit history and Plan-before-first-commit chronology. | Merged validator/tests; worker dispatch still missing. |
| CAP-021 | Comment create/edit/delete reruns and base-owned ritual evaluation. | Merged design/tests; complete actor/worker authentication missing. |
| CAP-029 | Exact source-bound, disabled-only, no-update ruleset proposal. | Merged helper/tests; no live proposal. |
| CAP-032 | Base-owned admission, exact PR/repository/SHA/files/rename/digest revalidation, bootstrap denial. | Merged workflow/tests; same-repo accepted path #50 incomplete. |
| CAP-033 | Public-fork exact authorization, revocation, and cancellation. | Merged workflow/tests; hosted proof #51 incomplete. |
| CAP-034 | Exact-head preflight/publisher, fixed result mapping, newer-run ownership, fail-closed rollback. | Failure publication observed; successful trusted-source proof incomplete. |
| CAP-037 | Inactive Codex-owned secure Dev Container boundary and adopter collision refusal. | Accepted agreement; implementation/runtime #33 frozen. |
| CAP-043 | Privacy-minimized, consent-gated feedback and no-checkout receiver. | Deterministic fixtures; live label setup incomplete. |
| CAP-044 | Immutable provenance, collision/symlink refusal, stage-only install, adopter-truth-preserving upgrade. | Deterministic fixtures; live adoption/native Windows unproved. |
| CAP-047 | Skills-only plugin with canonical byte/mode sync and safe partial-install degradation. | Static artifact/tests; publication/install/use unproved. |
| CAP-050 | Explicit preview/apply and fail-closed setup helpers. | Fixtures; target live setup incomplete. |
| CAP-052 | Kit-development/adopter-truth namespace separation. | Target design/installer; source currently regresses this boundary. |
| CAP-053 | Broad Codex/plugin/installer/action-pin/permission guard wall. | Merged tests; active ruleset does not require statuses. |
| CAP-060 | Explicit refusal to infer external product/release state from repository fixtures. | Agreement/documentation; no release evidence exists. |

The existing secure Dev Container and admission proof chain remains authoritative:
[#33](https://github.com/mochan-tk/ttt1-codex/issues/33),
[#49](https://github.com/mochan-tk/ttt1-codex/issues/49),
[#50](https://github.com/mochan-tk/ttt1-codex/issues/50),
[#51](https://github.com/mochan-tk/ttt1-codex/issues/51), and
[#52](https://github.com/mochan-tk/ttt1-codex/issues/52).
The new governance phase is blocked by #33. Release-readiness phase #65 is also
blocked by existing release Epic #40.

## UNKNOWN register

| Ledger | UNKNOWN | Required evidence |
|---|---|---|
| CAP-014 | Stable parent/ancestor identity and lifecycle authority. | [#72](https://github.com/mochan-tk/ttt1-codex/issues/72) |
| CAP-015 | V2 depth, concurrency, queueing, budget, heartbeat, and status limits. | [#72](https://github.com/mochan-tk/ttt1-codex/issues/72), [#78](https://github.com/mochan-tk/ttt1-codex/issues/78) |
| CAP-017 | Failure, interruption, parent termination, partial writes, and orphan propagation. | [#75](https://github.com/mochan-tk/ttt1-codex/issues/75), [#76](https://github.com/mochan-tk/ttt1-codex/issues/76) |
| CAP-048 | Plugin publication, install/update/rollback, and cross-surface behavior. | [#77](https://github.com/mochan-tk/ttt1-codex/issues/77) |
| CAP-061 | Source stacked/multi-PR activation: its `#89` gate resolves to an unrelated closed PR, so activation is not proved. | [#71](https://github.com/mochan-tk/ttt1-codex/issues/71), then a later human agreement and [Phase #61](https://github.com/mochan-tk/ttt1-codex/issues/61) |

Runtime Tasks [#72](https://github.com/mochan-tk/ttt1-codex/issues/72)
through [#78](https://github.com/mochan-tk/ttt1-codex/issues/78) are detailed,
blocked, disjoint, and not ready.

## NON_PORTABLE register

| Ledger | Source surface | Rationale |
|---|---|---|
| CAP-024 | Copilot Rubber Duck | No evidenced named one-to-one Codex product feature; use normal steering/reviewer roles without claiming equivalence. |
| CAP-036 | Source .devcontainer payload | Copilot extensions, mutable components, and adopter-owned namespace conflict with the Codex secure boundary. |
| CAP-041 | VS Code Playwright MCP | Unpinned, editor-specific, non-distributed, and unsafe as generic project configuration. |
| CAP-054 | Copilot setup workflow | Reserved Copilot cloud lifecycle has no Codex compatibility contract. |

Copilot instructions, agents, prompts, and skills are not copied. They are
represented as CODEX_NATIVE AGENTS.md, .agents/skills, .codex/agents, and
portable configuration.

## Source limitations deliberately not copied

- The Task ritual does not authenticate runtime session IDs and its open
  [Issue #6](https://github.com/mochan-tk/agentic-dev-kit-for-copilot/issues/6)
  records comment-authenticity/freshness risk.
- Source .github adopter namespaces now contain source-specific ADR/context
  records that the installer distributes, contradicting the documented
  namespace boundary.
- One public raw plugin spike contains a personal local-path example; this map
  does not reproduce it.
- Two source provenance files declare internal sensitivity while stored in a
  public repository.
- Source onboarding still invokes a legacy no-profile ruleset flow.
- Source README no longer carries the detailed governance commands claimed by
  its recent changelog.
- Source run.ps1 has Windows evidence; scaffold-init.ps1 does not.
- Source stacked/multi-PR mechanics are explicitly off pending `#89`, but the
  live `#89` is an unrelated closed, unmerged governance PR; activation remains
  UNKNOWN and is not copied.
- Plugin activation/update/cross-surface claims remain partial/no-go evidence,
  not accepted product capability.

## Rolling-wave graph

| Phase | Epic | State |
|---:|---|---|
| 1 | [#58](https://github.com/mochan-tk/ttt1-codex/issues/58) | Decomposed into #59 and read-only acceptance #66-#71. |
| 2 | [#60](https://github.com/mochan-tk/ttt1-codex/issues/60) | Decomposed into not-ready runtime spikes #72-#78; blocked by #58. |
| 3 | [#61](https://github.com/mochan-tk/ttt1-codex/issues/61) | Coarse supervisor/worker phase; blocked by #60. |
| 4 | [#62](https://github.com/mochan-tk/ttt1-codex/issues/62) | Coarse provider-neutral isolation/replacement phase; blocked by #61. |
| 5 | [#63](https://github.com/mochan-tk/ttt1-codex/issues/63) | Coarse ritual/governance/CI phase; blocked by #62 and existing #33. |
| 6 | [#64](https://github.com/mochan-tk/ttt1-codex/issues/64) | Coarse onboarding/distribution phase; blocked by #63. |
| 7 | [#65](https://github.com/mochan-tk/ttt1-codex/issues/65) | Coarse live/release-readiness phase; blocked by #64 and existing #40. |

Only Planning Task #59 is ready. No implementation or runtime spike is ready.

## Historical 110-file compatibility appendix — superseded

This appendix preserves exact historical assertions consumed by the existing
target test_runtime_parity.py, which is outside Task #59 ownership. It is not
the current audit, does not supersede the 135-file inventory above, and must be
removed or revised only by a separately owned synchronization Task.

Historical source pin:
20637b703cbde6abd8934fc222abbe6c82bb4568.

An earlier PR #37 authority also used the 110-file source pin
f466c7e169243e2bea03b4b33a20f8c557328d96. It is preserved as lineage under
superseded REQ-037; the 20637b appendix remains solely because the current
semantic regression test asserts it. Neither pin is the current 135-file audit.

| Historical source area | Historical tracked files | Historical disposition |
|---|---:|---|
| Root controls and distribution metadata | 6 | Historical only. |
| `.github/**` | 85 | Historical only. |
| `docs/**` | 15 | Historical only. |
| `.devcontainer/**` | 3 | Historical only. |
| `.vscode/mcp.json` | 1 | Historical only. |
| **Total** | **110** | Superseded by the current 135-file authority. |

Historical behavior delta
[75a457dd5439b3d43fcc925881650b7bc4705b77](https://github.com/mochan-tk/agentic-dev-kit-for-copilot/commit/75a457dd5439b3d43fcc925881650b7bc4705b77)
was described as gated cloud CI diagnosis and recorded action_required as an
organization Actions approval boundary rather than passing CI.

Historical pin 20637b703cbde6abd8934fc222abbe6c82bb4568 was described as a
program session above Epic sessions coordinating sibling Epic parents.

Historical deferred-boundary wording retained solely for the test contract:
setup-ruleset was “Deferred to Task #35” and “not claimed source-equivalent”;
Task #33 was also open. Neither open Task was implementation evidence. Task #35
is now closed and later admission work is merged/partially proved, so those
sentences are not current-state claims.

The follow-up synchronization must change the stale deterministic test and this
appendix together. Task #59 does not weaken or bypass the test.
