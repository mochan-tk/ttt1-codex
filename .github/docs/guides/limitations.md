# Limitations and deliberate boundaries

- The plugin directory is validated but is not registered in a personal or
  team marketplace by this repository. Marketplace publication is a separate
  maintainer action.
- The plugin is skills-only. It cannot install `AGENTS.md`, GitHub controls,
  custom project agents, repository configuration, or GitHub setup scripts.
  Its synchronized skills detect missing full-kit controls and return
  read-only analysis or drafts instead of claiming those controls exist.
- No repository hook is active by default. Hooks execute trusted repository
  content and require a project-specific review. In the current
  [Hooks runtime](https://learn.chatgpt.com/docs/hooks), only
  `type: "command"` handlers execute; `prompt` and `agent` handlers are parsed
  but skipped.
- No MCP server or private endpoint is preconfigured. The generic kit cannot
  know an adopter's service, authentication, data policy, or version pin.
- No Codex GitHub Action is active by default. The base wall is deterministic;
  a secret-bearing agent review workflow needs a separate threat review.
- Scheduled tasks are not stored as repository files and cannot be installed
  by a Git template. Web and desktop can create and manage them; only desktop
  can use a local project/worktree and requires the machine and app to remain
  running. Web cannot work directly in a local folder. CLI and IDE have no
  Scheduled management interface. See the
  [official documentation](https://learn.chatgpt.com/docs/automations).
- The official [import flow](https://learn.chatgpt.com/docs/import) does not
  list GitHub Copilot. Migration from the Copilot kit is manual; `/import` is
  not a compatibility bridge.
- The bundled project custom agent named `explorer` intentionally shadows the
  built-in Codex `explorer`. A same-named custom agent takes precedence. Rename
  or remove it if the built-in role is preferred.
- Bundled custom-agent `sandbox_mode = "read-only"` is a default, not an
  unbypassable boundary. Subagents inherit the parent permission mode and
  Codex reapplies live runtime overrides when spawning them; review the parent
  mode before delegation.
- REQ-018 remains literal: `1 Task = 1 session = 1 worktree = 1 branch = 1 PR`.
  That Task session is the sole implementing writer. Any bounded Task-support
  subagent is read-only, receives no File ownership, and may only explore,
  review, or observe tests before reporting one hop to the Task session. The
  separate read-only orchestrator may update the GitHub planning ledger at its
  Epic-parent layer, but never performs Task implementation.
- The optional secure Dev Container is owned by a separate frozen Task. This
  reconstruction neither copies nor validates its uncommitted worktree.
- The ruleset helper is also owned by that pending admission-boundary work and
  remains unchanged here. Use only its `--dry-run` path in this candidate;
  source-bound required-check integration is a recorded follow-up in Task #35.
  This repository does not yet claim source-equivalent ruleset admission.
- The Bash installer is exercised on macOS/Linux-compatible Bash and through
  hermetic fixtures. The PowerShell shim requires a real Windows/Git Bash
  environment for end-to-end confirmation.
- Account-tier behavior for GitHub Projects, rulesets, code owners, private
  repositories, and Actions must be verified in the adopter's organization.
- A successful Codex cloud Task and a PR workflow are separate states. A run in
  `action_required` can be an organization Actions approval boundary; it is
  neither evidence the agent failed nor evidence required CI passed.
- Live setup helpers currently target GitHub.com explicitly. GitHub Enterprise
  Server is not supported; `GH_HOST` cannot redirect a previewed operation to
  another host.
- The repository cannot prove a human agreement, license, or completion merge
  locally. Those gates exist only in reviewed GitHub history.
- A tag or release must exist before tag-based upgrade commands are repeatable.
  Until then, use an exact commit SHA.
- The pinned source audit is
  `20637b703cbde6abd8934fc222abbe6c82bb4568` with 110 tracked files. Source
  content may advance after that pin; current official Codex documentation and
  the installed runtime remain the final product-schema authority.
