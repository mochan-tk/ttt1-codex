# Scaffold Changelog and Lineage

This file tracks releases of the reusable ADLC scaffolding. An instantiated
project keeps this file for upgrade provenance; its product changelog belongs
elsewhere.

**Template line:** Codex-native ADLC

**Current candidate:** v1.0.0

**Candidate state:** GitHub control-plane, Codex-native execution, repository
skills, CI, tuning visibility, and retro hygiene are implemented. The measured
license trial and human license merge are still required before release.

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
- the owner's 2026-08-03 decisions to compare platform-native outcomes rather
  than force cross-agent compatibility files, and to preserve GitHub as the
  mandatory ADLC control plane beneath Codex-native execution.

The candidate starts at v1.0.0; it does not inherit the old repository's Git
history or version numbers.

Implemented candidate surface:

- GitHub Issue forms, PR Evidence template, CODEOWNERS, Dependabot, and safe
  label, Project, and disabled-ruleset setup scripts;
- concise `AGENTS.md`, portable `.codex/` configuration, focused custom agents,
  and eight Codex-native workflows under `.agents/skills/`;
- deterministic Markdown, form/template, skill, compatibility-path,
  English-content, and shell checks;
- separate `quality` and `scaffold-self-check` CI jobs with third-party Actions
  pinned to complete commit SHAs; and
- report-only retro hygiene plus an explicitly authorized, idempotent monthly
  review Issue path. Issue-body edit-diff automation remains a candidate and is
  deliberately not implemented before a second occurrence.

Measure an instance before upgrade or license review:

```bash
scripts/tuning-status.sh
scripts/check-md-links.sh
scripts/check-template-sync.sh
scripts/check-skills.sh
scripts/retro-hygiene.sh
```

These commands report the current checkout; they do not enable a ruleset,
change repository settings, promote a retro candidate, or complete a human
merge gate.
