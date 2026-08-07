# ADR-0001: Codex-native template architecture

- Status: accepted by the agreement merge
- Date: 2026-08-03
- Amended: 2026-08-06 by Task #25
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

Applying the template to an actual application exposed a namespace collision:
ordinary product repositories already use top-level `docs/` and `scripts/`.
The original whole-repository Markdown, English, Bash, and ShellCheck scans
also treated adopter content as if it were a scaffold contract. Moving only
the shipped files would therefore leave the behavioral collision in place.
The architecture needs an explicit physical and validation boundary without
giving up GitHub controls or Codex-native discovery.

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

### Namespace and ownership contract

`.github/**` is reserved for GitHub control-plane use and shared between the
scaffold and adopter. It contains both reusable ADLC controls and
adopter-specific GitHub configuration, so location under `.github/**` alone
does not establish scaffold ownership. Each scaffold check explicitly names
the files or subtrees whose contract it enforces.

For namespace ownership, the Scaffold control plane is a cross-cutting view of
named contracts across the two authority planes above, not a third authority
plane. It includes these paths:

- `.github/docs/**` contains reviewed ADLC agreements, minimum
  provenance-linked context extracts, and scaffold operating documentation.
- `.github/scripts/**` contains ADLC setup helpers, deterministic scaffold
  checks, and their tests.
- `.agents/**` and `.codex/**` remain the Codex-native skill, skill-local
  helper, role, and project configuration surfaces.
- Root `AGENTS.md` remains the always-on repository constitution.

The GitHub-common contracts required by REQ-034 are also explicitly named:

- `.github/CODEOWNERS`;
- `.github/ISSUE_TEMPLATE/config.yml`,
  `.github/ISSUE_TEMPLATE/epic.yml`, and
  `.github/ISSUE_TEMPLATE/task.yml`;
- `.github/PULL_REQUEST_TEMPLATE.md`;
- `.github/dependabot.yml`; and
- `.github/workflows/ci.yml` and
  `.github/workflows/retro-hygiene.yml`.

These named files may contain accepted instance customization. Scaffold
upgrades review and merge those differences; they do not replace them. Other
Issue forms, workflows, and GitHub files beside the named contracts remain
adopter-owned.

Top-level `docs/**`, `scripts/**`, and other non-reserved product paths form the
Application workspace. The scaffold does not ship, rewrite, or sweep those
paths by filename extension alone. Adopter-specific files under `.github/**`
are likewise application-owned unless an explicit scaffold contract names
them. Onboarding measures the application's toolchain and adds suitable
project checks to the existing quality wall.

Root distribution files have explicit, mixed responsibilities rather than
implying ownership of the whole repository root:

- `README.md` is the shipped discovery and onboarding surface, then becomes a
  shared document that the adopter integrates with the application README.
- `LICENSE` is the reviewed distribution license; changing or replacing it is
  a separate human legal decision.
- `SCAFFOLD-CHANGELOG.md` preserves scaffold lineage and upgrade directions.
- `.gitignore` is shared configuration that adopters may extend; upgrades
  review its diff and do not replace instance additions blindly.

Scaffold ownership defines default validation and upgrade-review
responsibility. It never authorizes an upstream release to overwrite accepted
instance agreements, tuned guidance, or project truth. Persistent extracts in
`.github/docs/context/**` remain minimum English template artifacts under
REQ-025 and REQ-029; source originals and controlled data stay in their
governed external locations.

### Initial migration requirement

The initial transition to this contract must be one atomic,
history-preserving Task: move the current `docs/**` and `scripts/**` scaffold
artifacts to their named target paths, update every reference, workflow, and
test, and land positive and negative boundary fixtures together. It must
preserve form and template synchronization, immutable Action pins, actionlint,
CODEOWNERS coverage, ruleset and required-check linkage, and the existing CI
job names. Splitting the physical moves would leave an intermediate repository
with broken commands and ambiguous ownership.

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

1. **Agreement layer:** `.github/docs/agreements/` contains reviewed
   requirements, non-goals, vocabulary, and ADRs after the namespace
   transition.
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
- Real applications can use top-level `docs/**` and `scripts/**` without their
  content being claimed or linted by the generic scaffold.
- Explicit control-path allowlists keep scaffold failures fail-closed without
  turning adopter-specific `.github/**` files into upstream-owned artifacts.
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
- Add fixture application files under top-level `docs/**` and `scripts/**` and
  confirm Japanese text, a broken application-only link, and invalid shell are
  outside scaffold-only gates.
- Add equivalent applicable violations under `.github/docs/**`,
  `.github/scripts/**`, `.agents/**`, `.codex/**`, and root `AGENTS.md`; confirm
  the corresponding scaffold gates fail closed.
- Confirm adopter-specific `.github/**` files are ignored unless an explicit
  scaffold contract includes them, while all shipped GitHub controls still
  receive their deterministic checks.
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
- [Copilot namespace migration PR #78](https://github.com/mochan-tk/ttt1-copilot/pull/78)
- [Codex Task #25 owner observation](https://github.com/mochan-tk/ttt1-codex/issues/25)
- [Epic #1](https://github.com/mochan-tk/ttt1-codex/issues/1)
