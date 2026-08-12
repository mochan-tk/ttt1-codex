# ADR-0004: Codex distribution and integration boundary

- Status: accepted by the agreement merge
- Date: 2026-08-12
- Owners: repository owner and agreement reviewers
- Source baseline: `mochan-tk/agentic-dev-kit-for-copilot` at
  `f466c7e169243e2bea03b4b33a20f8c557328d96`
- Implementation baseline: PR #37, merged as
  `e47bc24092403a87239520e2f1942cc861db2b5b`

## Context

PR #37 extended the existing Codex template instead of replacing it. The
merged repository now contains a pinned 110-file source capability map, safe
template and installer paths, nine canonical repository skills, four project
custom subagents, a synchronized skills-only plugin artifact, context
connectors, consent-gated adopter feedback, supporting documentation, and
deterministic validation. It retains the stronger GitHub ledger, Three Merges,
and Task ritual that preceded the reconstruction.

Those repository artifacts do not prove every release or runtime boundary.
The plugin has not been registered, submitted, reviewed, or published through
a marketplace. No tag or GitHub release exists for this release candidate.
The installer has no recorded live adopter rollout or native Windows
end-to-end run. Connector definitions exist, but no adopter-specific source is
activated by this agreement. No repository hook, organization-specific MCP
server, Scheduled task, or secret-bearing Codex Action is enabled. Task #33's
optional secure Dev Container and Task #35's ruleset admission boundary remain
separate, open work.

Current Codex surfaces also have distinct authority boundaries:

- `AGENTS.md` is repository guidance loaded through Codex's instruction
  precedence chain.
- Skills are progressive-disclosure workflow packages. `SKILL.md` is the
  instruction entry point and `agents/openai.yaml` supplies optional interface,
  invocation, and dependency metadata.
- `.codex/agents/*.toml` defines project-scoped custom subagents. A bundled
  `sandbox_mode = "read-only"` value is a default, not an unbypassable security
  boundary: the parent turn's permission mode and live runtime overrides are
  reapplied when Codex spawns a child.
- Plugins package skills, MCP connections, or hooks for supported surfaces;
  a valid local artifact and public marketplace publication are separate
  states and decisions.
- Repository hooks are executable content that require project trust and
  review of the current hook definition before they run.
- MCP configuration belongs in user or trusted project `config.toml`; secrets
  and organization-specific endpoints do not belong in this generic template.
- Scheduled tasks are app product state, not a repository file, and run with
  the selected unattended permission boundary.

## Decision

1. Keep GitHub as the durable control, review, and enforcement plane. Codex
   guidance and integrations execute through that plane rather than replacing
   Issues, PRs, reviews, checks, rulesets, tags, or releases.
2. Retain root `AGENTS.md`, nine canonical skills under `.agents/skills/`,
   their `agents/openai.yaml` metadata, and four bundled project custom
   subagents under `.codex/agents/`. The agents use read-only defaults and
   explicit no-write instructions, while parent and user runtime policy
   remains authoritative.
3. Retain two complete repository adoption paths: GitHub template creation and
   the collision-, symlink-, and provenance-safe `scaffold-init` installer.
   The installer distributes `.github/**`, `.agents/**`, bundled
   `.codex/agents/**`, portable `.codex/config.toml`, `AGENTS.md`, and lineage,
   stages but never commits, and preserves instance truth during upgrade.
4. Retain the validated skills-only plugin under
   `plugin/agentic-dev-kit-for-codex/`. Its skill tree must remain
   byte-identical to the canonical tree. The artifact does not install GitHub
   controls, `AGENTS.md`, project custom agents, repository configuration, or
   setup helpers. Marketplace registration, submission, review, publication,
   installation, and representative live use require separate evidence.
5. Retain the checked connector contract and preview-first activation wizard.
   Connector activation and resulting data access remain adopter-specific,
   reviewed project decisions; repository conformance tests are not live
   activation evidence.
6. Retain consent-gated adopter feedback with no telemetry endpoint. It may
   offer only a fixed validated payload after an unexpected interactive
   failure, an exact public preview, and literal user consent.
7. Keep repository hooks, organization-specific MCP endpoints, Scheduled
   tasks, marketplace mutations, secret-bearing Codex Actions, and repository
   Settings disabled or absent by default. `$codex-automation` may design only
   a currently supported mechanism with least privilege, explicit authority,
   and an Issue-first review boundary.
8. Do not treat repository evidence as proof of a tag/release, archive or
   checksum, live adoption, native Windows execution, external marketplace
   state, or human decision. Record each only after it actually occurs.
9. Do not copy, activate, modify, or package `.codex/devcontainer/**`, and do
   not change `.github/scripts/setup-ruleset.sh` through this agreement. Task
   #33 and Task #35 retain their own ownership, blockers, runtime evidence, and
   human gates.

## Consequences

- Template and installer adopters can receive the full repository operating
  system; plugin adopters receive only reusable skills.
- There is one canonical skill tree under `.agents/skills/`; deterministic
  validation keeps the plugin copy synchronized, including executable modes.
- Custom-agent sandbox declarations reduce accidental write capability but do
  not override a parent or user who deliberately selects broader live runtime
  permissions.
- A repository can add hooks, MCP, Scheduled tasks, or a Codex Action later,
  but credentials, personal paths, concrete model pins, private endpoints, and
  app state remain outside generic distribution.
- Upgrades refresh kit-owned machinery while preserving agreements, context,
  workflows, CODEOWNERS, `AGENTS.md`, and `.codex/config.toml` for review.
- The Copilot source remains an attributed design origin, not a compatibility
  surface or runtime dependency.
- This text remains a proposal until its agreement PR is reviewed and merged.
  That agreement merge is distinct from a later license or completion merge;
  the executor does not perform it.

## Validation

Repository evidence must:

- compare the 110-file capability map with the pinned source commit;
- exercise installer dry-run, collision refusal, force, upgrade preservation,
  symlink refusal, dirty-source provenance, and stage-only behavior in isolated
  repositories;
- validate all canonical and packaged skills, `agents/openai.yaml`, the plugin
  manifest, custom-agent TOML, and canonical/plugin byte and mode equality;
- validate connector structure, source-preview behavior, explicit local apply,
  and consent-gated feedback fixtures;
- confirm no active repository hook, MCP endpoint, Scheduled task artifact,
  secret-bearing Codex Action, marketplace mutation, Dev Container payload, or
  ruleset admission change is introduced by this decision; and
- show a final agreement-only diff plus passing local and hosted checks.

External evidence remains separately required for plugin marketplace state,
tag/release artifacts, a live adopter trial, native Windows execution,
adopter-specific connector activation, Task #33/#35 completion, and every
human merge or Settings decision.

## References

- [Architecture guide](../../guides/architecture.md)
- [Capability map](../../guides/copilot-capability-map.md)
- [Automation skill](../../../../.agents/skills/codex-automation/SKILL.md)
- [Official Codex customization](https://learn.chatgpt.com/docs/customization/overview)
- [Official Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Official Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Official Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Official Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Official Codex MCP](https://learn.chatgpt.com/docs/extend/mcp)
- [Official Scheduled tasks](https://learn.chatgpt.com/docs/automations)
- [Official plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Official plugin publication](https://developers.openai.com/plugins/deploy/submission)
- [Official import behavior](https://learn.chatgpt.com/docs/import)
