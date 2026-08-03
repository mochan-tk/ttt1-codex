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

The owner further clarified that Codex specialization applies to how agents
execute, not to whether the repository uses GitHub. GitHub capabilities are
indispensable to ADLC and must remain the durable control, ledger, and
enforcement foundation beneath the Codex-native layer.

## Decision

Adopt two cooperating planes:

1. **GitHub control plane — mandatory.** Issues, forms, labels, types,
   sub-issues, and dependencies encode work and its tracking graph. Branches,
   pull requests, reviews, CODEOWNERS, closing links, releases, and tags encode
   change and the Three Merges. Actions, checks, rulesets, Dependabot, and
   security features provide deterministic enforcement. Projects and its
   fields are derived planning views where the account supports them.
2. **Codex execution plane — native.** `AGENTS.md`, repository skills, custom
   agents, portable configuration, and Codex's GitHub connection or `gh`
   fallback tell Codex how to collect, agree, plan, route, execute, verify,
   resume, learn, and upstream through the GitHub plane.

The GitHub plane is authoritative; Codex session plans, messages, and internal
state are replaceable caches. Account-dependent GitHub features may degrade
visibly with documented setup or fallback behavior, but never silently into
session-only state.

The GitHub capability contract is:

| Capability | Required ADLC role |
|---|---|
| Git history, versioned agreements, tags, and lineage | Preserve reviewed truth and upgrade provenance |
| Issues, forms, comments, labels, sub-issues, and dependencies | Hold work orders, plans, outcomes, and the tracking graph |
| Mechanically calculated frontier | Expose runnable Tasks from Issue state rather than session memory |
| Projects and fields | Project the Issue graph when available; never become planning truth |
| Pull requests, Evidence template, reviews, CODEOWNERS, and closing links | Hold change, human judgment, the Three Merges, and Issue closure |
| Actions, required checks, rulesets, branch protection, and security automation | Form the deterministic verification and enforcement wall |
| Issue-first repository Settings procedure | Keep non-delegable human actions in the ledger |

The GitHub-common repository skeleton therefore retains Issue forms, the PR
template, CODEOWNERS, CI and retro-hygiene workflows, Dependabot, and safe setup
scripts for labels, Projects, and rulesets. Agent-facing instructions, skills,
roles, prompts, and tool configuration are the platform-specific portion.

Within those planes, build this template with the following authority layers:

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
6. **Ledger and enforcement layer:** GitHub Issues, PRs, Actions, checks,
   rulesets, Projects, CODEOWNERS, labels, Dependabot, and security automation
   remain mandatory ADLC infrastructure where applicable.

Do not create:

- `CLAUDE.md`;
- `.github/copilot-instructions.md`;
- Copilot `.instructions.md`, `.agent.md`, `.prompt.md`, or setup workflows
  whose only purpose is that product; or
- deprecated Codex custom prompt files.

When a useful source behavior lived only in one of those files, translate the
behavior into `AGENTS.md`, a Codex skill, a Codex custom agent, a GitHub-common
template, or a deterministic check.

Do not translate away an official GitHub capability. Codex-specific files may
change the execution mechanism and repository layout, but Issues remain work
orders, PRs remain change and merge records, and GitHub checks remain the hard
verification wall.

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
- Codex can execute the full lifecycle natively without weakening the shared
  GitHub work graph, merge history, review boundary, or deterministic gates.
- A user who wants multi-agent-product compatibility must build it as a
  separate variant or later agreement; it is not an implicit goal here.

## Validation

- Start Codex at the repository root and confirm it reports the root
  `AGENTS.md` as project guidance.
- Invoke representative skills explicitly and indirectly; confirm discovery
  from `.agents/skills/`.
- Spawn each project custom agent and confirm its name and role are available.
- Run CI negative checks for forbidden compatibility paths.
- From a fresh Codex session, traverse one Task from an Issue plan comment
  through implementation, Actions and required checks, PR review, Evidence,
  `Closes #N`, and the completion merge record.
- Verify setup automation for labels, Projects, and a disabled ruleset against
  a live GitHub account, including visible behavior when a feature is
  unavailable.

## References

- [Codex AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex subagents and project custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Deprecated Codex custom prompts](https://learn.chatgpt.com/docs/custom-prompts)
- [Pinned Claude-built comparison baseline](https://github.com/mochan-tk/ttt1-claude/tree/e88688c80095036f255b1353f827a4b2f32fdc49)
- [Epic #1](https://github.com/mochan-tk/ttt1-codex/issues/1)
