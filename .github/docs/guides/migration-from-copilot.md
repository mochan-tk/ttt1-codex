# Migration from the Copilot kit

Migrate capability by capability. Do not run a global `Copilot` to `Codex`
text replacement.

This is a manual migration. The official
[import flow](https://learn.chatgpt.com/docs/import) supports Claude Code and
Cursor in Codex CLI and also Claude Cowork in the desktop app; it does not list
GitHub Copilot. Do not tell adopters to use `/import` for this kit.

## 1. Preserve the ledger before changing execution files

Inventory open Epics, Tasks, dependencies, plan/outcome comments, PR closing
links, labels, CODEOWNERS, workflows, agreements, and source pins. Record the
Copilot kit version or source commit. Finish or explicitly transfer every
active writer before changing agent-facing paths.

## 2. Install on an isolated branch

Run the Codex installer with `--dry-run`. For an existing Copilot instance,
expect collisions in `.github/**` and `AGENTS.md`; use a reviewed manual merge
or a carefully inspected `--force` only when the target paths are intentionally
replaced. Never overwrite project agreements, context, workflows, or ownership
without reconciling their accepted changes.

## 3. Translate execution surfaces

| Remove after migration | Replace with |
|---|---|
| `.github/copilot-instructions.md` | Root/nested `AGENTS.md`, agreements, and skills |
| `.github/instructions/*.instructions.md` | Nested `AGENTS.md` or a focused skill |
| `.github/agents/*.agent.md` | `.codex/agents/*.toml` |
| `.github/prompts/*.prompt.md` | Explicit `$skill-name` invocation and skill metadata |
| `.github/skills/**` | `.agents/skills/**` |
| `.github/workflows/copilot-setup-steps.yml` | Measured project setup and ordinary CI |
| `.vscode/mcp.json` | Reviewed Codex MCP configuration if the connection is still required |

Do not delete a source surface until its behavior is mapped in
[`copilot-capability-map.md`](copilot-capability-map.md) and the replacement is
discoverable in a fresh Codex session.

The distributed project custom agent named `explorer` intentionally takes
precedence over Codex's built-in `explorer`, as documented in
[official subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents).
Rename the project agent before migration if the built-in behavior is desired.
Its read-only sandbox is a default; the parent permission mode and live runtime
overrides remain authoritative when Codex spawns it.

## 4. Re-route Tasks

Keep the four `exec:*` labels if they remain useful, but interpret them as
Codex cloud, app, CLI, and IDE. Replace Copilot assignment and session commands
with the current Codex task/thread or subagent mechanism available on the
chosen surface. Keep the Task Issue as the work order and the PR as the change
artifact.

Map the session hierarchy by intent, not by Copilot tool name:

- one program session conducts the sibling phase-Epic set;
- one Epic-parent session decomposes and dispatches that phase's Tasks;
- one sole-writer Task session controls its implementation, worktree, branch,
  and PR, preserving `1 Task = 1 session = 1 worktree = 1 branch = 1 PR`;
- bounded Codex subagents perform read-only exploration, review, or test
  observation only, receive no File ownership, make no edits, and report one
  hop for independent verification by the Task session.

Do not recursively spawn a successor Epic from the prior Epic parent. For
cloud work, inspect the Codex Task result, branch/PR, and workflow checks as
separate states. `action_required` can indicate an organization Actions gate;
it is not agent-failure evidence and still does not satisfy required CI.

## 5. Re-measure setup

Use `$project-onboarding` after the agreement merge. Run the real commands,
replace stale Copilot setup assumptions, confirm all required criteria can run
on their routed surface, and repeat the license trial. Do not carry an old
autonomy claim across an execution-platform migration.

Recreate product-state integrations only when still needed:

- use [Scheduled tasks](https://learn.chatgpt.com/docs/automations) on web or
  desktop; only desktop runs against a local project/worktree, while CLI and
  IDE have no Scheduled management interface;
- review Hooks against the [current schema](https://learn.chatgpt.com/docs/hooks);
  only `type: "command"` executes today, while `prompt` and `agent` handlers
  are parsed but skipped; and
- re-author MCP configuration for Codex rather than copying another client's
  file or credentials.

## 6. Verify removal and behavior

Run the full validation suite and search for remaining Copilot-only paths.
Product comparison or attribution prose may mention Copilot; runtime files may
not depend on its instruction, agent, prompt, skill, or setup conventions.

## Migrating from an earlier `ttt1-codex`

Use `scaffold-init.sh --upgrade --dry-run`. Review refreshed scripts, skills,
agents, and forms. The upgrade preserves `AGENTS.md`, `.codex/config.toml`,
workflows, CODEOWNERS, agreements, and context so local truth is never replaced
automatically. The plugin artifact is repository-only and is not installed or
refreshed by `scaffold-init`. Read `SCAFFOLD-CHANGELOG.md` and port required
changes into preserved files through dedicated review.
