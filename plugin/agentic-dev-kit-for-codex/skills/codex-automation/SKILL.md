---
name: codex-automation
description: Designs supported Codex automations, repository hooks, MCP connections, and optional GitHub Action integrations with least privilege and an explicit human trust boundary. Use when a recurring task, event-driven check, external tool connection, scheduled monitor, repo-local hook, or Codex Action is requested or when an existing automation must be audited, migrated, or disabled.
---

# Codex Automation

Choose the smallest supported mechanism that produces the requested outcome.
Automations are conveniences around the durable GitHub ledger; they never
replace the Task work order, evidence, required checks, or a human merge.

## Classify the trigger

| Need | Codex-native mechanism | Durable repository artifact |
|---|---|---|
| Repeated or scheduled user task | Codex app automation | Document the purpose and owner in the originating Issue; the schedule itself is app state. |
| Deterministic command before or after a Codex tool event | Repository hook | `.codex/hooks.json`, only after the repository is trusted and the exact command is reviewed. |
| Read or act in an external service | MCP server or connected app | Project-safe MCP metadata in `.codex/config.toml`; credentials stay outside Git. |
| Reusable multi-step agent procedure | Repository skill | `.agents/skills/<name>/SKILL.md` and optional resources. |
| Focused delegation with a read-only default | Custom subagent | `.codex/agents/<name>.toml`. |
| Pull-request analysis in GitHub Actions | `openai/codex-action` | A separately reviewed workflow with pinned dependencies, minimal permissions, and an explicit secret boundary. |

Do not invent a repository file for an app automation. Do not emulate an
unsupported lifecycle event with a polling shell process. If the current Codex
surface does not expose the required mechanism, state the limitation and offer
the closest safe manual workflow.

## Design before enabling

1. Read the Task, applicable agreements, `AGENTS.md`, and existing `.codex/`
   configuration. Identify who owns the trigger and who can disable it.
2. Define the event, inputs, output, retry budget, timeout, idempotency key,
   failure destination, and evidence. A recurring write must be safe to run
   twice.
3. Classify every permission and secret. Prefer read-only access. Keep tokens,
   credentials, personal paths, and private endpoints out of committed files.
4. Preview the exact mutation. Creating or changing an app automation,
   repository setting, secret, external record, or schedule requires explicit
   user authority; inspection does not.
5. Add a deterministic validator or dry-run when the repository owns the
   configuration. Never depend on an agent instruction to enforce a property
   that a check can prove.
6. Test the success path, a denied/absent-credential path, a repeated event,
   and the disable or rollback path. Record fresh evidence on the Task.

Load [references/supported-patterns.md](references/supported-patterns.md) when
implementing hooks, MCP, Actions, or app automations.

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
manual boundary. If the user asked to create a schedule, use the Codex app's
automation capability only after the schedule and time zone are unambiguous.
