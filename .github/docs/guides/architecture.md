# Architecture

The kit separates durable control from agent execution.

```text
GitHub control plane
  Issues + comments + dependencies  -> work order, plan, frontier, outcome
  PRs + reviews + CODEOWNERS        -> change, Evidence, Three Merges
  Actions + rulesets + checks       -> deterministic enforcement
                 |
                 v
Codex execution plane
  AGENTS.md                         -> small always-on constitution
  .agents/skills/                   -> nine on-demand workflows
  .codex/agents/                    -> four agents with read-only defaults
  .codex/config.toml                -> portable trusted-project settings
  Codex tools / connectors / gh CLI -> bounded access to the control plane
```

Session messages, internal plans, Projects views, and local scratch state are
caches. A fresh Codex session must be able to reconstruct the work from Git,
the Task Issue, its comments, the PR, and checks.

The Codex-native session hierarchy mirrors the two-level Issue graph:

```text
Program session (whole project; conductor of conductors)
  +-- Epic-parent session: phase A ---- sole-writer Task session ---- read-only subagent(s)
  +-- Epic-parent session: phase B ---- sole-writer Task session ---- read-only subagent(s)
  +-- Epic-parent session: phase C ---- sole-writer Task session ---- read-only subagent(s)
```

Phase Epics are siblings ordered by `blocked-by`. The program starts or wakes
Epic parents and replans across phases, but never decomposes or dispatches
Tasks. Each Epic parent decomposes just in time, dispatches its Task frontier,
steers, and verifies. The literal contract remains
`1 Task = 1 session = 1 worktree = 1 branch = 1 PR`: that Task session is the
sole implementing writer. It may delegate only independent parallel read-only
exploration, review, or test observation to Codex subagents. They receive no
File ownership and make no edits. Reports climb one hop, parents independently
verify ground truth, and completed threads close leaf first. No Epic parent
recursively spawns its successor.

## Instruction and workflow layering

Codex reads root-to-working-directory `AGENTS.md` files. The root file carries
only invariants needed for most work; an adopter may add a nested `AGENTS.md`
near a governed subtree. Long procedures belong in skills, detailed rationale
in agreements, and Task-specific facts in the Task Issue.

The nine skills implement the lifecycle:

1. `context-collection`
2. `context-distillation`
3. `project-onboarding`
4. `plan-management`
5. `task-routing`
6. `session-orchestration`
7. `verification`
8. `retro`
9. `codex-automation`

The bundled `explorer`, `planner`, `orchestrator`, and `reviewer` agents use
read-only defaults plus explicit no-write instructions. Parent and user runtime
overrides remain authoritative, so this is a safe default rather than a hard
security boundary. Codex reapplies the parent permission mode and live runtime
overrides when spawning a child. The project custom agent named `explorer`
intentionally takes precedence over the built-in `explorer`. Implementation
remains in the owning Codex Task. See the
[official subagent behavior](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Distribution boundaries

| Distribution | Includes | Excludes |
|---|---|---|
| GitHub template | Entire tracked repository | User credentials and external settings |
| `scaffold-init` | GitHub control plane, canonical skills, bundled agents/config, constitution, lineage, kit-scoped license/notice | Application README/license, plugin copy, editor config, frozen optional Dev Container |
| Plugin artifact | Nine synchronized skills plus license/notice | GitHub controls, agents, repo config, installer, settings; skills degrade to read-only/draft guidance when these controls are absent |

## Native capability boundaries

- **Hooks:** executable trusted-repository configuration. None is active by
  default. Add `.codex/hooks.json` only through a reviewed project Task. Only
  `type: "command"` handlers execute today; `prompt` and `agent` are parsed but
  skipped. Recheck the [official Hooks schema](https://learn.chatgpt.com/docs/hooks).
- **MCP:** external tool configuration belongs in `.codex/config.toml` only
  when portable. Secrets and private endpoints stay in managed environment or
  organization policy.
- **Scheduled tasks:** schedules are product state, not fake repository files.
  Web and desktop manage them; only desktop can use a local project/worktree,
  while CLI and IDE provide no Scheduled management UI. Their prompt must
  re-read the ledger and include a stop condition. See
  [Scheduled tasks](https://learn.chatgpt.com/docs/automations).
- **Codex GitHub Action:** optional and secret-bearing. The default kit does
  not enable it; deterministic Actions remain sufficient for the base
  scaffold.
- **Plugins:** package reusable capabilities. A skills-only plugin cannot
  install repository governance and never claims to do so.
- **Cloud Tasks and CI:** cloud execution result, branch/PR state, and PR
  workflows are separate evidence lanes. `action_required` can be an
  organization Actions approval boundary; it does not prove cloud execution
  failed and it does not satisfy required checks.

## Safety properties

- One Task, session, worktree, branch, PR, and active writer.
- Exact approval only for high-risk plans; ordinary work uses lazy consensus.
- Deterministic measures precede implementation.
- Setup helpers changed here require explicit authority; their previews do not
  write. The frozen ruleset admission boundary remains outside this change.
- Installer collisions and symlink ancestors fail closed.
- External Actions use full commit pins and checkout credentials are not
  persisted.
- Credentials, PII, controlled data, personal paths, model pins, and private
  endpoints are absent from the generic distribution.

The capability trace is pinned to the 110-file Copilot source at
`20637b703cbde6abd8934fc222abbe6c82bb4568`. Task #33 still owns optional
Dev Container runtime evidence and Task #35 still owns ruleset admission; the
architecture does not infer completion from their drafts or previews.
