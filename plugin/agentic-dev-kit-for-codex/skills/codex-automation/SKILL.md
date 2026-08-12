---
name: codex-automation
description: Designs supported Codex Scheduled tasks, repository hooks, MCP connections, and optional GitHub Action integrations with least privilege and an explicit human trust boundary. Use when a recurring task, event-driven check, external tool connection, scheduled monitor, repo-local hook, or Codex Action is requested or when an existing automation must be audited, migrated, or disabled.
---

# Codex Automation

Choose the smallest supported mechanism that produces the requested outcome.
Automations are conveniences around the durable GitHub ledger; they never
replace the Task work order, evidence, required checks, or a human merge.

## Classify the trigger

| Need | Codex-native mechanism | Durable repository artifact |
|---|---|---|
| Repeated or scheduled user task | Scheduled task | Document the purpose and owner in the originating Issue; the schedule itself is product state. |
| Deterministic command before or after a Codex tool event | Repository hook | `.codex/hooks.json`, only after the repository is trusted and the exact command is reviewed. |
| Read or act in an external service | MCP server or connected app | Project-safe MCP metadata in `.codex/config.toml`; credentials stay outside Git. |
| Reusable multi-step agent procedure | Repository skill | `.agents/skills/<name>/SKILL.md` and optional resources. |
| Focused delegation with a read-only default | Custom subagent | `.codex/agents/<name>.toml`. |
| Pull-request analysis in GitHub Actions | `openai/codex-action` | A separately reviewed workflow with pinned dependencies, minimal permissions, and an explicit secret boundary. |

Do not invent a repository file for a Scheduled task. Do not emulate an
unsupported lifecycle event with a polling shell process. If the current Codex
surface does not expose the required mechanism, state the limitation and offer
the closest safe manual workflow.

## Detect the distribution boundary

Check for the root constitution, Task/PR controls, and the project `.codex/`
layer before proposing activation. A skills-only plugin cannot install those
surfaces. If they are absent, list what is missing and return a read-only
design or draft configuration only. Do not fabricate a Task gate, trusted
project, hook path, MCP policy, Scheduled task, secret, or GitHub workflow, and
do not claim a live control exists. Any external or repository write requires
every missing control to be restored and verified first, then
separate explicit authority on its owning surface.

## Choose the Scheduled task surface

Use the current product term **Scheduled tasks**:

- ChatGPT web and the desktop app can create and manage Scheduled tasks from a
  ChatGPT or Codex chat when the workspace has the feature.
- Only the desktop app can run a Scheduled task against a local project or an
  isolated local worktree. The computer must remain on, the app must remain
  running, and the selected project must still exist on disk.
- Web Scheduled tasks can use uploaded context and connected tools, but cannot
  work directly in a local folder.
- Codex CLI and the IDE extension have no Scheduled management interface. They
  may prepare and manually test the prompt, skill, or script; use web or the
  desktop app to create and manage the schedule.

See the [official Scheduled tasks documentation](https://learn.chatgpt.com/docs/automations).

## Design before enabling

1. Read the Task, applicable agreements, `AGENTS.md`, and existing `.codex/`
   configuration. Identify who owns the trigger and who can disable it.
2. Define the event, inputs, output, retry budget, timeout, idempotency key,
   failure destination, and evidence. A recurring write must be safe to run
   twice.
3. Classify every permission and secret. Prefer read-only access. Keep tokens,
   credentials, personal paths, and private endpoints out of committed files.
4. Preview the exact mutation. Creating or changing a Scheduled task,
   repository setting, secret, external record, or schedule requires explicit
   user authority; inspection does not.
5. Add a deterministic validator or dry-run when the repository owns the
   configuration. Never depend on an agent instruction to enforce a property
   that a check can prove.
6. Test the success path, a denied/absent-credential path, a repeated event,
   and the disable or rollback path. Record fresh evidence on the Task.

Load [references/supported-patterns.md](references/supported-patterns.md) when
implementing hooks, MCP, Actions, or Scheduled tasks.

## Hook rules

- Treat `.codex/hooks.json` as executable repository content. Add it only when
  the hook is essential, deterministic, bounded, and safe for every trusted
  contributor who opens the project.
- Pin or use repository-owned commands. Reject shell interpolation of
  untrusted event text; pass values as structured arguments or environment
  variables supported by the hook contract.
- A hook may report or block a local action, but it may not silently approve,
  merge, push, alter GitHub settings, or exfiltrate repository content.
- Keep optional examples outside the discovery path. Copy one into
  `.codex/hooks.json` only through a reviewed project-specific Task.
- Only `type: "command"` hook handlers execute today. `prompt` and `agent`
  handlers are parsed but skipped, so never design a control that depends
  on them. Recheck the [official Hooks documentation](https://learn.chatgpt.com/docs/hooks)
  before adopting a later handler type.

## MCP and connected-service rules

- Prefer a user- or organization-managed connector when one already exists.
- Commit only portable server identity and startup configuration. Use
  environment-variable references for secrets and document the variable name,
  required scope, and failure behavior without recording a value.
- Pin package versions or immutable artifacts where the transport permits it.
- Start with the narrowest tool allowlist and read-only operations. Require a
  fresh user decision before enabling external writes.
- Record source provenance when material is imported through MCP and apply the
  `$context-collection` sensitivity rules.

## Automation handoff

Return the chosen mechanism, trigger, owner, permissions, secret locations,
idempotency behavior, verification evidence, disable procedure, and remaining
manual boundary. If the user asked to create a Scheduled task, use a supported
web or desktop surface only after the schedule, time zone, local-project need,
and destination chat are unambiguous.
