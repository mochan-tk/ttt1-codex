# Current Codex capability baseline for reconstruction

Status: planning evidence, not an implementation claim<br>
Retrieved: 2026-08-19<br>
Local observation: Codex CLI 0.148.0-alpha.15 on macOS 15.2 arm64<br>
Official stable source inspected: [rust-v0.148.0](https://github.com/openai/codex/releases/tag/rust-v0.148.0), source commit [3ba0f711642a888aec92a611a3f3b2211157ff89](https://github.com/openai/codex/commit/3ba0f711642a888aec92a611a3f3b2211157ff89)

This document distinguishes current official documentation, version-pinned official
source, direct local observation, inference, and UNKNOWN. Product behavior is
never promoted into the durable lifecycle contract without its named surface,
maturity, version, and fallback.

## Evidence classes

| Class | Meaning |
|---|---|
| DOCUMENTED | Current official OpenAI documentation states the behavior for the named surface. |
| SOURCE-SUPPORTED | The pinned stable openai/codex source implements the behavior; public docs may not promise compatibility. |
| OBSERVED | Direct versioned runtime or GitHub observation; not a forward guarantee. |
| INFERENCE | A bounded conclusion from primary evidence, explicitly identified as inference. |
| UNKNOWN | Primary evidence is absent, ambiguous, experimental, or insufficient for architecture authority. |
| UNSUPPORTED | Current primary evidence explicitly rules out the proposed behavior on the named surface. |

Experimental features may change or disappear; stable features have a support
and deprecation path. See [feature maturity](https://learn.chatgpt.com/docs/feature-maturity).

## Capability matrix

| Capability | Finding | Surface and stability | Architecture consequence | Primary evidence |
|---|---|---|---|---|
| Root and nested AGENTS.md | DOCUMENTED. Codex builds an instruction chain from Git root to the working directory; nearer files override earlier guidance. | Local app, CLI, and IDE project execution. Exact cloud parity is not promised. | Keep root guidance small; use nested files only for real path scope. Recheck conflicts, cap, and cloud in #77. | [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |
| Repository Skills | DOCUMENTED locally. Project skills are discovered under .agents/skills and may be explicitly or implicitly invoked. | Local project surfaces; exact cloud discovery parity is UNKNOWN. | Keep workflows in canonical Skills and verify cloud routing separately. | [Build skills](https://learn.chatgpt.com/docs/build-skills) |
| Custom agents | DOCUMENTED/PARTIAL. Built-ins include default, worker, and explorer; project or personal TOML can define roles; a same-named custom role shadows a built-in. The format may evolve. | App, CLI, and IDE local subagents. Complete personal-versus-project duplicate precedence is unclear. | Treat TOML as a default, not an immutable role or ownership lease. | [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| Local subagents | DOCUMENTED. App, CLI, and IDE expose subagents; eligible hosted users receive hosted subagents. App shows threads, CLI exposes /agent, and IDE uses a background panel. | Surface-specific controls. Hosted web shows status but cannot steer or stop an individual child. | Route controls explicitly; do not promise a universal session console. | [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| Descendant spawning | SOURCE-SUPPORTED in stable Multi-Agent V2. Both root and subagent prompts authorize descendants, and the spawn handler records lineage. | Version-pinned stable source; public Subagents documentation does not make this a compatibility promise. | Deep transport can be investigated, but durable Task hierarchy stays in GitHub. | [root/subagent prompts](https://github.com/openai/codex/blob/3ba0f711642a888aec92a611a3f3b2211157ff89/codex-rs/core/src/session/multi_agents.rs#L11-L38), [V2 spawn](https://github.com/openai/codex/blob/3ba0f711642a888aec92a611a3f3b2211157ff89/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs#L63-L109) |
| Ordinary subagent workspace | UNSUPPORTED as writer isolation in current V2. All agents share the same container, filesystem, directory, and CWD; edits are immediately visible. | Version-pinned stable source. | Ordinary subagents remain read-only for lifecycle work. Writing PR workers require explicit managed or provider-neutral worktrees. | [shared workspace source](https://github.com/openai/codex/blob/3ba0f711642a888aec92a611a3f3b2211157ff89/codex-rs/core/src/session/multi_agents.rs#L53-L58) |
| Maximum nesting depth | UNKNOWN for V2. V1 enforces agents.max_depth; current configuration says that setting is V1-only and ignored by V2. | Version-pinned source, runtime limit not documented. | Use a conservative kit limit and #72/#78; never infer unlimited depth. | [V1 check](https://github.com/openai/codex/blob/3ba0f711642a888aec92a611a3f3b2211157ff89/codex-rs/core/src/tools/handlers/multi_agents/spawn.rs#L64-L70), [V2 config scope](https://github.com/openai/codex/blob/3ba0f711642a888aec92a611a3f3b2211157ff89/codex-rs/config/src/config_toml.rs#L668-L674) |
| Concurrency, queueing, budget, and heartbeat | PARTIAL/UNKNOWN. A per-root concurrency setting exists, but defaults, service quotas, queuing, per-child usage, heartbeat, and responsiveness are not a durable public contract. | Surface/account/version dependent. | Keep configurable conservative caps and measure #78. | [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| Sandbox and approval inheritance | PARTIAL. Children inherit the current permission mode; CLI reapplies live overrides, while app/IDE use composer permissions. A custom role may declare a narrower sandbox. | Surface-dependent precedence. | Default child roles read-only; #75 must measure effective policy and denial propagation. | [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [sandboxing](https://learn.chatgpt.com/docs/sandboxing) |
| Parent and ancestor metadata | PARTIAL/EXPERIMENTAL. App Server thread/list can filter direct children or descendants and exposes source kinds. | App Server is experimental; ancestry fields are not durable lifecycle authority. | Use metadata only as advisory correlation; dispatch and release live in GitHub. | [App Server](https://learn.chatgpt.com/docs/app-server) |
| Steering, interrupt, archive, and delete | PARTIAL. App Server documents turn steering/interrupt and thread lifecycle. Archive attempts descendants and can partially succeed. | Experimental API; app/CLI/IDE UI differs; hosted web lacks individual steer/stop. | Preserve leaf-first cleanup and explicit reconciliation as kit policy. | [App Server](https://learn.chatgpt.com/docs/app-server), [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| Desktop managed worktrees | DOCUMENTED. Managed worktrees are separate working copies with shared Git metadata and begin detached; create a branch before commit/push/PR. Git permits one worktree per checked-out branch. | Codex desktop app. | Use one explicit active writer lease per PR even when worktrees isolate paths. | [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees) |
| Permanent worktrees | DOCUMENTED but not writer isolation. Multiple chats can use one permanent worktree. | Codex desktop app. | Chat count cannot substitute for a single-writer lease. | [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees) |
| Local/Worktree handoff | DOCUMENTED. Desktop can move a chat/code association between Local and Worktree modes. | Desktop app only. | #74 records exact Git/thread state preserved by each direction. | [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees) |
| CLI | DOCUMENTED core commands; codex cloud and app-server remain experimental. CLI does not manage Scheduled tasks. | CLI. | Route stable local commands separately from experimental service/API commands. | [CLI](https://learn.chatgpt.com/docs/codex/cli), [developer commands](https://learn.chatgpt.com/docs/developer-commands) |
| IDE | PARTIAL. Local work, subagents, and cloud delegation are available; plugins and Scheduled-task management are not. | IDE extension. | Do not claim desktop plugin or schedule parity in IDE. | [IDE](https://learn.chatgpt.com/docs/codex/ide), [Plugins](https://learn.chatgpt.com/docs/plugins) |
| Cloud tasks | PARTIAL. A cloud task runs in an isolated container from a selected branch/SHA, may edit/test, and can return a diff or PR. Setup network and agent network differ; setup secrets are removed before agent execution. | Cloud service; CLI cloud command experimental. | Keep cloud task result, branch/commit/PR, and GitHub checks as separate evidence lanes. | [Codex cloud](https://learn.chatgpt.com/docs/cloud), [cloud environment](https://learn.chatgpt.com/docs/environments/cloud-environment) |
| Cross-surface handoff | PARTIAL. Documented routes include CLI /app, app Local/Worktree, remote-host handoff, and IDE-to-Cloud delegation that starts a new cloud chat with existing chat context and local source changes. Same-thread identity, branch mapping, and exact Git continuity for cloud delegation remain UNKNOWN. | Route-specific. | Maintain an explicit routing matrix, measure #77, and retain a GitHub/Git fallback. | [developer commands](https://learn.chatgpt.com/docs/developer-commands), [remote connections](https://learn.chatgpt.com/docs/remote-connections), [Prompting: Cloud delegation](https://learn.chatgpt.com/docs/prompting) |
| Hooks | DOCUMENTED with gaps. Current events cover session, subagent, tool, permission, compaction, and stop phases. Only command handlers execute; prompt and agent handlers are skipped. Coverage is not universal. | Trusted local project/plugin execution; surface/version dependent. | Hooks may add observation or bounded guards but are not a complete path lease or lifecycle wall. | [Hooks](https://learn.chatgpt.com/docs/hooks) |
| Plugins | PARTIAL by surface. Plugins can package skills and other supported components; desktop/CLI support them, IDE does not, and a new session is needed after install. | Product state plus artifact. | Keep the repository plugin skills-only and distinguish validation from publication/install/use. | [Plugins](https://learn.chatgpt.com/docs/plugins), [package plugins](https://developers.openai.com/plugins/build/plugins) |
| Scheduled tasks | DOCUMENTED on desktop/web; CLI/IDE management unsupported. Only desktop can use a local project/worktree; web cannot directly use a local folder. | Product state, not a repository file. | Do not invent schedule files; any later automation is Issue-first and surface-specific. | [Scheduled tasks](https://learn.chatgpt.com/docs/automations) |
| GitHub integration | DOCUMENTED. Codex can review or start cloud work and, when authorized, push fixes. | Cloud connection and GitHub permissions. | Codex result does not replace CI, branch protection, or human review. | [GitHub integration](https://learn.chatgpt.com/docs/third-party/github) |
| ChatGPT Projects versus local projects | DOCUMENTED as distinct concepts; no official Program/Epic/File-ownership lifecycle exists. | ChatGPT product versus local repositories. | GitHub Issues/PRs remain the durable hierarchy; use Project session as a kit role name only. | [Projects and chats](https://learn.chatgpt.com/docs/projects) |

## Direct runtime observations

The local binary reported Codex CLI 0.148.0-alpha.15. A read-only feature
listing classified multi_agent, hooks, and plugins as stable; multi_agent_v2
was classified stable but disabled in the observed configuration. This is
version-scoped observation and does not replace stable-release source or
surface documentation.

No runtime spike was performed in this Planning Task. Issues
[#72](https://github.com/mochan-tk/ttt1-codex/issues/72) through
[#78](https://github.com/mochan-tk/ttt1-codex/issues/78) remain blocked and not
ready.

## Corrections to the historical target narrative

- The session hierarchy is a kit role mapping over Codex threads, not a native
  mirror of GitHub Program/Epic/Task semantics.
- One-hop and read-only delegation is a required safety policy, not a Codex
  nesting limit. V2 descendants exist, but ordinary children share the checkout.
- Parent permission inheritance must be scoped by surface; a role TOML is a
  default, not an unbypassable fence.
- Leaf-first teardown is retained because archive can cascade and partially
  fail, not because Codex requires leaf-first order.
- This repository plugin is skills-only. Current platform plugins can package
  more component types, so the narrower claim must not be generalized.
- IDE-to-Cloud delegation creates a new cloud chat carrying context and local
  source changes. Whether it preserves any thread or Git identity is UNKNOWN;
  cloud completion, branch/PR state, and PR checks remain separate.

## Controlled architecture decisions

The planning architecture may rely on:

1. GitHub and Git as durable authority.
2. Root/nested AGENTS.md and repository Skills as Codex-native guidance.
3. Explicit desktop managed or provider-neutral worktrees for writing workers.
4. Read-only ordinary subagents for bounded parallel audit/review.
5. Human authority over high risk, agreements, Settings, acceptance, and merge.

It may not rely on:

1. Thread ancestry as a durable ownership lease.
2. Ordinary subagent checkout isolation.
3. Unlimited or fixed V2 depth, concurrency, budget, or heartbeat.
4. Atomic descendant shutdown or failure propagation.
5. Universal cross-surface resume/control.
6. Static plugin/config files as evidence of product installation or external state.
