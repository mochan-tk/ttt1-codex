# ADR-0003: Codex-native secure Dev Container contract

- Status: accepted by the agreement merge
- Date: 2026-08-08
- Owners: repository owner and agreement reviewers
- Scope: inactive reference and future implementation evidence; no container
  or materializer is implemented by this ADR
- Provenance: official OpenAI guidance and the pinned `openai/codex` reference
  at `45f8cafa4e2ec20f9b189d5aa9409e424b6d3d09`

## Context

Teams may want a reproducible local boundary for Codex when a host cannot run
the Linux sandbox directly or already standardizes on Dev Containers. OpenAI's
security guidance describes Docker as an outer isolation boundary, recommends
keeping Codex's Linux sandbox as an inner boundary where the container permits
it, and warns that an outer-boundary-only process can expose every credential
available inside the container to malicious repository code.

The official secure Dev Container example is useful design provenance. At the
pinned commit it demonstrates an Ubuntu 24.04 base, Codex and common tools,
`bubblewrap`, firewall startup, persistent named volumes, and explicit Docker
capabilities. It is not this template's implementation contract. Its source is
Apache-2.0, this repository is MIT, and some source choices are deliberately
outside this template's defaults, including a sandbox-disable environment
variable, broad provider ranges, a mutable `latest` feature, Rust contributor
tooling, and a global ignore that hides `.codex/`.

GitHub **Use this template** copies every tracked payload, including optional
references. Existing applications also commonly own `.devcontainer/**`.
Shipping an active root container would therefore create a distribution and
ownership collision. The agreement must separate an inspectable Codex-owned
reference from an adopter-owned active container and must define measurable
security claims before implementation begins.

The threat model includes malicious or compromised repository content,
dependency and download substitution, accidental credential disclosure,
outbound data exfiltration, an incomplete IPv4 or IPv6 firewall, over-broad
host mounts, and container escape made easier by relaxed runtime controls.
Docker and `bubblewrap` reduce exposure but are not perfect isolation. Any
credential intentionally projected into the workspace remains reachable by
repository code running with the same container identity.

## Decision

### 1. Distribution, ownership, and activation

- The canonical reference lives only under `.codex/devcontainer/**`. It is an
  inactive, optional Codex-owned payload and may not be the repository's active
  Dev Container configuration.
- GitHub **Use this template** intentionally copies the reference. The GitHub
  Issue, agreement pull request, later implementation pull request, reviews,
  required checks, and closing links remain the authoritative ADLC ledger and
  enforcement record. Container-local state does not replace that plane.
- Application `.devcontainer/**` remains adopter-owned. A later, separately
  scoped `risk:high` setup action may propose activation only after it previews
  the exact source, target, additions, replacements, and deletions. It refuses
  an existing target or any collision by default.
- Activation does not infer ownership from a filename, header, comment, marker,
  or heuristic sentinel and does not sweep unrelated application container
  files. Overwrite mode, if ever proposed, requires a separate agreement and
  explicit human decision.
- This ADR specifies no implemented materializer, installer, update command,
  container file, network rule, credential, or runtime setting.

### 2. Two isolation boundaries

Docker is the outer boundary between the Dev Container and the host. The
default profile also keeps Codex's Linux `bubblewrap` (`bwrap`) sandbox as the
preferred inner boundary when the selected Docker runtime and architecture
support it. The implementation must prove the inner sandbox works; installing
the binary alone is not evidence.

The default profile never sets `CODEX_UNSAFE_ALLOW_NO_SANDBOX=1` and never
starts Codex with `--sandbox danger-full-access` or
`--dangerously-bypass-approvals-and-sandbox`. An outer-boundary-only mode is a
manual exception, not a distributed default. Only trusted repositories may use
it, and it must repeat the official warning: malicious project code can
exfiltrate anything available inside the Dev Container, including Codex
credentials. The exception requires a separate recorded human decision and
must not be selected by fallback logic.

