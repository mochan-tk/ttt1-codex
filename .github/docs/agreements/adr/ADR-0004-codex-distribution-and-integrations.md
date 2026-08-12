# ADR-0004: Codex distribution and integration boundary

- Status: proposed; becomes authoritative only through an agreement merge
- Date: 2026-08-12
- Owners: repository owner and agreement reviewers
- Source baseline: `mochan-tk/agentic-dev-kit-for-copilot` at
  `f466c7e169243e2bea03b4b33a20f8c557328d96`

## Context

The existing Codex template already implements the durable GitHub ledger,
Three Merges, eight native skills, three custom agents with read-only
defaults, and stronger Task-ritual tests than the Copilot source. The source
additionally provides a safe installer, context connectors, consent-gated
adopter feedback, and a more complete distribution story. Separate frozen
work owns the optional secure Dev Container and its GitHub admission/ruleset
boundary; those files must not be folded into this reconstruction.

Codex also exposes native capabilities that are not interchangeable:
repository skills, project custom agents, trusted repository hooks, MCP
configuration, app automations, plugins, and an optional GitHub Action. Each
has a different trust and persistence boundary.

## Decision

Extend the existing Codex template instead of replacing it.

1. Keep GitHub as the durable control and enforcement plane.
2. Ship nine canonical repository skills and four bundled custom agents with
   read-only defaults and explicit no-write instructions. Add
   `codex-automation` and `explorer` to the existing surface; parent and user
   runtime policy remains authoritative.
3. Provide two complete repository adoption paths: GitHub template creation
   and the collision-safe `scaffold-init` installer. The installer distributes
   `.github/**`, `.agents/**`, bundled `.codex/agents/**`, portable
   `.codex/config.toml`, `AGENTS.md`, and lineage, while preserving instance
   truth on upgrade.
4. Provide a validated skills-only plugin artifact. It deliberately does not
   pretend to install GitHub controls, custom project agents, repository
   configuration, or setup scripts.
5. Ship connector definitions and a preview-first activation wizard. Connector
   activation remains a reviewed project decision.
6. Keep hooks, organization-specific MCP endpoints, secret-bearing Actions,
   app automations, and repository settings disabled by default. The
   `codex-automation` skill explains how to add only a supported mechanism with
   least privilege and explicit authority.
7. Offer adopter feedback only after an unexpected interactive failure, only
   with an exact preview and literal consent, and only from an allowlisted
   payload. There is no telemetry endpoint.
8. Do not copy, activate, modify, or package `.codex/devcontainer/**`, and do
   not change `.github/scripts/setup-ruleset.sh` in this work. Their frozen
   Tasks remain independent.

## Consequences

- Template and installer adopters receive the full operating system; plugin
  adopters receive only reusable skills and must not be told otherwise.
- There is one canonical skill tree under `.agents/skills/`; deterministic
  validation requires the plugin copy to be byte-identical.
- A repository may add hooks or MCP configuration later, but credentials,
  personal paths, concrete model pins, and private endpoints remain outside the
  generic template.
- Upgrades refresh kit-owned machinery and preserve agreements, context,
  workflows, CODEOWNERS, `AGENTS.md`, and `.codex/config.toml` for review.
- The Copilot source remains an attributed design origin, not a compatibility
  surface or a runtime dependency.

## Validation

- Run the complete deterministic test and validator suite.
- Exercise installer dry-run, collision refusal, force, upgrade preservation,
  symlink refusal, dirty-source provenance, and stage-only behavior in isolated
  repositories.
- Validate the plugin manifest with the current plugin validator and compare
  every packaged skill byte-for-byte with the canonical copy.
- Validate connector structure and both no-network preview and explicit apply
  paths for source activation.
- Confirm no active hook, MCP endpoint, Codex Action, marketplace mutation, or
  Dev Container payload is introduced by this decision.

## References

- [Architecture guide](../../guides/architecture.md)
- [Capability map](../../guides/copilot-capability-map.md)
- [Automation skill](../../../../.agents/skills/codex-automation/SKILL.md)
- [Official Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Official Codex plugins](https://learn.chatgpt.com/docs/build-plugins)
