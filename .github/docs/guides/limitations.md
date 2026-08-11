# Limitations and deliberate boundaries

- The plugin directory is validated but is not registered in a personal or
  team marketplace by this repository. Marketplace publication is a separate
  maintainer action.
- The plugin is skills-only. It cannot install `AGENTS.md`, GitHub controls,
  custom project agents, repository configuration, or setup scripts.
- No repository hook is active by default. Hooks execute trusted repository
  content and require a project-specific review.
- No MCP server or private endpoint is preconfigured. The generic kit cannot
  know an adopter's service, authentication, data policy, or version pin.
- No Codex GitHub Action is active by default. The base wall is deterministic;
  a secret-bearing agent review workflow needs a separate threat review.
- App automations are not stored as repository files and cannot be installed by
  a Git template. Users create them in a supported Codex app surface.
- The optional secure Dev Container is owned by a separate frozen Task. This
  reconstruction neither copies nor validates its uncommitted worktree.
- The ruleset helper is also owned by that pending admission-boundary work and
  remains unchanged here. Use only its `--dry-run` path in this candidate;
  source-bound required-check integration is a recorded follow-up.
- The Bash installer is exercised on macOS/Linux-compatible Bash and through
  hermetic fixtures. The PowerShell shim requires a real Windows/Git Bash
  environment for end-to-end confirmation.
- Account-tier behavior for GitHub Projects, rulesets, code owners, private
  repositories, and Actions must be verified in the adopter's organization.
- Live setup helpers currently target GitHub.com explicitly. GitHub Enterprise
  Server is not supported; `GH_HOST` cannot redirect a previewed operation to
  another host.
- The repository cannot prove a human agreement, license, or completion merge
  locally. Those gates exist only in reviewed GitHub history.
- A tag or release must exist before tag-based upgrade commands are repeatable.
  Until then, use an exact commit SHA.
- Source content may mention capabilities introduced after this version.
  Current official Codex documentation and the installed CLI remain the final
  schema authority.