The Dev Container client and engine, active configuration, Dockerfile, build
context allowlist, local features, bootstrap and firewall programs, materializer
output, and pinned image/feature artifacts form the pre-container trusted
computing base. They are evaluated before the inner sandbox or in-container
probes can protect the session. The active configuration is therefore never
auto-discovered from an untrusted branch and passed directly to a Dev Container
client.

Before every build, rebuild, or start, a trusted external preflight obtains the
expected manifest from the immutable commit accepted by the implementation PR
and verifies every transitive control artifact by exact hash or digest. It also
requires regular files with no symlink escape and rejects missing, untracked,
or drifted active `.devcontainer/**`; host-side lifecycle commands such as
`initializeCommand`; privileged mode; unexpected mounts, capabilities, or
security relaxations; mutable feature/image references; and a build context
outside the reviewed allowlist. The preflight itself is pinned outside the
candidate worktree or independently verified by the human; it never executes a
checker supplied by the untrusted branch. Any mismatch fails before the client
reads or launches the active configuration. Changing a trusted-control artifact
requires a new Issue, pull request, required checks, and human review.

The container is never privileged and never receives the Docker socket.
Capabilities and relaxed Docker security options use this allowlist and must
be retained only when architecture-specific runtime evidence proves them
necessary:

| Control | Permitted purpose | Required justification |
|---|---|---|
| `NET_ADMIN` | Install and inspect the IPv4 and IPv6 default-deny firewall. | Privileged setup is isolated from the normal agent identity, and mutation probes prove that identity cannot acquire the capability after startup. |
| `NET_RAW` | Support only a measured firewall or network probe that requires raw sockets. | Omit it when TCP/UDP probes and the selected firewall do not need it. |
| `SYS_ADMIN` | Permit the namespace and mount operations required by the measured `bwrap` path. | This broad capability materially weakens Docker; evidence must show no narrower user-namespace configuration works. |
| `SYS_CHROOT` | Permit the measured inner sandbox to change its root. | Omit it if the selected `bwrap` invocation succeeds without it. |
| `SETUID` and `SETGID` | Permit the measured setuid `bwrap` identity transition. | The installed helper, ownership, mode, and non-root caller must be inspected. |
| `SYS_PTRACE` | Permit process inspection only if Codex's measured Linux sandbox requires it. | Omit it unless the supported-architecture smoke test fails for this specific reason. |
| `seccomp=unconfined` | Allow `bwrap` to establish Codex's inner seccomp policy when Docker's default profile blocks it. | Prefer a narrow outer profile; if unconfined is necessary, prove the inner sandbox and record the lost outer control. |
| `apparmor=unconfined` | Allow the measured namespace and mount sequence when the host AppArmor profile blocks it. | Prefer a named narrow profile; omit this relaxation on runtimes that do not require it. |

No capability or relaxation is included merely because the provenance example
used it. The later implementation maps the minimum proven set separately for
`linux/amd64` and `linux/arm64`, documents the residual risk, and fails closed
instead of silently disabling the inner sandbox.

Firewall bootstrap runs through a root-owned one-shot init, isolated sidecar,
or host proxy before any untrusted repository hook or Codex process. The
ordinary Codex identity receives no root login, blanket or passwordless `sudo`,
effective `NET_ADMIN` or `NET_RAW`, or write access to firewall binaries,
rules, sets, DNS configuration, or the allowlist. A narrowly scoped bootstrap
helper, if required, accepts only root-owned read-only policy and is not
available to the agent after setup. Startup fails closed when the runtime
cannot establish this separation. The later runtime evidence must prove that
the ordinary identity cannot gain privilege, flush or replace IPv4/IPv6 rules,
change an address set, or rewrite the allowlist.

### 3. Runtime outbound policy

