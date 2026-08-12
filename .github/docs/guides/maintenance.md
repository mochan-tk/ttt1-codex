# Maintenance and release procedure

## Change a skill

1. Edit the canonical `.agents/skills/<name>/` directory.
2. Keep `SKILL.md` frontmatter limited to `name` and a precise trigger-rich
   `description`.
3. Regenerate `agents/openai.yaml` with the skill-creator generator when its
   interface changes.
4. Copy the canonical skill byte-for-byte into
   `plugin/agentic-dev-kit-for-codex/skills/<name>/`.
5. Run the official skill validator and `.github/scripts/check-skills.sh`.

## Add a custom agent

Use current Codex custom-agent keys. The four bundled coordination agents must
retain read-only defaults, explicit no-write instructions, and only name,
description, sandbox mode, and developer instructions. Parent and user runtime
policy remains authoritative. A project-specific extension may add supported
fields, but the generic template rejects credentials, personal paths, and
concrete model pins.

## Add a connector

Copy `.github/connectors/CONNECTOR-TEMPLATE.md`, begin with
`status: experimental`, implement `discover`, `retrieve`, `pin`, and `verify`,
and add positive and negative conformance fixtures. Activation remains an
adopter-specific PR; adding a definition never activates a source.

## Upgrade an instance

```bash
SCAFFOLD_REF=<exact-tag-or-sha> \
  bash .github/scripts/scaffold-init.sh --upgrade --dry-run
SCAFFOLD_REF=<exact-tag-or-sha> \
  bash .github/scripts/scaffold-init.sh --upgrade
git diff --cached
```

Read `SCAFFOLD-CHANGELOG.md`. Reconcile preserved workflows, ownership,
constitution, config, agreements, and context manually. Run the instance's
measured product checks in addition to the scaffold suite.

## Release checklist

1. Confirm the worktree contains only intended changes and no secret or
   personal path.
2. Run all deterministic checks from the quickstart plus official skill and
   plugin validators.
3. Exercise installer scenarios in temporary repositories and inspect the
   staged file set.
4. Forward-test all nine skills with direct and indirect prompts; verify the
   four bundled agents are discoverable with read-only defaults and explicit
   no-write instructions.
5. Review the capability map against the pinned Copilot source commit.
6. Update version numbers in the changelog and plugin manifest together.
7. Produce archives/checksums only from a clean reviewed commit. Never claim a
   package or hash before the artifact exists.
8. Create the tag/release and verify the tag-resolved network installer in a
   disposable repository.
9. Publish or register the plugin marketplace entry separately if desired;
   repository release does not imply marketplace availability.

## Complete validation

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
.github/scripts/check-changelog-refs.sh
.github/scripts/check-escalation-wording.sh
.github/scripts/check-workflow-permissions.sh
.github/scripts/retro-hygiene.sh
.github/scripts/tuning-status.sh --ci
```
