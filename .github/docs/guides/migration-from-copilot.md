# Migration from the Copilot kit

Migrate capability by capability. Do not run a global `Copilot` to `Codex`
text replacement.

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

## 4. Re-route Tasks

Keep the four `exec:*` labels if they remain useful, but interpret them as
Codex cloud, app, CLI, and IDE. Replace Copilot assignment and session commands
with the current Codex task/thread or subagent mechanism available on the
chosen surface. Keep the Task Issue as the work order and the PR as the change
artifact.

## 5. Re-measure setup

Use `$project-onboarding` after the agreement merge. Run the real commands,
replace stale Copilot setup assumptions, confirm all required criteria can run
on their routed surface, and repeat the license trial. Do not carry an old
autonomy claim across an execution-platform migration.

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