Runtime egress is default-deny for both IPv4 and IPv6 before Codex or repository
hooks can run. Firewall setup fails closed when a required tool is absent, a
domain cannot be resolved, an address or rule is invalid, either protocol
family cannot be governed, or a probe disagrees with policy. There is no
permissive startup fallback.

Name resolution uses a root-owned DNS policy surface that accepts only the
exact approved query names and sends them only to the configured resolver.
The ordinary agent cannot select another resolver, issue arbitrary TCP or UDP
port 53 traffic, rewrite resolver policy, or bypass it with DNS over TLS or
DNS over HTTPS. Wildcard queries are not inferred from an allowed hostname.
The IPv4 and IPv6 negative wall includes a randomized external query name and
an alternate-resolver attempt; successful resolution or transmission fails
startup. Without this control, an attacker could encode data in DNS query names
even while every HTTP blocked probe passes.

The intended minimum-domain allowlist for runtime is explicit, but remains a
candidate until the later implementation measures each flow:

- `api.openai.com` and `auth.openai.com` as candidate Codex API and
  authentication endpoints; and
- `github.com`, `api.github.com`, `codeload.github.com`,
  `raw.githubusercontent.com`, and `objects.githubusercontent.com` as candidate
  endpoints for GitHub clone, fetch, push, pull request, Issue, and
  release-object flows.

An implementation may remove an unused domain. It may add a domain only with a
documented runtime need, positive probe, owner review, and corresponding policy
test. Package registries and build mirrors belong to the disposable build
phase unless runtime evidence proves they are necessary. Organization-specific
domains, MCP endpoints, and application services are instance decisions, not
generic defaults.

Startup verification exercises both an allowed destination and a deliberately
blocked destination over IPv4 and IPv6. If a public allowed endpoint lacks one
address family, a disposable dual-stack controlled probe service must exercise
the actual rules; absence of host IPv6 is not passing evidence. A failed
allowed probe or successful blocked probe stops startup.

Domain-to-address firewall rules are a bounded control, not perfect domain
isolation:

- DNS rebinding can change an answer between validation and use;
- cached addresses expire, so TTL-aware DNS refresh or a DNS-aware proxy is
  required for long-running sessions;
- CDNs and shared IP addresses can admit traffic beyond one hostname;
- an allowed hostname does not constrain tenant, account, repository, API path,
  request body, or credential scope, so malicious code can still exfiltrate to
  an allowed API and a domain allowlist is not data-loss prevention;
- provider address ranges change and are broader than a domain allowlist;
- Docker DNS and host-network modes can bypass an incomplete ruleset; and
- IPv4-only resolution or filtering leaves an IPv6 escape path.

The active implementation therefore rejects host networking, validates DNS
answers and refresh behavior, applies equivalent IPv4 and IPv6 policy, and
tests changing-provider-range failure. Least-scope credentials, provider-side
access controls, audited requests, and an instance-specific proxy that can
enforce tenant, repository, and API-path policy are separate controls; the
generic firewall alone cannot make that secure claim. Fetching a provider's
current meta ranges is never treated as immutable domain assurance.

### 4. Credentials, persistence, mounts, and build context

- No secret is committed, copied into the image, placed in a build argument or
  build context, persisted in a layer, printed to a build/start log, or written
  to command history. `.env`, credential files, tokens, and unrelated adopter
  workspace content never reach the builder.
- Runtime credentials are projected explicitly, individually, and at minimum
  scope. They are revocable and short-lived where the provider supports that.
  Repository code can access every credential projected inside the container;
  the container is not a secret boundary from its own workspace.
- Persistent Codex state, GitHub CLI state, and Bash/Zsh command history use
  separate named volumes with inspected ownership and permissions. Named
  volumes do not justify persisting plaintext tokens or secrets in history.
- The workspace or selected linked worktree is the only general read-write host
  bind. Any other host bind names one necessary file or directory, is read-only,
  and is documented in the evidence. A broad host home, SSH directory, parent
  source tree, credential directory, agent socket, or Docker socket is
  forbidden. Prefer a generated minimal Git configuration over binding the host
  `.gitconfig`.
