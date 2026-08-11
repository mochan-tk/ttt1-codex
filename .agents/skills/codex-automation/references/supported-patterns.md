# Supported automation patterns

Use current official Codex documentation as the authority when a capability or
schema may have changed:

- [Hooks](https://learn.chatgpt.com/docs/hooks)
- [MCP](https://learn.chatgpt.com/docs/extend/mcp)
- [GitHub Action](https://learn.chatgpt.com/docs/github-action)
- [Skills](https://learn.chatgpt.com/docs/build-skills)
- [Custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## Repository hook pattern

Repository hooks live at `.codex/hooks.json` and become active only for a
trusted project. Keep examples outside that path until a project Task reviews
the command, event, timeout, and failure policy. Validate the JSON and execute
the referenced command directly in a clean checkout before enabling it.

## MCP pattern

Project-safe MCP configuration belongs in `.codex/config.toml`. Keep secrets in
the environment or a managed credential store. The committed file may name an
environment variable but must never contain its value. Confirm the currently
installed Codex CLI schema with official documentation or `codex mcp --help`
before editing; do not copy a configuration from another client.

## App automation pattern

An app automation is product state, not a tracked repository file. Define its
prompt so each run re-reads the durable ledger and exits safely when no action
is needed. Write schedules with an explicit time zone, use the longest useful
interval, and include a stop condition. The creating user remains the owner.

## GitHub Action pattern

Use `openai/codex-action` only in a separately reviewed workflow. Pin every
third-party Action to a full commit SHA, set `persist-credentials: false`,
grant job-level read permissions unless a documented output requires more, and
place the API key in a GitHub secret. Never run untrusted pull-request code in a
secret-bearing context. Prefer advisory output over automatic mutation.

## Failure contract

Every automation must answer:

- What exact event causes a run?
- How is a duplicate detected?
- What is the maximum runtime and retry count?
- Where is a failure recorded without leaking sensitive input?
- Who can disable it, and how?
- Which human decision remains non-delegable?
