# Copilot source to Codex capability map

Source audited: [`mochan-tk/agentic-dev-kit-for-copilot`](https://github.com/mochan-tk/agentic-dev-kit-for-copilot)
at [`20637b703cbde6abd8934fc222abbe6c82bb4568`](https://github.com/mochan-tk/agentic-dev-kit-for-copilot/tree/20637b703cbde6abd8934fc222abbe6c82bb4568)
(110 tracked files).
The mapping preserves intent, not product-specific filenames.

## Audited inventory closure

| Source area | Tracked files | Disposition in this map |
|---|---:|---|
| Root controls and distribution metadata | 6 | Constitution, README/lineage, license, ignore, and line-ending policy are covered below. |
| `.github/**` | 85 | Skills, agents, prompts, instructions, workflows, scripts, forms, templates, connectors, and development records are covered by the surface, lifecycle, script, and workflow tables. |
| `docs/**` | 15 | Source design/development records are summarized into the target agreements, ADR, migration guide, and this pinned audit instead of being installed as adopter truth. |
| `.devcontainer/**` | 3 | Explicitly deferred to the isolated frozen Task; no uncommitted file is copied. |
| `.vscode/mcp.json` | 1 | Explicit non-port rationale appears in the surface table. |
| **Total** | **110** | Every tracked source file belongs to one of these audited areas. |

The file count and area totals are unchanged from the prior audit, but the
behavior is not. These two source changes after the prior pinned baseline are
traced explicitly:

| Source change | Codex-native disposition |
|---|---|
| [`75a457d`](https://github.com/mochan-tk/agentic-dev-kit-for-copilot/commit/75a457dd5439b3d43fcc925881650b7bc4705b77) — gated cloud CI diagnosis | `$session-orchestration` independently inspects the Codex cloud Task, branch/PR result, and PR workflows. `action_required` is recorded as a possible organization Actions approval boundary: it is neither proof the Task failed nor passing CI. |
| [`20637b7`](https://github.com/mochan-tk/agentic-dev-kit-for-copilot/commit/20637b703cbde6abd8934fc222abbe6c82bb4568) — program session above Epic sessions | `$session-orchestration`, `$plan-management`, `.codex/agents/orchestrator.toml`, and the architecture guide define one program conductor over sibling Epic parents without recursive successor nesting. |

## Repository and agent-facing surfaces

| Copilot source element | Codex implementation | Status and rationale |
|---|---|---|
| Root `AGENTS.md` | Root `AGENTS.md` | Preserved and strengthened as the durable constitution. |
| `.github/copilot-instructions.md` | `AGENTS.md`, agreements, and focused skills | Rebuilt; Codex does not read Copilot always-on instructions. |
| `.github/instructions/*.instructions.md` | Nested `AGENTS.md` when an adopter needs path scope; otherwise agreements/skills | Rebuilt as a supported Codex layering rule; sample firmware assumptions are not forced on adopters. |
| Three `.github/agents/*.agent.md` | `.codex/agents/{orchestrator,planner,reviewer}.toml` | Rebuilt in current custom-agent format with read-only defaults and no-write instructions; the orchestrator now separates program and Epic-parent authority. Parent permission mode and live runtime overrides remain authoritative. |
| Repository exploration embedded in agents | `.codex/agents/explorer.toml` | Added as a fourth role with the same read-only default. Its project-scoped name intentionally shadows Codex's built-in `explorer`. |
| Seven `.github/prompts/*.prompt.md` | Skill invocation and `agents/openai.yaml` starter prompts | Rebuilt; deprecated prompt files are intentionally absent. |
| Project-onboarding skill landing, label bootstrap, source activation, measurement, evidence, and P6 handoff | `$project-onboarding`, `setup-labels.sh`, and `setup-sources.sh` | Rebuilt with preview/consent boundaries plus a durable `Deferred from onboarding` ledger, evidence-PR `## Next steps`, and first-phase Epic pointer. Chat is not the carrier. |
| Other seven `.github/skills/**` workflows | Seven `.agents/skills/**` counterparts | Rebuilt in the Codex discovery location with stricter metadata. |
| No Copilot automation-design skill | `.agents/skills/codex-automation/**` | Added to cover current Hooks, MCP, Scheduled tasks, plugins, and optional Action boundaries without activating generic product state. |
| `.vscode/mcp.json` with Playwright | Project-specific `.codex/config.toml` after review | Not copied: the source used an unpinned package and its installer did not distribute the file. No generic endpoint or credential is invented. |
| `.devcontainer/**` with Copilot extensions | Separately owned optional `.codex/devcontainer/**` Task | Deferred and isolated; the frozen Task is not copied or modified by this reconstruction. |

## GitHub control plane and lifecycle

| Source capability | Codex location | Status |
|---|---|---|
| Epic and AI Task Issue forms | `.github/ISSUE_TEMPLATE/{epic,task}.yml` | Preserved; Task form uses Codex roles/surfaces. |
| Adopter feedback form | `.github/ISSUE_TEMPLATE/feedback.yml` | Preserved with target terminology. |
| Blank Issue disabled | `.github/ISSUE_TEMPLATE/config.yml` | Preserved. |
| PR evidence template | `.github/PULL_REQUEST_TEMPLATE.md` | Preserved and strengthened with plan/outcome authority. |
| CODEOWNERS | `.github/CODEOWNERS` | Preserved as a project-tuned review wall. |
| Dependabot for Actions | `.github/dependabot.yml` | Preserved. |
| Context contract/connectors | `.github/connectors/**` | Ported without stale Copilot prompts or non-distributed design links. |
| Builtin and spec-kit sources | `builtin.md`, `speckit.md`, `setup-sources.sh` | Ported; preview is local/read-only, activation is a reviewed PR. |
| Agreement/context templates | `.github/docs/agreements/**`, `.github/docs/context/**` | Existing Codex version retained; source-only development records are summarized, not shipped as false project truth. |
| Three Merges | README, `AGENTS.md`, skills, templates | Preserved. |
| Rolling Issue graph/frontier | `$plan-management`, `frontier.sh`, `new-task.sh` | Preserved and strengthened: one phase per sibling Epic, `blocked-by` phase order, just-in-time Task waves, and one current decomposition-state line. Live Issue creation requires verified prerequisites and explicit `--apply`. |
| Routing across cloud/app/CLI/IDE | `$task-routing` and Task form | Rebuilt for Codex surfaces without model-name pins. |
| Program/Epic/Task orchestration | `$session-orchestration` and `.codex/agents/orchestrator.toml` | Rebuilt without changing REQ-018: one sole-writer Task session may use bounded subagents only for independent parallel read-only exploration, review, or test observation. One-hop reports, parent ground-truth checks, steer/stop/close controls, leaf-first teardown, and sibling Epic parents live under one program conductor. |
| Layered verification | `$verification`, CI, reviewer | Preserved; agent self-report is never Evidence. |
| Retro hygiene | `$retro`, `retro-hygiene.sh/.yml` | Preserved with report-only defaults and explicit Issue creation. |

## Source scripts

| Copilot source script | Codex result |
|---|---|
| `scaffold-init.sh`, `scaffold-init.ps1` | Ported for Codex paths, source repo, upgrade ownership, provenance, stage-only behavior, and Codex handoff. |
| `setup-labels.sh` | Retained with Codex labels and explicit `--apply`. |
| `setup-project.sh` | Retained with explicit `--apply`; Projects remains a derived view. |
| `setup-ruleset.sh` | **Deferred to Task #35.** The target helper remains unchanged by this parity Task and is not claimed source-equivalent. Its required-check source binding, admission tests, live settings evidence, and human enablement remain outstanding; only its documented `--dry-run` path is eligible meanwhile. |
| `setup-sources.sh` | Ported; no-network dry-run and explicit local write. |
| `frontier.sh`, `new-task.sh` | Retained under the `plan-management` skill. |
| `tuning-status.sh` | Retained as the visible onboarding gate. |
| `check-action-pins.sh` | Existing Python `check_action_pins.py` retained and expanded to all tracked workflows. |
| `check-task-ritual.sh` | Existing Python `check_task_ritual.py` retained; its chronology and immutability checks are stronger. |
| `check-copilot-surface.sh` | Replaced by `check-skills.sh` plus plugin synchronization and native TOML/YAML validation. |
| `check-connectors.sh` | Ported. |
| `check-template-sync.sh` | Existing stricter target implementation retained. |
| `check-md-links.sh` | Existing target implementation retained and expanded to guides, connectors, plugin, README, and changelog. |
| `check-changelog-refs.sh` | Ported as a deterministic lineage reference guard. |
| `check-escalation-wording.sh` | Ported to keep the failure-count source singular. |
| `check-workflow-permissions.sh` | Ported to enforce job-level checkout permissions. |
| `feedback-lib.sh` | Ported with the fixed allowlist and consent gate; target docs do not reuse the source ADR number. |
| Source shell regression suites | Target Python/Bash guards plus installer fixtures | Rebuilt around deterministic target behavior, including `test_runtime_parity.py`; no target test result is treated as Task #35 admission evidence or Task #33 runtime evidence. |

## Workflows and distribution

| Source element | Codex result | Rationale |
|---|---|---|
| `ci.yml` | Existing target CI discovers Codex, connector, installer, permission, plugin, and runtime-parity checks | Preserved target wall; it does not establish the separately owned source-bound ruleset admission contract in Task #35. |
| `retro-hygiene.yml` | Existing Codex workflow | Preserved. |
| `adopter-feedback.yml` | Ported | Marker classification needs no checkout and only `issues: write`. |
| `copilot-setup-steps.yml` | No compatibility workflow | Codex setup is measured per repository; no Copilot-reserved job or placeholder is valid. |
| Template copy distribution | GitHub template | Preserved. |
| Safe existing-repo installation | `scaffold-init` | Preserved and extended to Codex discovery paths. |
| No source plugin | Valid skills-only plugin artifact | Added with byte-identical skills and safe degradation when full-kit GitHub controls are absent; publication remains external. |
| MIT `LICENSE` | Existing MIT license plus `NOTICE.md` attribution | Preserved. |
| Root source development records | This map (including its pinned audit inventory), migration guide, and ADR | Summarized; no separate source-audit artifact or old issue-number narrative is installed as adopter truth. |
| `.gitattributes`, `.gitignore`, README, changelog | Target root distribution metadata | `.gitattributes` and `.gitignore` are seed-if-absent, the kit README is template-only and adopter-owned during installation, and the changelog is always installed for lineage. |

No tracked Copilot runtime path is required for the Codex kit. Compatibility
copies are rejected by `check-skills.sh`; migration is complete only after the
Codex replacements and their deterministic checks pass.

## Current Codex product boundaries used by this map

- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
  support inspection, steering, stopping, and closing. A same-named project
  custom agent takes precedence over a built-in, and parent live permission
  overrides are reapplied when a child is spawned.
- [Scheduled tasks](https://learn.chatgpt.com/docs/automations) are managed on
  web or desktop. Only desktop can use a local project/worktree; CLI and IDE do
  not provide the Scheduled management interface.
- [Hooks](https://learn.chatgpt.com/docs/hooks) currently execute only
  `type: "command"`; `prompt` and `agent` handlers are parsed but skipped.
- [Import](https://learn.chatgpt.com/docs/import) does not list GitHub Copilot
  as a supported source. Migration from this Copilot kit is therefore manual.

The optional secure Dev Container remains deferred to Task #33. The ruleset
admission boundary remains deferred to Task #35. Neither open Task, a local
preview, nor this 110-file traceability map is completion evidence for those
capabilities.