- The Docker build context is the minimal immutable reference subtree, not the
  repository or adopter workspace root. It uses an explicit allowlist and no
  `COPY .`; an inspection test proves that an adopter `.env`, application
  source, `.git`, and unrelated workspace files cannot be sent to the builder.

### 5. Baseline and supply chain

The intended generic baseline is Ubuntu 24.04. The later implementation may
claim multi-architecture support only after measuring `linux/amd64` and
`linux/arm64`. For each claimed architecture, it maps the selected base-image
digest, Codex artifact, package set, capabilities, and disposable build result.
An architecture is not supported merely because an upstream manifest lists it.

The baseline contains the current template prerequisites—Git, Bash, Ruby with
YAML support, `jq`, Python 3.11 or later, and an authenticated GitHub CLI—plus
Codex, `bubblewrap`, IPv4/IPv6 firewall and DNS/probe tooling, and the
ShellCheck, actionlint, and repository-provided scaffold checks used by hosted
CI. Authentication is a runtime setup step, never an image-layer credential.
Rust, application SDKs, databases, organization tools, and other unmeasured
application runtimes are excluded from the generic baseline.

Every external image, Dev Container feature, package repository, package,
downloaded binary, and Codex artifact has immutable evidence appropriate to
its distribution mechanism: digest, exact version plus lockfile integrity,
checksum, or immutable repository snapshot. A human-readable tag may accompany
a digest but cannot replace it. Mutable `latest`-only features, unverified
installer pipes, and unlocked downloads are forbidden. Each pin records its
source and an explicit reviewed update path; an updater is not implemented by
this agreement.

### 6. Linked Git worktree behavior

The later implementation must exercise an actual linked Git worktree inside
the running container, not a copied fixture. The Git common and linked-worktree
administrative directories stay within the one workspace bind or named
volumes; they do not require another writable host bind. The design does not
mount the host home or a broad parent tree, and it resolves the worktree `.git`
pointer consistently inside the container.

Evidence performs `git status`, confirms the branch, creates and inspects a
diff, commits it, and records `git rev-parse --git-common-dir`. A new file
matching `.codex/agents/*.toml` must appear in `git status`. Container Git
configuration and global excludes may not hide `.codex/`, `.agents/`, or
another repository-owned ADLC surface; this explicitly excludes the broad
`.codex/` global-ignore pattern present in the provenance example.

### 7. Surface boundary

This contract covers a local Dev Container driven by Docker and a compatible
Dev Container client. Codex cloud uses OpenAI-managed isolation, setup, secret,
and network phases and is not this container. Compatibility with the Dev
Container specification does not establish GitHub Codespaces support. Neither
Codespaces nor another surface may be claimed without its own measured
evidence.

The later implementation Task is `risk:high` and must run on a
Docker/Dev-Container-capable surface. Runtime criteria cannot be deferred,
replaced by static inspection, or moved to a follow-up to complete that Task.

### 8. Required implementation evidence

Before the reference can be described as implemented or secure, one later Task
must record all of the following on its actual pull request head:

1. strict JSON parsing and Dev Container schema validation;
2. Bash syntax, ShellCheck, actionlint where applicable, and repository scaffold
   checks without new suppressions;
3. immutable-reference, checksum, lockfile, build-context, prohibited-flag, and
   trusted-control-manifest checks; negative fixtures alter the active config,
   add a host lifecycle command, mount, capability, mutable feature, or symlink,
   and prove the trusted external preflight refuses them before a mock Dev
   Container client can run;
4. an explicit `linux/amd64` and `linux/arm64` dependency/capability mapping;
5. a disposable image build for each supported architecture;
6. post-create and post-start smoke tests for every baseline tool, authenticated
   `gh`, Codex availability, and a functional `bubblewrap` sandbox;
