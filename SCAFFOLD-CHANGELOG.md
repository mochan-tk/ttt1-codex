# Scaffold Changelog and Lineage

This file tracks releases of the reusable ADLC scaffolding. An instantiated
project keeps this file for upgrade provenance; its product changelog belongs
elsewhere.

**Template line:** Codex-native ADLC

**Current candidate:** v1.0.0

## Upgrade an instance

1. Add this template repository as a read-only remote and fetch its tags.
2. Diff the instance's adopted tag against the target tag.
3. Apply procedural, template, and gate changes while retaining the instance's
   project truth, commands, tool configuration, and agreements.
4. Run onboarding status and every scaffold self-check.
5. Land the upgrade as one reviewed `scaffold:` pull request and record any
   local deviations.

Example inspection flow:

```bash
git remote add scaffold https://github.com/mochan-tk/ttt1-codex.git
git fetch scaffold 'refs/tags/*:refs/tags/scaffold/*'
git diff scaffold/v1.0.0..scaffold/v1.1.0 -- . ':!docs/context' ':!docs/agreements'
```

Do not blindly replace `AGENTS.md`, `.codex/config.toml`, or agreement content
that the instance deliberately tuned. Inspect agreement changes separately,
then reconcile accepted changes through an agreement pull request:

```bash
git diff scaffold/v1.0.0..scaffold/v1.1.0 -- docs/agreements
```

## Upstream learning

When a retro fix is useful beyond one instance, propose the same change to this
template and link the originating Issue. The template owner alone decides
whether to merge it. Instances opt into later template versions; the template
does not push changes downstream automatically.

Each applicable instance PR records exactly one result:

- `upstream: proposed <url>`
- `upstream: not-applicable — <reason>`

## Versions

### v1.0.0 — candidate

Fresh-history Codex specialization consolidated from:

- `mochan-tk/tt1` main at `74b8b65` (v0.5.0), including the merged
  project-board linkage, Kind field, and infrastructure issue-first retro
  improvements;
- the proposed v0.6.0 semantics of `mochan-tk/tt1` PR #39 at `9450b52` for
  Task Issue plan-comment landing;
- the 2026-08-02 ADLC design review and ADR-0006; and
- the owner's 2026-08-03 decision to compare platform-native outcomes rather
  than force cross-agent compatibility files.

The candidate starts at v1.0.0; it does not inherit the old repository's Git
history or version numbers.
