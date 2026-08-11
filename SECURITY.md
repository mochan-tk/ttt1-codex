# Security policy

Do not open a public Issue containing a vulnerability, credential, private
repository identity, personal path, customer data, or exploit details. Use the
repository owner's private security-reporting channel when enabled. If no
private channel is available, contact the owner through the public profile
without disclosing the sensitive details and ask for a secure channel.

The kit's security boundaries include:

- third-party Actions pinned to full commit SHAs;
- least-privilege workflow permissions and non-persistent checkout credentials;
- no active repository hooks, MCP endpoints, telemetry, or secret-bearing
  Codex Action by default;
- installer collision and symlink refusal, immutable source resolution,
  stage-only changes, and dirty-source provenance;
- reference-not-paste handling for secrets, PII, and controlled data; and
- consent-gated adopter feedback with a fixed allowlist and exact preview.

Treat `AGENTS.md`, skills, custom agents, hooks, workflows, setup scripts,
connector definitions, plugin manifests, and installer changes as supply-chain
sensitive. Review their behavior and tests before trusting a repository or
installing a release.