7. allowed and blocked IPv4 and IPv6 firewall probes at startup, including
   fail-closed negative fixtures for resolution, rule, and probe failures, plus
   ordinary-agent mutation probes for `sudo`, capabilities, rules, sets, DNS,
   and allowlist files; the earliest repository-controlled lifecycle hook must
   run a blocked-egress fixture that proves policy was active before that hook,
   and arbitrary-name, alternate-resolver, DNS-over-TLS, and DNS-over-HTTPS
   probes must fail without leaking their randomized payload;
8. mount, named-volume, build-layer, build-context, environment, log, history,
   and secret inspection with no unexplained credential exposure;
9. the complete linked-worktree Git workflow and `.codex/agents/*.toml`
   visibility test described above; and
10. all hosted required GitHub checks on the tested commit, independent Codex
    review, and non-author human approval.

A successful static check does not substitute for a runtime item. Every result
links the command, architecture, image digest, tested commit, and observed
output in the GitHub Evidence ledger.

Items 6 through 9 run separately on both `linux/amd64` and `linux/arm64` using
native or otherwise hardware-backed execution representative of the claimed
runtime. A cross-build, manifest inspection, or QEMU-only build is not runtime
support evidence. No repository-controlled host lifecycle command may run
outside the container, and no in-container repository hook may precede the
root-owned policy bootstrap.

### 9. Provenance, licensing, and comparison exclusions

The implementation may study the pinned official reference and cite its
decisions, but it must be written originally for this repository under MIT and
must not copy or adapt OpenAI source files. If a future proposal needs verbatim
or adapted Apache-2.0 material, a separate human license decision must first
record exact derived-file boundaries, retain applicable copyright and NOTICE
material, preserve the Apache-2.0 terms, and provide modification attribution.
This ADR does not grant that decision and adds no attribution file.

Copilot comparison artifacts do not define the Codex contract. The reference
therefore excludes GitHub Copilot extensions and Copilot-only instructions,
prompts, agents, or setup behavior. It also excludes comparison-specific
ownership sentinels, contributor-only root `.devcontainer/**` assumptions, and
mutable feature references. GitHub-common Issues, pull requests, reviews,
checks, and rulesets remain applicable and are not removed for product purity.

## Consequences

- GitHub template distribution remains accurate while an adopter's active
  application container stays untouched.
- The contract requires two boundaries, least privilege, fail-closed
  networking, minimal credentials, and immutable dependencies over convenience;
  no secure or supported runtime claim exists until the later evidence passes.
- Supporting two architectures, linked worktrees, dual-stack probes, and
  supply-chain evidence increases implementation cost; unsupported or
  unmeasured behavior is reported rather than implied.
- Manual outer-boundary-only operation remains possible for a trusted
  repository, but it is visibly outside the safe default and carries the
  credential-exfiltration warning.
- The agreement creates no executable container and opens no network path. A
  separate high-risk Task and human merge are required before activation.

## References

- [OpenAI: Agent approvals and security — Run Codex in Dev Containers](https://learn.chatgpt.com/docs/agent-approvals-security#run-codex-in-dev-containers)
- [Pinned official Codex secure Dev Container reference](https://github.com/openai/codex/tree/45f8cafa4e2ec20f9b189d5aa9409e424b6d3d09/.devcontainer)
- [OpenAI Codex license at the pinned reference](https://github.com/openai/codex/blob/45f8cafa4e2ec20f9b189d5aa9409e424b6d3d09/LICENSE)
- [Codex Task #31](https://github.com/mochan-tk/ttt1-codex/issues/31)
- [Codex Task #29](https://github.com/mochan-tk/ttt1-codex/issues/29)
- [Copilot comparison PR #99](https://github.com/mochan-tk/ttt1-copilot/pull/99)
- [Copilot comparison PR #101](https://github.com/mochan-tk/ttt1-copilot/pull/101)
