# Contributing

Start every change from a GitHub Task Issue and follow `AGENTS.md`. Keep one
active writer and one branch/worktree/PR per Task. Add executable acceptance
criteria before implementation, land an authoritative plan comment before the
first change, and post measured outcome Evidence before reporting completion.

For kit changes:

- preserve the GitHub control plane and Codex-native execution boundary;
- keep application-owned paths outside scaffold-only validators;
- update the Copilot capability map when a source behavior changes;
- keep canonical and plugin skills byte-identical;
- add regression coverage for every validator, installer, or setup change;
- use full commit pins for third-party Actions; and
- do not add secrets, personal paths, private endpoints, concrete model pins,
  active hooks, or organization settings to the generic distribution.

Run the complete suite in
[the maintenance guide](.github/docs/guides/maintenance.md) before opening a
pull request. Fill every row of the PR Evidence table and identify any deferred
criterion with a linked, requester-approved work-order change.
