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
security boundary. Implementation remains in the owning Codex task.

## Distribution boundaries

| Distribution | Includes | Excludes |
|---|---|---|
| GitHub template | Entire tracked repository | User credentials and external settings |
| `scaffold-init` | GitHub control plane, canonical skills, bundled agents/config, constitution, lineage, kit-scoped license/notice | Application README/license, plugin copy, editor config, frozen optional Dev Container |
| Plugin artifact | Nine synchronized skills plus license/notice | GitHub controls, agents, repo config, installer, settings |

## Native capability boundaries

- **Hooks:** executable trusted-repository configuration. None is active by
  default. Add `.codex/hooks.json` only through a reviewed project Task.
- **MCP:** external tool configuration belongs in `.codex/config.toml` only
  when portable. Secrets and private endpoints stay in managed environment or
  organization policy.
- **App automations:** schedules and recurring tasks are app state, not fake
  repository files. Their prompt must re-read the ledger and include a stop
  condition.
- **Codex GitHub Action:** optional and secret-bearing. The default kit does
  not enable it; deterministic Actions remain sufficient for the base
  scaffold.
- **Plugins:** package reusable capabilities. A skills-only plugin cannot
  install repository governance and never claims to do so.

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
