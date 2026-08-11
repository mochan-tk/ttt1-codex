# Quickstart

Choose one adoption path. The full template and installer produce equivalent
core ADLC runtime and control capabilities; distribution metadata such as the
license and plugin artifact remains repository-only. The plugin is
intentionally skills-only.

## Prerequisites

- Git and Bash 3.2 or later;
- Ruby with its standard YAML parser, `jq`, and Python 3.11 or later;
- a current Codex app, CLI, IDE, or cloud surface with repository access;
- for live GitHub setup, `gh auth login --hostname github.com` with the Issue,
  label, and repository access required by the selected helper; and
- for Windows, Git for Windows so the PowerShell shim can invoke Git Bash.

Projects and rulesets additionally depend on account permissions and plan
availability. Preview paths do not require those live permissions.

## New repository: GitHub template

1. Create a repository with **Use this template**.
2. Clone it and open the root in Codex app, CLI, IDE, or cloud.
3. Confirm the copied instance is visibly untuned:

   ```bash
   .github/scripts/tuning-status.sh
   ```

4. Preview the canonical labels, then apply only after reviewing the plan:

   ```bash
   .github/scripts/setup-labels.sh --dry-run
   .github/scripts/setup-labels.sh --apply
   ```

5. Create the setup Epic and Task from the GitHub Issue forms. Ask Codex to use
   `$context-collection`, `$context-distillation`, and then
   `$project-onboarding`. The agreement merge precedes measured setup.

## Existing repository: safe installer

Preview from a local checkout of this kit without network access:

```bash
SCAFFOLD_SOURCE_DIR=/absolute/path/to/agentic-dev-kit-for-codex \
  bash /absolute/path/to/agentic-dev-kit-for-codex/.github/scripts/scaffold-init.sh \
  --dry-run /absolute/path/to/target
```

Run the same command without `--dry-run` only after reviewing collisions. A
fresh install refuses every collision by default, refuses symlinks even with
`--force`, stages files, and never commits. Use `--upgrade --dry-run` before an
upgrade; upgrade refreshes kit-owned machinery and preserves tuned surfaces
and project truth.

After a reviewed commit exists upstream, pin both the bootstrap script and its
payload to the same immutable commit:

```bash
KIT_COMMIT="replace-with-reviewed-40-hex-commit"
curl -fsSL "https://raw.githubusercontent.com/mochan-tk/ttt1-codex/$KIT_COMMIT/.github/scripts/scaffold-init.sh" \
  | SCAFFOLD_REF="$KIT_COMMIT" bash
```

Do not fetch the bootstrap from `main` in a repeatable organization rollout.
The installer also resolves its payload ref to a commit before download and
records that resolved SHA in `SCAFFOLD-CHANGELOG.md`.

## Skills-only plugin artifact

`plugin/agentic-dev-kit-for-codex/` is a validated Codex plugin containing the
nine reusable skills. It does not install `AGENTS.md`, GitHub workflows, Issue
forms, custom project agents, configuration, or setup scripts. Use the full
template or installer for the ADLC operating system.

The repository does not modify a personal or team marketplace. A maintainer
must publish or register the plugin through an approved marketplace before
`codex plugin add` can install it. Until then, treat it as a validated
distribution artifact, not as an already published plugin.

## First verification

```bash
git diff --check
git diff --cached --check
bash -n .github/scripts/*.sh .agents/skills/plan-management/scripts/*.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s .github/scripts/tests -p 'test_*.py' -v
.github/scripts/tests/run-portable-tests.sh
python3 .github/scripts/check_action_pins.py
.github/scripts/check-md-links.sh
.github/scripts/check-template-sync.sh
.github/scripts/check-skills.sh
.github/scripts/check-connectors.sh
.github/scripts/check-workflow-permissions.sh
```

Then run the target project's measured format, lint, type, test, build, and
security commands recorded by `$project-onboarding`.
