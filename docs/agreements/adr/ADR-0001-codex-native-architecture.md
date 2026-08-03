# ADR-0001: Codex-native template architecture

- Status: accepted by the agreement merge
- Date: 2026-08-03
- Owners: repository owner and agreement reviewers
- Supersedes: the handoff requirement for identical cross-agent file layouts

## Context

The source scaffold used Copilot-specific instructions, agents, prompts,
skills, and setup files, plus a `CLAUDE.md` compatibility shim. The comparison
experiment now builds independent templates with Codex, Claude, and GitHub
Copilot and then uses each template. Fair comparison therefore requires common
ADLC outcomes and evaluation criteria, not identical implementation files.

Current Codex documentation provides native, repository-scoped surfaces:

- root and nested `AGENTS.md` files for durable guidance;
- `.agents/skills/` for repo-scoped reusable workflows;
- `.codex/agents/` for project-scoped custom subagents; and
- trusted `.codex/config.toml` for shareable project configuration.

Codex custom prompts are deprecated in favor of skills.

## Decision

Build this template with the following authority layers:

1. **Agreement layer:** `docs/agreements/` contains reviewed requirements,
   non-goals, vocabulary, and ADRs.
2. **Always-on layer:** root `AGENTS.md` contains only durable rules needed for
   every Task. Nested `AGENTS.md` files are allowed when a subtree needs
   narrower review or execution rules.
3. **Workflow layer:** each reusable workflow is a focused skill under
   `.agents/skills/<name>/SKILL.md`, with optional deterministic scripts,
   references, templates, and `agents/openai.yaml` metadata.
4. **Role layer:** focused custom agents live under `.codex/agents/*.toml`.
   The template does not pin models or reasoning effort; adopters keep those
   choices in their own policy or configuration.
5. **Configuration layer:** `.codex/config.toml` contains only portable,
   trusted-repository settings. Credentials, personal paths, user models, and
   organization-specific MCP endpoints are excluded.
6. **Ledger and enforcement layer:** GitHub Issues, PRs, Actions, rulesets,
   Projects, CODEOWNERS, labels, and Dependabot remain because they are common
   repository infrastructure.

Do not create:

- `CLAUDE.md`;
- `.github/copilot-instructions.md`;
- Copilot `.instructions.md`, `.agent.md`, `.prompt.md`, or setup workflows
  whose only purpose is that product; or
- deprecated Codex custom prompt files.

When a useful source behavior lived only in one of those files, translate the
behavior into `AGENTS.md`, a Codex skill, a Codex custom agent, a GitHub-common
template, or a deterministic check.

The released repository uses the MIT software license and serves as the
Codex-native sample template associated with Appendix C of the ADLC book. That
distribution identity is approved by this agreement merge. The Appendix may
explain or link to the repository, but the repository remains the executable,
versioned artifact.

## Consequences

- Codex receives one authoritative instruction chain instead of duplicated
  guidance that can drift.
- Skills use progressive disclosure and protect the always-on context budget.
- Comparison artifacts differ by platform while D1-D10, lifecycle gates, CI
  evidence, onboarding quality, and ledger readability remain comparable.
- A user who wants multi-agent-product compatibility must build it as a
  separate variant or later agreement; it is not an implicit goal here.

## Validation

- Start Codex at the repository root and confirm it reports the root
  `AGENTS.md` as project guidance.
- Invoke representative skills explicitly and indirectly; confirm discovery
  from `.agents/skills/`.
- Spawn each project custom agent and confirm its name and role are available.
- Run CI negative checks for forbidden compatibility paths.

## References

- [Codex AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex subagents and project custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Deprecated Codex custom prompts](https://learn.chatgpt.com/docs/custom-prompts)
- [Epic #1](https://github.com/mochan-tk/ttt1-codex/issues/1)
