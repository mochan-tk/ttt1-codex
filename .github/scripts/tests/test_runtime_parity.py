#!/usr/bin/env python3
"""Semantic regressions for the Codex-native runtime-parity contract."""

from __future__ import annotations

import pathlib
import re
import stat
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
SOURCE_SHA = "20637b703cbde6abd8934fc222abbe6c82bb4568"
SKILLS = (
    "context-collection",
    "context-distillation",
    "plan-management",
    "project-onboarding",
    "retro",
    "session-orchestration",
    "task-routing",
    "verification",
    "codex-automation",
)
CANONICAL = ROOT / ".agents/skills"
PACKAGED = ROOT / "plugin/agentic-dev-kit-for-codex/skills"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def assert_terms(
    case: unittest.TestCase,
    text: str,
    *terms: str,
) -> None:
    folded = re.sub(
        r"\s+", " ", text.casefold().replace("`", " ").replace("*", "")
    ).strip()
    for term in terms:
        with case.subTest(term=term):
            expected = re.sub(
                r"\s+", " ", term.casefold().replace("`", " ").replace("*", "")
            ).strip()
            case.assertIn(expected, folded)


class SourceTraceabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.capability_map = read(".github/docs/guides/copilot-capability-map.md")

    def test_latest_source_pin_and_110_file_inventory_are_explicit(self) -> None:
        self.assertIn(SOURCE_SHA, self.capability_map)
        rows = {
            "Root controls and distribution metadata": 6,
            "`.github/**`": 85,
            "`docs/**`": 15,
            "`.devcontainer/**`": 3,
            "`.vscode/mcp.json`": 1,
        }
        for area, count in rows.items():
            with self.subTest(area=area):
                self.assertRegex(
                    self.capability_map,
                    rf"\| {re.escape(area)} \| {count} \|",
                )
        self.assertEqual(110, sum(rows.values()))
        self.assertIn("| **Total** | **110** |", self.capability_map)

    def test_latest_source_behavior_deltas_are_traced(self) -> None:
        assert_terms(
            self,
            self.capability_map,
            "75a457dd5439b3d43fcc925881650b7bc4705b77",
            "gated cloud CI diagnosis",
            "action_required",
            SOURCE_SHA,
            "program session above Epic sessions",
            "sibling Epic parents",
        )

    def test_deferred_boundaries_are_not_overstated(self) -> None:
        assert_terms(
            self,
            self.capability_map,
            "Deferred to Task #35",
            "not claimed source-equivalent",
            "Task #33",
            "Neither open Task",
        )


class OrchestrationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = read(".agents/skills/session-orchestration/SKILL.md")
        self.architecture = read(".github/docs/guides/architecture.md")

    def test_task_session_is_sole_writer_and_subagents_are_read_only(self) -> None:
        assert_terms(
            self,
            self.session,
            "1 Task = 1 session = 1 worktree = 1 branch = 1 PR",
            "sole implementing writer",
            "independent, parallel",
            "read-only exploration",
            "receive no File ownership",
            "do not edit files",
            "run commands that write workspace artifacts",
            "Do not commit, push, open a PR, or implement",
            "authoritative Plan",
            "Report one hop",
            "Reports climb one hop",
            "independently rechecks",
            "read-only subagent reports one hop to the Task session",
            "Task session posts",
            "reports completion to the Epic parent",
            "Steer a running subagent",
            "Stop or cancel",
            "closing subagent threads",
            "close completed threads",
            "subagent descendants, read-only subagents, Task sessions, Epic parents, then the program",
        )
        session_folded = self.session.casefold()
        self.assertNotIn("disjoint implementation paths", session_folded)
        self.assertNotIn("parallel write-heavy work is safe", session_folded)
        self.assertNotIn("- owned paths:", session_folded)

        assert_terms(
            self,
            self.architecture,
            "1 Task = 1 session = 1 worktree = 1 branch = 1 PR",
            "sole implementing writer",
            "read-only subagent(s)",
            "exploration, review, or test observation",
            "receive no File ownership",
            "make no edits",
        )
        self.assertNotIn(
            "disjoint work to codex subagents", self.architecture.casefold()
        )

    def test_program_and_epic_parent_authority_are_separate(self) -> None:
        assert_terms(
            self,
            self.session,
            "Whole project / Epic set",
            "Epic-parent sessions are siblings",
            "never decomposes Tasks",
            "never spawns its successor",
            "replan the cross-phase blockage",
            "decomposed just in time",
            "their PRs are merged",
            "decomposition-state line is accurate",
        )
        assert_terms(
            self,
            self.architecture,
            "Program session (whole project; conductor of conductors)",
            "No Epic parent recursively spawns its successor",
        )

    def test_cloud_task_and_pr_ci_states_are_distinct(self) -> None:
        assert_terms(
            self,
            self.session,
            "cloud Task's own output and completion state",
            "resulting branch, commits, and PR head/diff",
            "PR workflow runs and checks",
            "action_required",
            "does not prove the Codex Task failed",
            "does not prove CI passed",
            "organization Actions approval boundary",
        )

    def test_custom_orchestrator_covers_both_read_only_layers(self) -> None:
        agent = read(".codex/agents/orchestrator.toml")
        self.assertRegex(agent, r'(?m)^name = "orchestrator"$')
        self.assertRegex(agent, r'(?m)^sandbox_mode = "read-only"$')
        assert_terms(
            self,
            agent,
            "Program layer",
            "Never decompose Tasks",
            "Epic-parent layer",
            "Decompose its phase",
            "Dispatch only",
            "Never implement Task-owned changes",
            "Name but do not start the next sibling Epic",
        )


class PlanningAndOnboardingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = read(".agents/skills/plan-management/SKILL.md")
        self.onboarding = read(".agents/skills/project-onboarding/SKILL.md")

    def test_phase_graph_and_current_decomposition_state_are_required(self) -> None:
        assert_terms(
            self,
            self.plan,
            "one coarse Epic per phase, all phase Epics siblings",
            "Never make an Epic a sub-issue of another Epic",
            "blocked-by edges between sibling Epics",
            "detail only the next executable Task wave",
            "Keep exactly one current state line",
            "replace the prior line rather than appending history",
            "Phase <name> decomposed on YYYY-MM-DD into Tasks",
        )

    def test_plugin_task_creation_stays_preview_first(self) -> None:
        assert_terms(
            self,
            self.plan,
            "plugin-only or partial installation",
            "new-task.sh --apply",
            "explicit authority for live Issue creation",
            "keep --dry-run output as the handoff",
            "never fabricate a control",
        )

    def test_all_runtime_skills_degrade_safely_without_full_kit(self) -> None:
        contracts = {
            "context-collection": (
                "plugin-only or partial installation",
                "Name the missing controls",
                "inspect supplied sources read-only",
                "return draft provenance headers",
                "Do not create .github/docs/context/",
                "Never fabricate a governed source",
            ),
            "context-distillation": (
                "plugin-only or partial installation",
                "name the missing controls",
                "Read only the supplied provenance-linked material",
                "return draft requirement",
                "Do not assign a live REQ-###",
                "Never fabricate a source",
            ),
            "session-orchestration": (
                "plugin-only or partial installation",
                "name the missing controls",
                "read-only assessment or draft text",
                "while any full-kit control is missing",
                "Separate authority alone does not make a partial installation safe",
                "Never fabricate a missing helper",
            ),
            "plan-management": (
                "plugin-only or partial installation",
                "list the missing controls",
                "read-only graph analysis",
                "never fabricate a control",
            ),
            "project-onboarding": (
                "plugin-only or partial installation",
                "Report which full-kit contracts are missing",
                "read-only repository assessment",
                "Do not invoke, fabricate, or silently substitute",
            ),
            "task-routing": (
                "plugin-only or partial installation",
                "name the missing controls",
                "Assess the supplied brief read-only",
                "return a draft Routing block",
                "Do not edit an Issue",
                "claim the route is durably recorded or enforced",
            ),
            "verification": (
                "plugin-only or partial installation",
                "name the missing controls",
                "Inspect supplied files, logs, diffs, and existing results read-only",
                "return a draft verification matrix",
                "Do not edit code",
                "Never fabricate Evidence",
            ),
            "retro": (
                "plugin-only or partial installation",
                "name the missing controls",
                "Inspect supplied occurrence links",
                "return a draft candidate Issue/comment",
                "Do not run a live gh issue mutation",
                "Never fabricate an occurrence",
            ),
            "codex-automation": (
                "skills-only plugin cannot install",
                "list what is missing",
                "read-only design or draft configuration",
                "Do not fabricate a Task gate",
            ),
        }
        for skill, terms in contracts.items():
            with self.subTest(skill=skill):
                text = read(f".agents/skills/{skill}/SKILL.md")
                assert_terms(self, text, *terms)
                assert_terms(
                    self,
                    text,
                    "missing control",
                    "restored and verified first",
                    "separate explicit",
                    "authority",
                )

        self.assertEqual(set(SKILLS), set(contracts))

    def test_onboarding_handoff_has_all_durable_carriers(self) -> None:
        assert_terms(
            self,
            self.onboarding,
            "## Deferred from onboarding",
            "unrun, unverified, declined, blocked, or external",
            "Append this ledger to the first-phase Epic",
            "A chat summary is not a carrier",
            "## Next steps",
            "The evidence PR body must end",
            "first phase first",
            "decompose its first Task wave",
        )


class CurrentProductBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.automation = read(".agents/skills/codex-automation/SKILL.md")
        self.patterns = read(
            ".agents/skills/codex-automation/references/supported-patterns.md"
        )
        self.migration = read(".github/docs/guides/migration-from-copilot.md")
        self.limitations = read(".github/docs/guides/limitations.md")

    def test_scheduled_task_surfaces_match_current_documentation(self) -> None:
        for text in (self.automation, self.limitations):
            assert_terms(
                self,
                text,
                "Scheduled tasks",
                "web",
                "desktop",
                "local project",
                "worktree",
                "CLI",
                "IDE",
                "no Scheduled management interface",
            )
        self.assertNotIn("app automation", self.automation.casefold())
        assert_terms(
            self,
            self.automation,
            "The computer must remain on",
            "the app must remain running",
            "Web Scheduled tasks",
            "cannot work directly in a local folder",
        )

    def test_hook_execution_limit_is_explicit(self) -> None:
        for text in (self.automation, self.patterns, self.limitations):
            assert_terms(
                self,
                text,
                'type: "command"',
                "prompt",
                "agent",
                "parsed",
                "skipped",
            )

    def test_copilot_import_is_manual_and_explorer_shadow_is_disclosed(self) -> None:
        assert_terms(
            self,
            self.migration,
            "manual migration",
            "does not list GitHub Copilot",
            "Do not tell adopters to use /import",
            "intentionally takes precedence over Codex's built-in explorer",
            "parent permission mode and live runtime overrides",
        )


class PluginSynchronizationTests(unittest.TestCase):
    def test_runtime_skill_trees_are_byte_and_mode_identical(self) -> None:
        for skill in SKILLS:
            canonical_root = CANONICAL / skill
            packaged_root = PACKAGED / skill
            canonical_files = {
                path.relative_to(canonical_root)
                for path in canonical_root.rglob("*")
                if path.is_file()
            }
            packaged_files = {
                path.relative_to(packaged_root)
                for path in packaged_root.rglob("*")
                if path.is_file()
            }
            with self.subTest(skill=skill, check="file set"):
                self.assertEqual(canonical_files, packaged_files)
            for relative in sorted(canonical_files):
                canonical = canonical_root / relative
                packaged = packaged_root / relative
                with self.subTest(skill=skill, path=relative.as_posix()):
                    self.assertEqual(canonical.read_bytes(), packaged.read_bytes())
                    self.assertEqual(
                        canonical.stat().st_mode & stat.S_IXUSR,
                        packaged.stat().st_mode & stat.S_IXUSR,
                    )


if __name__ == "__main__":
    unittest.main()
