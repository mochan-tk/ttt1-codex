#!/usr/bin/env python3
"""Regression fixtures for the deterministic CI guards."""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock
from urllib.error import URLError
from urllib.parse import parse_qs, urlsplit


ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".github/scripts"))

import check_action_pins as action_pins  # noqa: E402
import check_task_ritual as task_ritual  # noqa: E402


SHA_A = "1" * 40
SHA_B = "a" * 40
REPOSITORY = "example/project"
SERVER_URL = "https://github.com"

MOVED_DOC_PATHS = {
    ".github/docs/agreements/README.md",
    ".github/docs/agreements/adr/ADR-0001-codex-native-architecture.md",
    ".github/docs/agreements/adr/ADR-0002-adlc-operating-model.md",
    ".github/docs/agreements/glossary.md",
    ".github/docs/agreements/non-goals.md",
    ".github/docs/agreements/requirements.md",
    ".github/docs/agreements/retro-log.md",
    ".github/docs/context/README.md",
}
MOVED_SCRIPT_PATHS = {
    ".github/scripts/check-md-links.sh",
    ".github/scripts/check-skills.sh",
    ".github/scripts/check-template-sync.sh",
    ".github/scripts/check_action_pins.py",
    ".github/scripts/check_task_ritual.py",
    ".github/scripts/retro-hygiene.sh",
    ".github/scripts/setup-labels.sh",
    ".github/scripts/setup-project.sh",
    ".github/scripts/setup-ruleset.sh",
    ".github/scripts/tests/test_ci_guards.py",
    ".github/scripts/tuning-status.sh",
}
MOVED_SHELL_PATHS = {
    path for path in MOVED_SCRIPT_PATHS if path.endswith(".sh")
}


def comment(identifier: int, body: str, created_at: str, updated_at: str | None = None) -> dict:
    return {
        "id": identifier,
        "body": body,
        "created_at": created_at,
        "updated_at": updated_at or created_at,
    }


def commit(committed_at: str) -> dict:
    return {"commit": {"committer": {"date": committed_at}}}


def valid_fixture() -> dict:
    return {
        "pull_request": {
            "body": (
                "Closes #17\n\n"
                "Plan: https://github.com/example/project/issues/17#issuecomment-102\n"
            )
        },
        "issue": {"number": 17, "labels": [{"name": "type:task"}]},
        "comments": [
            comment(101, "## Start\n\n- Executor: test", "2026-08-05T01:00:00Z"),
            comment(102, "## Plan\n\n1. Verify first.", "2026-08-05T01:01:00Z"),
        ],
        "commits": [commit("2026-08-05T01:02:00Z")],
    }


def ritual_errors(fixture: dict) -> list[str]:
    arguments = (
        REPOSITORY,
        SERVER_URL,
        fixture["pull_request"],
        fixture["issue"],
        fixture["comments"],
        fixture["commits"],
    )
    if "comment_histories" in fixture:
        return task_ritual.validate_ritual(
            *arguments, comment_histories=fixture["comment_histories"]
        )
    return task_ritual.validate_ritual(*arguments)


class ActionPinTests(unittest.TestCase):
    def test_named_list_and_local_uses_forms_pass(self) -> None:
        text = f"""
jobs:
  test:
    steps:
      - name: Named step
        uses: actions/checkout@{SHA_A} # v4.2.2
      - uses: example/action@{SHA_B} # v1.0.0
      - uses: ./local-action
      - uses: "example/quoted@{SHA_A}" # v2.3.4
"""
        errors, count = action_pins.validate_workflow_text("fixture.yml", text)
        self.assertEqual([], errors)
        self.assertEqual(4, count)

    def test_tag_and_branch_fail_in_both_uses_forms(self) -> None:
        text = """
steps:
  - name: Named step
    uses: example/action@v1 # v1.0.0
  - uses: example/action@main # v1.0.0
"""
        errors, count = action_pins.validate_workflow_text("fixture.yaml", text)
        self.assertEqual(2, count)
        self.assertEqual(2, len(errors))
        self.assertTrue(all("40-hex" in error.message for error in errors))

    def test_missing_version_comment_fails(self) -> None:
        errors, count = action_pins.validate_workflow_text(
            "fixture.yml", f"steps:\n  - uses: example/action@{SHA_A}\n"
        )
        self.assertEqual(1, count)
        self.assertEqual(1, len(errors))
        self.assertIn("# vX.Y.Z", errors[0].message)

    def test_short_sha_fails_even_with_version_comment(self) -> None:
        errors, _ = action_pins.validate_workflow_text(
            "fixture.yml", "steps:\n  - uses: example/action@abc1234 # v1.2.3\n"
        )
        self.assertEqual(1, len(errors))
        self.assertIn("40-hex", errors[0].message)

    def test_discovery_requests_all_tracked_workflows(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                b".github/workflows/adopter-feedback.yml\0"
                b".github/workflows/ci.yml\0"
                b".github/workflows/retro-hygiene.yml\0"
            ),
        )
        with mock.patch.object(action_pins.subprocess, "run", return_value=completed) as run:
            paths = action_pins.tracked_workflow_paths(ROOT)
        self.assertEqual(
            [
                ROOT / ".github/workflows/adopter-feedback.yml",
                ROOT / ".github/workflows/ci.yml",
                ROOT / ".github/workflows/retro-hygiene.yml",
            ],
            paths,
        )
        command = run.call_args.args[0]
        self.assertEqual(
            ["git", "ls-files", "-z", "--", ".github/workflows"],
            command,
        )


class ScaffoldContractTests(unittest.TestCase):
    def test_controller_uses_the_runner_event_payload_path_directly(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        runner_name = "GITHUB_EVENT_PATH"
        obsolete_context = "github.event" + "_path"
        obsolete_alias = runner_name.removeprefix("GITHUB_")

        self.assertNotIn(obsolete_context, workflow)
        for shadowed_name in (runner_name, obsolete_alias):
            self.assertNotRegex(
                workflow,
                re.compile(rf"(?m)^\s+{re.escape(shadowed_name)}:"),
            )
        self.assertEqual(1, workflow.count(f'os.environ.get("{runner_name}")'))
        self.assertNotIn(f'os.environ.get("{obsolete_alias}")', workflow)

    def test_ci_rechecks_pull_request_body_edits_and_discovers_guard_tests(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertRegex(
            workflow,
            re.compile(
                r"(?m)^  pull_request_target:\n"
                r"    types: \[opened, synchronize, reopened, edited\]$"
            ),
        )
        self.assertRegex(
            workflow,
            re.compile(
                r"(?m)^  issue_comment:\n"
                r"    types: \[created, edited, deleted\]$"
            ),
        )
        self.assertNotRegex(
            workflow,
            re.compile(
                r"(?m)^  (?:pull_request|push|workflow_dispatch|merge_group):"
            ),
        )
        self.assertNotIn("concurrency:", workflow)
        self.assertIn("permissions: {}", workflow)
        self.assertIn("actions: read", workflow)
        self.assertIn("statuses: read", workflow)
        self.assertIn("def prior_authorization_binding(", workflow)
        discovery_command = (
            "python3 -m unittest discover -s .github/scripts/tests -p 'test_*.py' -v"
        )
        self.assertIn(discovery_command, workflow)

    def test_ci_lists_guard_and_action_pin_checks(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn(
            "python3 -m unittest discover -s .github/scripts/tests -p 'test_*.py' -v",
            workflow,
        )
        self.assertIn("python3 .github/scripts/check_action_pins.py", workflow)
        self.assertTrue((ROOT / ".github/docs/agreements/README.md").is_file())

    def test_ci_selectors_are_explicit_and_codeowners_preserves_workflow_coverage(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        codeowners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")

        self.assertIn("candidate-quality-worker:", workflow)
        self.assertIn("candidate-scaffold-worker:", workflow)
        self.assertIn("candidate-secure-runtime:", workflow)
        self.assertNotRegex(
            workflow,
            re.compile(
                r"(?m)^    name: (?:quality|scaffold-self-check|secure-devcontainer)$"
            ),
        )

    def test_candidate_workers_refuse_job_only_reruns_before_checkout(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        codeowners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")
        worker_names = (
            "candidate-quality-worker",
            "candidate-scaffold-worker",
            "candidate-secure-runtime",
        )
        job_starts = list(re.finditer(r"(?m)^  ([a-z0-9-]+):$", workflow))
        blocks = {}
        for index, match in enumerate(job_starts):
            end = (
                job_starts[index + 1].start()
                if index + 1 < len(job_starts)
                else len(workflow)
            )
            blocks[match.group(1)] = workflow[match.start() : end]
        for worker in worker_names:
            with self.subTest(worker=worker):
                block = blocks[worker]
                self.assertIn("github.run_attempt == 1", block)
                guard = block.index("Refuse job-only reruns before candidate checkout")
                checkout = block.index("uses: actions/checkout@")
                self.assertLess(guard, checkout)
                self.assertIn("RUN_ATTEMPT: ${{ github.run_attempt }}", block)
                self.assertIn('[[ "$RUN_ATTEMPT" == "1" ]]', block)
        self.assertEqual(
            3,
            workflow.count("Refuse job-only reruns before candidate checkout"),
        )
        scaffold = blocks["candidate-scaffold-worker"]
        self.assertIn("BASE_REPOSITORY: ${{ github.repository }}", scaffold)
        self.assertIn('GIT_TERMINAL_PROMPT: "0"', scaffold)
        self.assertIn("git -c credential.helper= fetch", scaffold)
        self.assertIn('"https://github.com/$BASE_REPOSITORY.git" "$ACCEPTED_BASE"', scaffold)
        self.assertNotIn("${{ github.token }}", scaffold)
        self.assertLess(
            scaffold.index("git -c credential.helper= fetch"),
            scaffold.index('git diff --check "$ACCEPTED_BASE" "$ACCEPTED_HEAD"'),
        )
        shell_selector = (
            "          scaffold_shells=()\n"
            "          while IFS= read -r -d '' path; do\n"
            "            case \"$path\" in\n"
            "              .github/scripts/*.sh|.agents/*.sh|.codex/devcontainer/*.sh)\n"
            "                scaffold_shells+=(\"$path\")\n"
            "                ;;\n"
            "            esac\n"
            "          done < <(git ls-files -z -- .github/scripts .agents .codex/devcontainer)\n"
            "          ((${#scaffold_shells[@]} > 0))"
        )
        self.assertEqual(2, workflow.count(shell_selector))
        self.assertNotIn("git ls-files -z '*.sh'", workflow)
        for forbidden in (
            "allow-unsafe-pr-checkout",
            "id-token: write",
            "secrets:",
            "environment:",
            "services:",
            "container:",
            "actions/cache@",
            "actions/upload-artifact@",
            "actions/download-artifact@",
            "github.event.pull_request.head",
        ):
            self.assertNotIn(forbidden, workflow)
        for job in (
            "candidate-quality-worker",
            "candidate-scaffold-worker",
            "candidate-secure-runtime",
        ):
            tail = workflow.split(f"  {job}:\n", 1)[1]
            block = re.split(r"(?m)^  [a-z][a-z0-9-]*:\s*$", tail, maxsplit=1)[0]
            self.assertIn("    permissions:\n      contents: read\n", block)
            self.assertNotIn("statuses: write", block)
            self.assertNotIn("issues: write", block)
            self.assertNotIn("pull-requests: write", block)
            self.assertIn("persist-credentials: false", block)
        actionlint_selector = (
            "          workflow_files=()\n"
            "          while IFS= read -r -d '' workflow_file; do\n"
            "            case \"$workflow_file\" in\n"
            "              *.yml|*.yaml) workflow_files+=(\"$workflow_file\") ;;\n"
            "            esac\n"
            "          done < <(git ls-files -z -- .github/workflows)"
        )
        self.assertEqual(1, workflow.count(actionlint_selector))
        self.assertIn('"$RUNNER_TEMP/actionlint" -color "${workflow_files[@]}"', workflow)
        self.assertNotIn(".github/workflows/*.yml", workflow)
        self.assertIn("/.github/docs/agreements/**", codeowners)
        self.assertIn("/.github/workflows/**", codeowners)
        self.assertIn(
            "/.github/workflows/**           @mochan-tk @liner-takashi-kawamoto",
            codeowners,
        )

    def test_canonical_namespace_tree_and_modes(self) -> None:
        tracked = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8").split("\0")
        tracked = {item for item in tracked if item}
        self.assertEqual([], [item for item in tracked if item.startswith(("docs/", "scripts/"))])
        self.assertLessEqual(MOVED_DOC_PATHS, tracked)
        self.assertLessEqual(MOVED_SCRIPT_PATHS, tracked)

        for relative in sorted(MOVED_SHELL_PATHS):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).stat().st_mode & stat.S_IXUSR)
        for relative in sorted(MOVED_SCRIPT_PATHS - MOVED_SHELL_PATHS):
            with self.subTest(path=relative):
                self.assertFalse((ROOT / relative).stat().st_mode & stat.S_IXUSR)


class NamespaceBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = pathlib.Path(self.temporary.name) / "repo"
        self.repo.mkdir()

        tracked = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8").split("\0")
        for item in (entry for entry in tracked if entry):
            source = ROOT / item
            if not source.is_file():
                continue
            destination = self.repo / item
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        self.run_command("git", "init", "-q", check=True)
        self.run_command("git", "add", "-f", "--all", check=True)

    def run_command(
        self,
        *command: str,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            list(command),
            cwd=self.repo,
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=30,
        )

    def track(self, relative: str, content: str, *, executable: bool = False) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if executable:
            path.chmod(0o755)
        self.run_command("git", "add", "-f", "--", relative, check=True)

    def run_guard(self, relative: str) -> subprocess.CompletedProcess[str]:
        return self.run_command(str(self.repo / relative))

    def check_ignore(self, relative: str) -> subprocess.CompletedProcess[str]:
        return self.run_command(
            "git",
            "-c",
            f"core.excludesFile={os.devnull}",
            "check-ignore",
            "-v",
            "--no-index",
            relative,
        )

    def test_session_plan_ignore_is_root_anchored(self) -> None:
        root = self.check_ignore("plan.md")
        root_output = root.stdout + root.stderr
        self.assertEqual(0, root.returncode, root_output)
        source, checked_path = root.stdout.rstrip("\n").split("\t")
        source_path, line_number, pattern = source.rsplit(":", 2)
        self.assertEqual(".gitignore", source_path)
        self.assertTrue(line_number.isdigit())
        self.assertEqual("/plan.md", pattern)
        self.assertEqual("plan.md", checked_path)
        self.assertEqual("", root.stderr)

        nested_plans = (
            "specs/001-feature/plan.md",
            ".github/docs/context/example/plan.md",
            "app/plan.md",
        )
        for relative in nested_plans:
            with self.subTest(path=relative):
                nested = self.check_ignore(relative)
                nested_output = nested.stdout + nested.stderr
                self.assertEqual(1, nested.returncode, nested_output)
                self.assertEqual("", nested_output)

    def test_application_and_unlisted_github_paths_are_outside_scope(self) -> None:
        japanese = "\u65e5\u672c\u8a9e"
        self.track("docs/app.md", f"{japanese}\n[broken](missing.md)\n")
        self.track("docs/example.agent.md", japanese + "\n")
        self.track("scripts/invalid.sh", "#!/usr/bin/env bash\nif then\n", executable=True)
        self.track(".github/app.md", f"{japanese}\n[broken](missing.md)\n")
        self.track(".github/docs-application/bad.md", japanese + "\n")
        self.track(
            ".github/ISSUE_TEMPLATE/custom.yml",
            "name: adopter\nbody: [\n",
        )
        skills = self.run_guard(".github/scripts/check-skills.sh")
        links = self.run_guard(".github/scripts/check-md-links.sh")
        templates = self.run_guard(".github/scripts/check-template-sync.sh")
        pins = self.run_command(sys.executable, ".github/scripts/check_action_pins.py")

        self.assertEqual(0, skills.returncode, skills.stdout + skills.stderr)
        self.assertEqual(0, links.returncode, links.stdout + links.stderr)
        self.assertEqual(0, templates.returncode, templates.stdout + templates.stderr)
        self.assertEqual(0, pins.returncode, pins.stdout + pins.stderr)
        self.assertIn("across 3 tracked workflow file(s)", pins.stdout)

    def test_named_control_content_fails_closed(self) -> None:
        japanese = "\u65e5\u672c\u8a9e"
        self.track(
            ".github/docs/context/bad.md",
            f"{japanese}\n[broken](missing.md)\n",
        )
        self.track(
            ".github/scripts/bad.sh",
            "#!/usr/bin/env bash\nif then\n",
            executable=True,
        )
        self.track(
            ".agents/skills/plan-management/scripts/bad.sh",
            "#!/usr/bin/env bash\nfor\n",
            executable=True,
        )
        self.track(".github/ISSUE_TEMPLATE/task.yml", "name: task\nbody: [\n")

        skills = self.run_guard(".github/scripts/check-skills.sh")
        links = self.run_guard(".github/scripts/check-md-links.sh")
        templates = self.run_guard(".github/scripts/check-template-sync.sh")
        skill_output = skills.stdout + skills.stderr
        link_output = links.stdout + links.stderr
        template_output = templates.stdout + templates.stderr

        self.assertEqual(1, skills.returncode, skill_output)
        self.assertIn(".github/docs/context/bad.md", skill_output)
        self.assertIn("persistent scaffold content must be English-only", skill_output)
        self.assertIn(".github/scripts/bad.sh: bash -n failed", skill_output)
        self.assertIn(
            ".agents/skills/plan-management/scripts/bad.sh: bash -n failed",
            skill_output,
        )
        self.assertEqual(1, links.returncode, link_output)
        self.assertIn(".github/docs/context/bad.md", link_output)
        self.assertIn("missing linked path: missing.md", link_output)
        self.assertEqual(1, templates.returncode, template_output)
        self.assertIn(".github/ISSUE_TEMPLATE/task.yml", template_output)
        self.assertIn("invalid YAML", template_output)

    def test_plugin_version_must_match_release_lineage(self) -> None:
        relative = "plugin/agentic-dev-kit-for-codex/.codex-plugin/plugin.json"
        manifest = (self.repo / relative).read_text(encoding="utf-8")
        manifest = re.sub(
            r'("version"\s*:\s*")[^"]+(")',
            lambda match: match.group(1) + "9.9.9" + match.group(2),
            manifest,
            count=1,
        )
        self.track(relative, manifest)

        result = self.run_guard(".github/scripts/check-skills.sh")
        output = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, output)
        self.assertIn("must match changelog current candidate", output)

    def test_additional_project_agent_is_an_extension_point(self) -> None:
        self.track(
            ".codex/agents/unexpected.toml",
            'name = "unexpected"\n'
            'description = "Unexpected fixture"\n'
            'sandbox_mode = "read-only"\n'
            'developer_instructions = "Read only."\n',
        )
        result = self.run_guard(".github/scripts/check-skills.sh")
        output = result.stdout + result.stderr
        self.assertEqual(0, result.returncode, output)

    def test_bundled_agent_contract_fails_closed(self) -> None:
        explorer = (self.repo / ".codex/agents/explorer.toml").read_text(
            encoding="utf-8"
        )
        self.track(
            ".codex/agents/explorer.toml",
            explorer + 'model = "organization-specific-model"\n',
        )
        result = self.run_guard(".github/scripts/check-skills.sh")
        output = result.stdout + result.stderr
        self.assertEqual(1, result.returncode, output)
        self.assertIn("model pin setting 'model' is not portable", output)

    def test_root_agents_contract_fails_closed(self) -> None:
        self.track("AGENTS.md", "\u65e5\u672c\u8a9e\n")
        result = self.run_guard(".github/scripts/check-skills.sh")
        output = result.stdout + result.stderr
        self.assertEqual(1, result.returncode, output)
        self.assertIn("AGENTS.md:1", output)
        self.assertIn("persistent scaffold content must be English-only", output)

    def test_every_tracked_workflow_is_checked(self) -> None:
        self.track(
            ".github/workflows/app.yml",
            "jobs:\n  app:\n    steps:\n      - uses: example/action@main\n",
        )
        sibling = self.run_command(sys.executable, ".github/scripts/check_action_pins.py")
        sibling_output = sibling.stdout + sibling.stderr
        self.assertEqual(1, sibling.returncode, sibling_output)
        self.assertIn(".github/workflows/app.yml", sibling_output)
        self.assertIn("40-hex", sibling_output)

        self.run_command("git", "rm", "--cached", "--", ".github/workflows/app.yml", check=True)
        (self.repo / ".github/workflows/app.yml").unlink()

        ci_path = self.repo / ".github/workflows/ci.yml"
        ci_text = ci_path.read_text(encoding="utf-8")
        ci_text = re.sub(
            r"actions/checkout@[0-9a-f]{40}",
            "actions/checkout@main",
            ci_text,
            count=1,
        )
        self.track(".github/workflows/ci.yml", ci_text)
        named = self.run_command(sys.executable, ".github/scripts/check_action_pins.py")
        output = named.stdout + named.stderr
        self.assertEqual(1, named.returncode, output)
        self.assertIn(".github/workflows/ci.yml", output)
        self.assertIn("40-hex", output)

    def test_missing_named_workflow_fails_closed(self) -> None:
        missing = ".github/workflows/retro-hygiene.yml"
        (self.repo / missing).unlink()
        self.run_command("git", "rm", "--cached", "--", missing, check=True)
        result = self.run_command(sys.executable, ".github/scripts/check_action_pins.py")
        output = result.stdout + result.stderr
        self.assertEqual(1, result.returncode, output)
        self.assertIn("required workflow(s) are not tracked", output)
        self.assertIn(missing, output)


class TaskRitualTests(unittest.TestCase):
    def test_valid_task_ritual_passes(self) -> None:
        self.assertEqual([], ritual_errors(valid_fixture()))

    def test_plan_heading_grammar_distinguishes_authority_from_audits(self) -> None:
        canonical = {
            "## Plan": "initial-plan",
            "## Plan (authoritative)": "initial-plan",
            "## Plan — bounded title": "initial-plan",
            "## Revised Plan": "revised-plan",
            "## Revised Plan 2": "revised-plan",
            "## Revised Plan v3": "revised-plan",
            "## Revised Plan v3.1": "revised-plan",
            "## Revised Plan clarification": "revised-plan",
            "## Revised Plan — bounded title": "revised-plan",
            "## Revised Plan 2 — bounded title": "revised-plan",
            "## Revised Plan v3.1 — bounded title": "revised-plan",
            "## Revised Plan clarification — bounded title": "revised-plan",
        }
        non_authority = (
            "## Plan v3 audit — superseded before approval",
            "## Plan audit",
            "## Plan status",
            "## Plan note",
            "## Plan superseded",
            "## Plan (draft)",
            "## Plan —",
            "## Plan - wrong dash",
            "## Revised Plan 0",
            "## Revised Plan v0",
            "## Revised Plan audit",
            "## Revised Plan note",
            "## Revised Plan superseded",
            "## Revised Plan —",
            "## revised Plan v3.1",
        )

        for heading, expected in canonical.items():
            with self.subTest(heading=heading):
                self.assertEqual(expected, task_ritual._comment_kind(f"{heading}\n\nDetails"))
        for heading in non_authority:
            with self.subTest(heading=heading):
                self.assertEqual("other", task_ritual._comment_kind(f"{heading}\n\nDetails"))

    def test_issue_35_audit_heading_is_not_plan_authority(self) -> None:
        fixture = {
            "pull_request": {
                "body": (
                    "Closes #35\n\n"
                    "Plan: https://github.com/example/project/issues/35"
                    "#issuecomment-5264223122\n"
                )
            },
            "issue": {"number": 35, "labels": [{"name": "type:task"}]},
            "comments": [
                comment(
                    5224368000,
                    "## Start — bootstrap ownership",
                    "2026-08-08T03:40:00Z",
                ),
                comment(
                    5224368411,
                    "## Plan — bootstrap the base-owned boundary",
                    "2026-08-08T03:51:28Z",
                ),
                comment(
                    5264209657,
                    "## Plan v3 audit — superseded before approval",
                    "2026-08-12T08:21:26Z",
                ),
                comment(
                    5264223122,
                    "## Revised Plan v3.1 — authoritative execution order",
                    "2026-08-12T08:22:44Z",
                ),
            ],
            "commits": [commit("2026-08-12T08:30:00Z")],
        }

        self.assertEqual([], ritual_errors(fixture))

    def test_audit_heading_does_not_satisfy_missing_initial_plan(self) -> None:
        fixture = valid_fixture()
        fixture["comments"][1] = comment(
            102,
            "## Plan v3 audit — superseded before approval",
            "2026-08-05T01:01:00Z",
        )

        self.assertIn("found 0", "\n".join(ritual_errors(fixture)))

    def test_later_audit_heading_does_not_steal_latest_revised_plan(self) -> None:
        fixture = valid_fixture()
        fixture["comments"].extend(
            [
                comment(
                    103,
                    "## Revised Plan v3.1 — final authority",
                    "2026-08-05T01:03:00Z",
                ),
                comment(
                    104,
                    "## Plan v3 audit — superseded before approval",
                    "2026-08-05T01:04:00Z",
                ),
            ]
        )
        fixture["pull_request"]["body"] = (
            "Closes #17\n\n"
            "Plan: https://github.com/example/project/issues/17#issuecomment-103\n"
        )

        self.assertEqual([], ritual_errors(fixture))

    def test_historical_canonical_plan_cannot_be_hidden_by_audit_heading(self) -> None:
        fixture = valid_fixture()
        fixture["comments"].append(
            comment(
                103,
                "## Plan v3 audit — superseded before approval",
                "2026-08-05T01:03:00Z",
                "2026-08-05T01:03:30Z",
            )
        )
        fixture["comment_histories"] = {
            103: [
                "## Plan v3 audit — superseded before approval",
                "## Plan — original authority",
            ]
        }

        errors = "\n".join(ritual_errors(fixture))
        self.assertIn("Plan/Revised Plan comments must never be edited", errors)
        self.assertIn("issuecomment-103", errors)

    def test_missing_task_link_fails(self) -> None:
        fixture = valid_fixture()
        fixture["pull_request"]["body"] = "Plan: https://github.com/example/project/issues/17#issuecomment-102\n"
        self.assertIn("exactly one canonical", "\n".join(ritual_errors(fixture)))

    def test_duplicate_task_links_fail(self) -> None:
        fixture = valid_fixture()
        fixture["pull_request"]["body"] += "Closes #18\n"
        self.assertIn("found 2", "\n".join(ritual_errors(fixture)))

    def test_closes_must_be_first_nonblank_not_a_code_fenced_example(self) -> None:
        fixture = valid_fixture()
        fixture["pull_request"]["body"] = (
            "```text\n"
            "Closes #17\n"
            "```\n\n"
            "Plan: https://github.com/example/project/issues/17#issuecomment-102\n"
        )
        self.assertIn("first nonblank", "\n".join(ritual_errors(fixture)))

    def test_closing_issue_must_be_task(self) -> None:
        fixture = valid_fixture()
        fixture["issue"]["labels"] = [{"name": "type:epic"}]
        errors = "\n".join(ritual_errors(fixture))
        self.assertIn("not labeled type:task", errors)
        self.assertIn("gh issue edit 17 --add-label type:task", errors)

    def test_missing_and_duplicate_plan_links_fail(self) -> None:
        missing = valid_fixture()
        missing["pull_request"]["body"] = "Closes #17\n"
        self.assertIn("Plan: URL; found 0", "\n".join(ritual_errors(missing)))

        duplicate = valid_fixture()
        duplicate["pull_request"]["body"] += (
            "Plan: https://github.com/example/project/issues/17#issuecomment-102\n"
        )
        self.assertIn("Plan: URL; found 2", "\n".join(ritual_errors(duplicate)))

    def test_plan_link_must_point_to_same_task(self) -> None:
        fixture = valid_fixture()
        fixture["pull_request"]["body"] = (
            "Closes #17\n\n"
            "Plan: https://github.com/example/project/issues/18#issuecomment-102\n"
        )
        self.assertIn("same repository and Task", "\n".join(ritual_errors(fixture)))

    def test_missing_claim_fails(self) -> None:
        fixture = valid_fixture()
        fixture["comments"] = fixture["comments"][1:]
        self.assertIn("no leading ## Start or ## Resume", "\n".join(ritual_errors(fixture)))

    def test_claim_must_precede_authoritative_plan(self) -> None:
        fixture = valid_fixture()
        fixture["comments"][0] = comment(
            101, "## Resume\n\n- Executor: successor", "2026-08-05T01:01:30Z"
        )
        self.assertIn("must precede", "\n".join(ritual_errors(fixture)))

    def test_edited_start_and_resume_claims_fail(self) -> None:
        for heading in ("## Start", "## Resume"):
            with self.subTest(heading=heading):
                fixture = valid_fixture()
                fixture["comments"][0] = comment(
                    101,
                    f"{heading}\n\n- Executor: test",
                    "2026-08-05T01:00:00Z",
                    "2026-08-05T01:00:30Z",
                )
                fixture["comment_histories"] = {
                    101: [
                        f"{heading}\n\n- Executor: test",
                        f"{heading}\n\n- Executor: original",
                    ]
                }
                errors = "\n".join(ritual_errors(fixture))
                self.assertIn("Start/Resume comments must never be edited", errors)

    def test_edited_start_cannot_be_hidden_by_clean_resume(self) -> None:
        fixture = valid_fixture()
        fixture["comments"][0] = comment(
            101,
            "## Note\n\n- The original Start heading was removed.",
            "2026-08-05T01:00:00Z",
            "2026-08-05T01:00:30Z",
        )
        fixture["comments"].append(
            comment(103, "## Resume\n\n- Executor: successor", "2026-08-05T01:03:00Z")
        )
        fixture["comment_histories"] = {
            101: [
                "## Note\n\n- The original Start heading was removed.",
                "## Start\n\n- Executor: original",
            ]
        }
        errors = "\n".join(ritual_errors(fixture))
        self.assertIn("issuecomment-101", errors)

    def test_edited_plan_cannot_be_hidden_by_clean_replacement(self) -> None:
        fixture = valid_fixture()
        fixture["comments"][1] = comment(
            102,
            "## Note\n\n- The original Plan heading was removed.",
            "2026-08-05T01:01:00Z",
            "2026-08-05T01:01:30Z",
        )
        fixture["comments"].append(
            comment(103, "## Plan\n\n1. Clean replacement.", "2026-08-05T01:02:00Z")
        )
        fixture["commits"] = [commit("2026-08-05T01:03:00Z")]
        fixture["pull_request"]["body"] = (
            "Closes #17\n\n"
            "Plan: https://github.com/example/project/issues/17#issuecomment-103\n"
        )
        fixture["comment_histories"] = {
            102: [
                "## Note\n\n- The original Plan heading was removed.",
                "## Plan\n\n1. Original plan.",
            ]
        }
        errors = "\n".join(ritual_errors(fixture))
        self.assertIn("Plan/Revised Plan comments must never be edited", errors)
        self.assertIn("issuecomment-102", errors)

    def test_late_claim_plus_later_revision_does_not_repair_initial_order(self) -> None:
        fixture = valid_fixture()
        fixture["comments"][0] = comment(
            101, "## Resume\n\n- Executor: successor", "2026-08-05T01:01:30Z"
        )
        fixture["comments"].append(
            comment(103, "## Revised Plan\n\n- Later revision.", "2026-08-05T01:03:00Z")
        )
        fixture["pull_request"]["body"] = (
            "Closes #17\n\n"
            "Plan: https://github.com/example/project/issues/17#issuecomment-103\n"
        )
        self.assertIn("precede the initial", "\n".join(ritual_errors(fixture)))

    def test_initial_plan_must_precede_earliest_commit(self) -> None:
        fixture = valid_fixture()
        fixture["commits"] = [commit("2026-08-05T01:00:30Z")]
        self.assertIn("predate the earliest", "\n".join(ritual_errors(fixture)))

    def test_later_revised_plan_is_latest_without_rewriting_initial_history(self) -> None:
        fixture = valid_fixture()
        fixture["comments"].append(
            comment(103, "## Revised Plan\n\n- Preserve initial history.", "2026-08-05T01:03:00Z")
        )
        fixture["pull_request"]["body"] = (
            "Closes #17\n\n"
            "Plan: https://github.com/example/project/issues/17#issuecomment-103\n"
        )
        self.assertEqual([], ritual_errors(fixture))

    def test_plan_link_must_point_to_latest_plan(self) -> None:
        fixture = valid_fixture()
        fixture["comments"].append(
            comment(103, "## Revised Plan 2\n\n- New authority.", "2026-08-05T01:03:00Z")
        )
        self.assertIn("latest Plan", "\n".join(ritual_errors(fixture)))

    def test_exactly_one_initial_plan_is_required(self) -> None:
        fixture = valid_fixture()
        fixture["comments"].append(
            comment(103, "## Plan\n\n- Duplicate initial plan.", "2026-08-05T01:01:30Z")
        )
        fixture["pull_request"]["body"] = (
            "Closes #17\n\n"
            "Plan: https://github.com/example/project/issues/17#issuecomment-103\n"
        )
        self.assertIn("exactly one leading ## Plan", "\n".join(ritual_errors(fixture)))

    def test_latest_plan_must_be_unedited(self) -> None:
        fixture = valid_fixture()
        fixture["comments"][1] = comment(
            102,
            "## Plan\n\n1. Edited in place.",
            "2026-08-05T01:01:00Z",
            "2026-08-05T01:01:30Z",
        )
        fixture["comment_histories"] = {
            102: ["## Plan\n\n1. Edited in place.", "## Plan\n\n1. Original plan."]
        }
        self.assertIn("must never be edited", "\n".join(ritual_errors(fixture)))

    def test_edited_initial_plan_cannot_be_hidden_by_clean_revision(self) -> None:
        fixture = valid_fixture()
        fixture["comments"][1] = comment(
            102,
            "## Plan\n\n1. Edited in place.",
            "2026-08-05T01:01:00Z",
            "2026-08-05T01:01:30Z",
        )
        fixture["comments"].append(
            comment(103, "## Revised Plan\n\n- Clean revision.", "2026-08-05T01:03:00Z")
        )
        fixture["pull_request"]["body"] = (
            "Closes #17\n\n"
            "Plan: https://github.com/example/project/issues/17#issuecomment-103\n"
        )
        fixture["comment_histories"] = {
            102: ["## Plan\n\n1. Edited in place.", "## Plan\n\n1. Original plan."]
        }
        self.assertIn("issuecomment-102", "\n".join(ritual_errors(fixture)))

    def test_bot_metadata_does_not_bypass_missing_ritual(self) -> None:
        fixture = valid_fixture()
        fixture["pull_request"]["user"] = {"login": "dependabot[bot]", "type": "Bot"}
        fixture["comments"] = []
        errors = "\n".join(ritual_errors(fixture))
        self.assertIn("no leading ## Start", errors)
        self.assertIn("exactly one leading ## Plan", errors)


class ApiRetryTests(unittest.TestCase):
    def test_transient_api_error_is_retried(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=3, sleeper=lambda _: None)
        with mock.patch.object(
            client,
            "_request_once",
            side_effect=[URLError("temporary"), {"ok": True}],
        ) as request:
            self.assertEqual({"ok": True}, client.get_json("example"))
        self.assertEqual(2, request.call_count)

    def test_repeated_api_error_fails_closed(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=3, sleeper=lambda _: None)
        with mock.patch.object(client, "_request_once", side_effect=URLError("offline")) as request:
            with self.assertRaises(task_ritual.ApiError):
                client.get_json("example")
        self.assertEqual(3, request.call_count)

    def test_graphql_error_response_is_retried(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=3, sleeper=lambda _: None)
        with mock.patch.object(
            client,
            "_graphql_once",
            side_effect=[{"errors": [{"message": "temporary"}]}, {"data": {"ok": True}}],
        ) as request:
            self.assertEqual(
                {"data": {"ok": True}},
                client.post_graphql("query { ok }", {}),
            )
        self.assertEqual(2, request.call_count)

    def test_edit_state_reads_every_comment_and_requires_created_snapshot(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        payload = {
            "data": {
                "nodes": [
                    {
                        "id": "IC_clean",
                        "body": "## Start",
                        "lastEditedAt": None,
                        "includesCreatedEdit": False,
                        "userContentEdits": {"totalCount": 0},
                    },
                    {
                        "id": "IC_edited",
                        "body": "## Note",
                        "lastEditedAt": "2026-08-05T01:00:00Z",
                        "includesCreatedEdit": True,
                        "userContentEdits": {"totalCount": 2},
                    },
                ]
            }
        }
        with mock.patch.object(client, "_graphql_once", return_value=payload):
            states = client.get_issue_comment_edit_states(["IC_clean", "IC_edited"])
        self.assertFalse(states["IC_clean"].edited)
        self.assertTrue(states["IC_edited"].edited)
        self.assertEqual(2, states["IC_edited"].total_count)

    def test_edit_state_fails_closed_when_creation_snapshot_is_missing(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        payload = {
            "data": {
                "nodes": [
                    {
                        "id": "IC_edited",
                        "body": "## Note",
                        "lastEditedAt": "2026-08-05T01:00:00Z",
                        "includesCreatedEdit": False,
                        "userContentEdits": {"totalCount": 2},
                    }
                ]
            }
        }
        with mock.patch.object(client, "_graphql_once", return_value=payload):
            with self.assertRaises(task_ritual.ApiError):
                client.get_issue_comment_edit_states(["IC_edited"])

    def test_edit_state_fails_closed_on_partial_node(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        with mock.patch.object(
            client,
            "_graphql_once",
            return_value={"data": {"nodes": [None]}},
        ):
            with self.assertRaises(task_ritual.ApiError):
                client.get_issue_comment_edit_states(["IC_missing"])

    def test_edit_state_batches_at_the_graphql_limit(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        node_ids = [f"IC_{index}" for index in range(101)]

        def payload(ids: list[str]) -> dict:
            return {
                "data": {
                    "nodes": [
                        {
                            "id": identifier,
                            "body": "## Note",
                            "lastEditedAt": None,
                            "includesCreatedEdit": False,
                            "userContentEdits": {"totalCount": 0},
                        }
                        for identifier in ids
                    ]
                }
            }

        responses = [payload(node_ids[:100]), payload(node_ids[100:])]
        with mock.patch.object(client, "post_graphql", side_effect=responses) as request:
            states = client.get_issue_comment_edit_states(node_ids)
        self.assertEqual(101, len(states))
        self.assertEqual(
            [100, 1],
            [len(call.args[1]["ids"]) for call in request.call_args_list],
        )

    def test_issue_comment_history_returns_complete_snapshots(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        payload = {
            "data": {
                "node": {
                    "body": "## Note",
                    "lastEditedAt": "2026-08-05T01:00:00Z",
                    "includesCreatedEdit": True,
                    "userContentEdits": {
                        "totalCount": 2,
                        "nodes": [{"diff": "## Note"}, {"diff": "## Start"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor-2"},
                    }
                }
            }
        }
        with mock.patch.object(client, "_graphql_once", return_value=payload):
            self.assertEqual(
                ["## Note", "## Start"],
                client.get_issue_comment_history("IC_fixture"),
            )

    def test_issue_comment_history_aggregates_multiple_pages(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        first = {
            "data": {
                "node": {
                    "body": "## Note",
                    "lastEditedAt": "2026-08-05T01:00:00Z",
                    "includesCreatedEdit": True,
                    "userContentEdits": {
                        "totalCount": 2,
                        "nodes": [{"diff": "## Note"}],
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                    },
                }
            }
        }
        second = {
            "data": {
                "node": {
                    "body": "## Note",
                    "lastEditedAt": "2026-08-05T01:00:00Z",
                    "includesCreatedEdit": True,
                    "userContentEdits": {
                        "totalCount": 2,
                        "nodes": [{"diff": "## Start"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor-2"},
                    }
                }
            }
        }
        with mock.patch.object(client, "_graphql_once", side_effect=[first, second]) as request:
            self.assertEqual(
                ["## Note", "## Start"],
                client.get_issue_comment_history("IC_fixture"),
            )
        self.assertEqual("cursor-1", request.call_args_list[1].args[1]["after"])

    def test_issue_comment_history_fails_closed_on_single_snapshot(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        payload = {
            "data": {
                "node": {
                    "body": "## Note",
                    "lastEditedAt": "2026-08-05T01:00:00Z",
                    "includesCreatedEdit": True,
                    "userContentEdits": {
                        "totalCount": 1,
                        "nodes": [{"diff": "## Note"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor-1"},
                    },
                }
            }
        }
        with mock.patch.object(client, "_graphql_once", return_value=payload):
            with self.assertRaises(task_ritual.ApiError):
                client.get_issue_comment_history("IC_fixture")

    def test_issue_comment_history_fails_closed_on_cursor_stall(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        page = {
            "data": {
                "node": {
                    "body": "## Note",
                    "lastEditedAt": "2026-08-05T01:00:00Z",
                    "includesCreatedEdit": True,
                    "userContentEdits": {
                        "totalCount": 3,
                        "nodes": [{"diff": "## Note"}],
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                    },
                }
            }
        }
        with mock.patch.object(client, "_graphql_once", return_value=page):
            with self.assertRaises(task_ritual.ApiError):
                client.get_issue_comment_history("IC_fixture")

    def test_issue_comment_history_requires_current_body_snapshot(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        payload = {
            "data": {
                "node": {
                    "body": "## Note",
                    "lastEditedAt": "2026-08-05T01:00:00Z",
                    "includesCreatedEdit": True,
                    "userContentEdits": {
                        "totalCount": 2,
                        "nodes": [{"diff": "summary"}, {"diff": "## Start"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor-2"},
                    },
                }
            }
        }
        with mock.patch.object(client, "_graphql_once", return_value=payload):
            with self.assertRaises(task_ritual.ApiError):
                client.get_issue_comment_history("IC_fixture")

    def test_issue_comment_history_rejects_state_change_between_queries(self) -> None:
        client = task_ritual.GitHubApi("token", attempts=1)
        payload = {
            "data": {
                "node": {
                    "body": "## Note",
                    "lastEditedAt": "2026-08-05T01:02:00Z",
                    "includesCreatedEdit": True,
                    "userContentEdits": {
                        "totalCount": 2,
                        "nodes": [{"diff": "## Note"}, {"diff": "## Start"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor-2"},
                    },
                }
            }
        }
        earlier_state = task_ritual.CommentEditState(
            "## Note", "2026-08-05T01:00:00Z", 2
        )
        with mock.patch.object(client, "_graphql_once", return_value=payload):
            with self.assertRaises(task_ritual.ApiError):
                client.get_issue_comment_history("IC_fixture", earlier_state)

    def test_history_fetch_detects_same_second_content_edit(self) -> None:
        comments = [
            {**comment(101, "## Start", "2026-08-05T01:00:00Z"), "node_id": "IC_clean"},
            {
                **comment(102, "## Note", "2026-08-05T01:01:00Z"),
                "node_id": "IC_edited",
            },
        ]
        api = mock.Mock()
        clean_state = task_ritual.CommentEditState("## Start", None, 0)
        edited_state = task_ritual.CommentEditState(
            "## Note", "2026-08-05T01:01:00Z", 2
        )
        api.get_issue_comment_edit_states.return_value = {
            "IC_clean": clean_state,
            "IC_edited": edited_state,
        }
        api.get_issue_comment_history.return_value = ["## Note", "## Plan"]
        self.assertEqual(
            {102: ["## Note", "## Plan"]},
            task_ritual.fetch_comment_histories(api, comments),
        )
        api.get_issue_comment_edit_states.assert_called_once_with(["IC_clean", "IC_edited"])
        api.get_issue_comment_history.assert_called_once_with("IC_edited", edited_state)

    def test_history_fetch_ignores_non_content_update(self) -> None:
        comments = [
            {
                **comment(
                    101,
                    "## Start",
                    "2026-08-05T01:00:00Z",
                    "2026-08-05T01:00:30Z",
                ),
                "node_id": "IC_clean",
            }
        ]
        api = mock.Mock()
        api.get_issue_comment_edit_states.return_value = {
            "IC_clean": task_ritual.CommentEditState("## Start", None, 0)
        }
        self.assertEqual({}, task_ritual.fetch_comment_histories(api, comments))
        api.get_issue_comment_history.assert_not_called()

    def test_history_fetch_fails_fast_above_global_page_budget(self) -> None:
        comments = [
            {**comment(101, "## Note", "2026-08-05T01:00:00Z"), "node_id": "IC_1"},
            {**comment(102, "## Note", "2026-08-05T01:01:00Z"), "node_id": "IC_2"},
        ]
        api = mock.Mock()
        api.get_issue_comment_edit_states.return_value = {
            "IC_1": task_ritual.CommentEditState("## Note", "2026-08-05T01:00:00Z", 2),
            "IC_2": task_ritual.CommentEditState("## Note", "2026-08-05T01:01:00Z", 2),
        }
        with mock.patch.object(task_ritual, "MAX_TOTAL_HISTORY_PAGES", 1):
            with self.assertRaises(task_ritual.ApiError):
                task_ritual.fetch_comment_histories(api, comments)
        api.get_issue_comment_history.assert_not_called()

    def test_history_fetch_rejects_rest_graphql_body_mismatch(self) -> None:
        comments = [
            {**comment(101, "## Note", "2026-08-05T01:00:00Z"), "node_id": "IC_1"}
        ]
        api = mock.Mock()
        api.get_issue_comment_edit_states.return_value = {
            "IC_1": task_ritual.CommentEditState("changed body", None, 0)
        }
        with self.assertRaises(task_ritual.ApiError):
            task_ritual.fetch_comment_histories(api, comments)

    def test_history_fetch_fails_closed_without_node_id(self) -> None:
        comments = [
            comment(
                102,
                "## Note",
                "2026-08-05T01:01:00Z",
                "2026-08-05T01:01:30Z",
            )
        ]
        with self.assertRaises(task_ritual.ApiError):
            task_ritual.fetch_comment_histories(mock.Mock(), comments)


def embedded_task35_controller() -> str:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    begin = "          # TASK35_PROGRAM_BEGIN controller\n"
    end = "          # TASK35_PROGRAM_END controller\n"
    self_contained = workflow.split(begin, 1)
    if len(self_contained) != 2 or workflow.count(begin) != 1 or workflow.count(end) != 1:
        raise AssertionError("Task #35 controller sentinels are missing or ambiguous")
    block = self_contained[1].split(end, 1)[0]
    heredoc = "          python3 -I - <<'PY'\n"
    terminator = "          PY\n"
    if not block.startswith(heredoc) or not block.endswith(terminator):
        raise AssertionError("Task #35 controller is not the expected Python heredoc")
    return textwrap.dedent(block[len(heredoc) : -len(terminator)])


class FakeTask35GitHub:
    repository = "example/project"
    repository_id = 100
    pr_number = 7
    head_sha = "1" * 40
    base_sha = "a" * 40

    def __init__(self) -> None:
        self.head_repository = self.repository
        self.head_repository_id = self.repository_id
        self.permission = "write"
        self.permissions: dict[str, str] = {}
        self.files: list[dict] = [{"filename": "src/app.py", "status": "modified"}]
        self.comments: list[dict] = []
        self.pr_calls = 0
        self.drift_after_pr_call: int | None = None
        self.pr_overrides_by_call: dict[int, dict[str, object]] = {}
        self.files_calls = 0
        self.files_by_call: dict[int, list[dict]] = {}
        self.changed_files_override: int | None = None
        self.default_branch = "main"
        self.repository_metadata_id = self.repository_id
        self.malformed_files_link = False
        self.files_page_size: int | None = None
        self.comments_page_size: int | None = None
        self.statuses_page_size: int | None = None
        self.runs_page_size: int | None = None
        self.jobs_page_size: int | None = None
        self.files_link_override: str | None = None
        self.fail_get_suffix: str | None = None
        self.graphql_error = False
        self.status_posts: list[dict] = []
        self.commit_statuses: list[dict] = []
        self.status_failure_at: int | None = None
        self.status_commit_then_failure_at: int | None = None
        self.status_response_overrides: dict[str, object] = {}
        self.runs: list[dict] = []
        self.jobs: dict[int, list[dict]] = {}
        self.jobs_by_filter: dict[tuple[int, str], list[dict]] = {}
        self.cancelled: list[int] = []
        self.requests: list[tuple[str, str, object]] = []
        self.server: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    def pull_request(self) -> dict:
        self.pr_calls += 1
        head = self.head_sha
        if self.drift_after_pr_call is not None and self.pr_calls > self.drift_after_pr_call:
            head = "2" * 40
        result = {
            "number": self.pr_number,
            "state": "open",
            "changed_files": (
                self.changed_files_override
                if self.changed_files_override is not None
                else len(self.files)
            ),
            "head": {
                "sha": head,
                "ref": "feature/task-35",
                "repo": {
                    "id": self.head_repository_id,
                    "full_name": self.head_repository,
                },
            },
            "base": {
                "sha": self.base_sha,
                "ref": "main",
                "repo": {"id": self.repository_id, "full_name": self.repository},
            },
            "user": {"id": 11, "login": "pull-author", "type": "User"},
        }
        override = self.pr_overrides_by_call.get(self.pr_calls, {})
        if "number" in override:
            result["number"] = override["number"]
        if "state" in override:
            result["state"] = override["state"]
        if "changed_files" in override:
            result["changed_files"] = override["changed_files"]
        for side in ("head", "base"):
            for field in ("sha", "ref"):
                key = f"{side}_{field}"
                if key in override:
                    result[side][field] = override[key]
            for field in ("id", "full_name"):
                key = f"{side}_repo_{field}"
                if key in override:
                    result[side]["repo"][field] = override[key]
        for field in ("id", "login", "type"):
            key = f"author_{field}"
            if key in override:
                result["user"][field] = override[key]
        return result

    def authorization_comment(self, identifier: int = 501) -> dict:
        return {
            "id": identifier,
            "node_id": f"IC_{identifier}",
            "body": f"/authorize-secure-devcontainer-runtime {self.head_sha}",
            "created_at": "2026-08-12T01:00:00Z",
            "updated_at": "2026-08-12T01:00:00Z",
            "issue_url": f"PLACEHOLDER/repos/{self.repository}/issues/{self.pr_number}",
            "user": {"id": 22, "login": "reviewer", "type": "User"},
        }

    def diff_digest(self) -> str:
        records = []
        for item in self.files:
            records.append(
                (
                    item["status"],
                    item["filename"],
                    item.get("previous_filename", ""),
                )
            )
        return hashlib.sha256(
            json.dumps(sorted(records), separators=(",", ":")).encode("utf-8")
        ).hexdigest()

    def event(self, event_name: str = "pull_request_target", action: str = "opened") -> dict:
        base = {
            "action": action,
            "repository": {"id": self.repository_id, "full_name": self.repository},
        }
        if event_name == "pull_request_target":
            base["pull_request"] = {"number": self.pr_number}
        else:
            base["issue"] = {
                "number": self.pr_number,
                "pull_request": {"url": "https://example.invalid/pull/7"},
            }
            if self.comments:
                base["comment"] = self.comments[0]
        return base

    def __enter__(self) -> "FakeTask35GitHub":
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, _format: str, *_args: object) -> None:
                return

            def send_json(
                self,
                payload: object,
                status: int = 200,
                headers: dict[str, str] | None = None,
            ) -> None:
                raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                for key, value in (headers or {}).items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(raw)

            def read_json(self) -> object:
                length = int(self.headers.get("Content-Length", "0"))
                return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

            def do_GET(self) -> None:  # noqa: N802
                parsed = urlsplit(self.path)
                path = parsed.path
                fixture.requests.append(("GET", self.path, None))
                if fixture.fail_get_suffix and path.endswith(fixture.fail_get_suffix):
                    self.send_json({"message": "injected GET failure"}, status=500)
                    return
                if path == f"/repos/{fixture.repository}":
                    self.send_json(
                        {
                            "id": fixture.repository_metadata_id,
                            "full_name": fixture.repository,
                            "default_branch": fixture.default_branch,
                            "owner": {
                                "id": 1,
                                "login": fixture.repository.split("/", 1)[0],
                                "type": "Organization",
                            },
                        }
                    )
                    return
                if path == f"/repos/{fixture.repository}/pulls/{fixture.pr_number}":
                    self.send_json(fixture.pull_request())
                    return
                if path == f"/repos/{fixture.repository}/pulls/{fixture.pr_number}/files":
                    headers = {"Link": "not-a-valid-link"} if fixture.malformed_files_link else {}
                    fixture.files_calls += 1
                    source_files = fixture.files_by_call.get(
                        fixture.files_calls, fixture.files
                    )
                    page = int(parse_qs(parsed.query).get("page", ["1"])[0])
                    if fixture.files_page_size is not None:
                        start = (page - 1) * fixture.files_page_size
                        records = source_files[start : start + fixture.files_page_size]
                        if start + fixture.files_page_size < len(source_files):
                            headers["Link"] = (
                                f'<{fixture.url}{path}?per_page=100&page={page + 1}>; rel="next"'
                            )
                    else:
                        records = source_files
                    if fixture.files_link_override is not None:
                        headers["Link"] = fixture.files_link_override
                    self.send_json(records, headers=headers)
                    return
                if path == f"/repos/{fixture.repository}/issues/{fixture.pr_number}/comments":
                    page = int(parse_qs(parsed.query).get("page", ["1"])[0])
                    headers = {}
                    if fixture.comments_page_size is not None:
                        start = (page - 1) * fixture.comments_page_size
                        records = fixture.comments[
                            start : start + fixture.comments_page_size
                        ]
                        if start + fixture.comments_page_size < len(fixture.comments):
                            headers["Link"] = (
                                f'<{fixture.url}{path}?per_page=100&page={page + 1}>; rel="next"'
                            )
                    else:
                        records = fixture.comments
                    self.send_json(records, headers=headers)
                    return
                if path == f"/repos/{fixture.repository}/commits/{fixture.head_sha}/statuses":
                    page = int(parse_qs(parsed.query).get("page", ["1"])[0])
                    headers = {}
                    if fixture.statuses_page_size is not None:
                        start = (page - 1) * fixture.statuses_page_size
                        records = fixture.commit_statuses[
                            start : start + fixture.statuses_page_size
                        ]
                        if start + fixture.statuses_page_size < len(fixture.commit_statuses):
                            headers["Link"] = (
                                f'<{fixture.url}{path}?per_page=100&page={page + 1}>; rel="next"'
                            )
                    else:
                        records = fixture.commit_statuses
                    self.send_json(records, headers=headers)
                    return
                if path.startswith(f"/repos/{fixture.repository}/collaborators/"):
                    login = path.rsplit("/", 2)[-2]
                    author = next(
                        (
                            item.get("user")
                            for item in fixture.comments
                            if isinstance(item.get("user"), dict)
                            and item["user"].get("login") == login
                        ),
                        {"id": 22, "login": login, "type": "User"},
                    )
                    self.send_json(
                        {
                            "permission": fixture.permissions.get(
                                login, fixture.permission
                            ),
                            "user": author,
                        }
                    )
                    return
                comment_prefix = f"/repos/{fixture.repository}/issues/comments/"
                if path.startswith(comment_prefix):
                    identifier = int(path.removeprefix(comment_prefix))
                    found = next((item for item in fixture.comments if item["id"] == identifier), None)
                    if found is None:
                        self.send_json({"message": "Not Found"}, status=404)
                    else:
                        self.send_json(found)
                    return
                if path == f"/repos/{fixture.repository}/actions/workflows/ci.yml/runs":
                    status_filter = parse_qs(parsed.query).get("status", [None])[0]
                    page = int(parse_qs(parsed.query).get("page", ["1"])[0])
                    headers = {}
                    records = [
                        item
                        for item in fixture.runs
                        if status_filter is None or item.get("status") == status_filter
                    ]
                    if fixture.runs_page_size is not None:
                        start = (page - 1) * fixture.runs_page_size
                        selected = records
                        records = selected[start : start + fixture.runs_page_size]
                        if start + fixture.runs_page_size < len(selected):
                            headers["Link"] = (
                                f'<{fixture.url}{path}?status={status_filter}&per_page=100&page={page + 1}>; rel="next"'
                            )
                    self.send_json(
                        {
                            "total_count": len(
                                [
                                    item
                                    for item in fixture.runs
                                    if status_filter is None
                                    or item.get("status") == status_filter
                                ]
                            ),
                            "workflow_runs": records,
                        },
                        headers=headers,
                    )
                    return
                run_detail = re.fullmatch(
                    rf"/repos/{re.escape(fixture.repository)}/actions/runs/([1-9][0-9]*)",
                    path,
                )
                if run_detail:
                    identifier = int(run_detail.group(1))
                    found = next(
                        (item for item in fixture.runs if item.get("id") == identifier),
                        None,
                    )
                    if found is None:
                        self.send_json({"message": "Not Found"}, status=404)
                    else:
                        response = {
                            **found,
                            "repository": {
                                "id": fixture.repository_id,
                                "full_name": fixture.repository,
                            },
                        }
                        self.send_json(response)
                    return
                run_jobs = re.fullmatch(
                    rf"/repos/{re.escape(fixture.repository)}/actions/runs/([1-9][0-9]*)/jobs",
                    path,
                )
                if run_jobs:
                    identifier = int(run_jobs.group(1))
                    filter_value = parse_qs(parsed.query).get("filter", ["latest"])[0]
                    jobs = fixture.jobs_by_filter.get(
                        (identifier, filter_value), fixture.jobs.get(identifier, [])
                    )
                    page = int(parse_qs(parsed.query).get("page", ["1"])[0])
                    headers = {}
                    records = jobs
                    if fixture.jobs_page_size is not None:
                        start = (page - 1) * fixture.jobs_page_size
                        records = jobs[start : start + fixture.jobs_page_size]
                        if start + fixture.jobs_page_size < len(jobs):
                            headers["Link"] = (
                                f'<{fixture.url}{path}?filter={filter_value}&per_page=100&page={page + 1}>; rel="next"'
                            )
                    self.send_json(
                        {"total_count": len(jobs), "jobs": records}, headers=headers
                    )
                    return
                self.send_json({"message": "unexpected GET"}, status=404)

            def do_POST(self) -> None:  # noqa: N802
                parsed = urlsplit(self.path)
                path = parsed.path
                body = self.read_json()
                fixture.requests.append(("POST", self.path, body))
                if path == "/graphql":
                    if fixture.graphql_error:
                        self.send_json({"errors": [{"message": "injected"}], "data": None})
                        return
                    variables = body.get("variables", {}) if isinstance(body, dict) else {}
                    ids = variables.get("ids", []) if isinstance(variables, dict) else []
                    nodes = []
                    for node_id in ids:
                        item = next(
                            (comment for comment in fixture.comments if comment["node_id"] == node_id),
                            None,
                        )
                        if item is None:
                            nodes.append(None)
                            continue
                        edited = item["updated_at"] != item["created_at"]
                        nodes.append(
                            {
                                "__typename": "IssueComment",
                                "id": item["node_id"],
                                "databaseId": item["id"],
                                "body": item["body"],
                                "createdAt": item["created_at"],
                                "lastEditedAt": item["updated_at"] if edited else None,
                                "includesCreatedEdit": edited,
                                "userContentEdits": {
                                    "totalCount": item.get(
                                        "edit_count", 2 if edited else 0
                                    )
                                },
                            }
                        )
                    self.send_json({"data": {"nodes": nodes}})
                    return
                status_match = re.fullmatch(
                    rf"/repos/{re.escape(fixture.repository)}/statuses/([0-9a-f]{{40}})",
                    path,
                )
                if status_match:
                    fixture.status_posts.append(body)
                    if fixture.status_failure_at == len(fixture.status_posts):
                        self.send_json({"message": "injected failure"}, status=500)
                        return
                    if fixture.status_commit_then_failure_at == len(
                        fixture.status_posts
                    ):
                        fixture.commit_statuses.insert(
                            0,
                            {
                                "id": len(fixture.status_posts),
                                "state": body["state"],
                                "context": body["context"],
                                "target_url": body["target_url"],
                            },
                        )
                        self.send_json(
                            {"message": "injected post-commit response failure"},
                            status=500,
                        )
                        return
                    self.send_json(
                        {
                            "id": len(fixture.status_posts),
                            "state": body["state"],
                            "context": body["context"],
                            "sha": status_match.group(1),
                            "target_url": body["target_url"],
                            **fixture.status_response_overrides,
                        },
                        status=201,
                    )
                    fixture.commit_statuses.insert(
                        0,
                        {
                            "id": len(fixture.status_posts),
                            "state": body["state"],
                            "context": body["context"],
                            "target_url": body["target_url"],
                        },
                    )
                    return
                cancel_match = re.fullmatch(
                    rf"/repos/{re.escape(fixture.repository)}/actions/runs/([1-9][0-9]*)/cancel",
                    path,
                )
                if cancel_match:
                    fixture.cancelled.append(int(cancel_match.group(1)))
                    self.send_response(202)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                self.send_json({"message": "unexpected POST"}, status=404)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        assert self.server is not None
        assert self.thread is not None
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    @property
    def url(self) -> str:
        assert self.server is not None
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def run(
        self,
        mode: str,
        *,
        event_name: str = "pull_request_target",
        event: dict | None = None,
        event_text: str | None = None,
        extra_env: dict[str, str] | None = None,
        unset_env: tuple[str, ...] = (),
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, str]]:
        with tempfile.TemporaryDirectory() as temporary:
            temp = pathlib.Path(temporary)
            event_path = temp / "event.json"
            event_path.write_text(
                (
                    event_text
                    if event_text is not None
                    else json.dumps(
                        event or self.event(event_name), separators=(",", ":")
                    )
                ),
                encoding="utf-8",
            )
            output_path = temp / "output"
            environment = {
                **os.environ,
                "TASK35_MODE": mode,
                "GH_TOKEN": "fixture-token",
                "EVENT_NAME": event_name,
                "GITHUB_EVENT_PATH": str(event_path),
                "REPOSITORY": self.repository,
                "REPOSITORY_ID": str(self.repository_id),
                "API_URL": self.url,
                "GRAPHQL_URL": f"{self.url}/graphql",
                "GITHUB_OUTPUT": str(output_path),
                "RUN_ID": "9001",
                "RUN_ATTEMPT": "1",
                "SERVER_URL": "https://github.example.invalid",
                "ACCEPTED_REPOSITORY": self.head_repository,
            }
            environment.update(extra_env or {})
            environment.pop("GITHUB_EVENT_PATH".removeprefix("GITHUB_"), None)
            for name in unset_env:
                environment.pop(name, None)
            for item in self.comments:
                if isinstance(item.get("issue_url"), str) and item["issue_url"].startswith(
                    "PLACEHOLDER/"
                ):
                    item["issue_url"] = f"{self.url}/{item['issue_url'].removeprefix('PLACEHOLDER/')}"
            completed = subprocess.run(
                [sys.executable, "-I", "-"],
                input=embedded_task35_controller(),
                text=True,
                capture_output=True,
                env=environment,
                timeout=20,
                check=False,
            )
            outputs: dict[str, str] = {}
            if output_path.exists():
                for line in output_path.read_text(encoding="utf-8").splitlines():
                    key, value = line.split("=", 1)
                    if key in outputs:
                        raise AssertionError(f"duplicate workflow output: {key}")
                    outputs[key] = value
            return completed, outputs


class Task35AdmissionBehaviorTests(unittest.TestCase):
    def test_embedded_controller_is_real_python_and_has_one_sentinel(self) -> None:
        script = embedded_task35_controller()
        compile(script, "ci-controller", "exec")
        self.assertIn("def admission()", script)
        self.assertIn("def publisher()", script)
        self.assertIn("def cancel_runs()", script)

    def test_non_pull_request_issue_comment_is_an_api_free_noop(self) -> None:
        with FakeTask35GitHub() as fixture:
            event = fixture.event("issue_comment", "created")
            event["issue"].pop("pull_request")
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual(
                {
                    "pr_number": "1",
                    "head_sha": "0" * 40,
                    "head_repository": "none/none",
                    "head_repository_id": "1",
                    "base_sha": "0" * 40,
                    "changed_files": "0",
                    "diff_digest": "0" * 64,
                    "classification": "none",
                    "decision": "noop",
                    "reason": "not-a-pull-request",
                    "auth_comment_id": "0",
                    "publish": "false",
                    "cancel": "false",
                    "cancel_scope": "none",
                    "run_quality": "false",
                    "run_scaffold": "false",
                    "run_secure": "false",
                    "secure_applicable": "false",
                },
                outputs,
            )
            self.assertEqual([], fixture.requests)
            self.assertEqual([], fixture.status_posts)
            self.assertEqual([], fixture.cancelled)

    def test_runner_event_payload_path_fails_closed(self) -> None:
        runner_path = "GITHUB_EVENT_PATH"
        cases = (
            (
                "absent",
                {},
                None,
                (runner_path,),
                "GITHUB_EVENT_PATH must be a non-empty string",
            ),
            (
                "empty",
                {runner_path: ""},
                None,
                (),
                "GITHUB_EVENT_PATH must be a non-empty string",
            ),
            (
                "unreadable",
                {runner_path: str(ROOT / ".github/task46-missing-event.json")},
                None,
                (),
                "event payload could not be read",
            ),
            ("malformed", {}, "{", (), "event payload is not strict JSON"),
        )
        for name, extra_env, event_text, unset_env, error in cases:
            with self.subTest(name=name), FakeTask35GitHub() as fixture:
                completed, outputs = fixture.run(
                    "admission",
                    event_text=event_text,
                    extra_env=extra_env,
                    unset_env=unset_env,
                )
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(error, completed.stderr)
                self.assertEqual({}, outputs)
                self.assertEqual([], fixture.requests)
                self.assertEqual([], fixture.status_posts)
                self.assertEqual([], fixture.cancelled)

        with FakeTask35GitHub() as fixture:
            event = fixture.event()
            event["repository"] = {
                "id": fixture.repository_id + 1,
                "full_name": fixture.repository,
            }
            completed, outputs = fixture.run("admission", event=event)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn(
                "event repository identity does not match the trusted environment",
                completed.stderr,
            )
            self.assertEqual({}, outputs)
            self.assertEqual([], fixture.requests)
            self.assertEqual([], fixture.status_posts)
            self.assertEqual([], fixture.cancelled)

    def test_pull_request_target_classification_and_release_matrix(self) -> None:
        cases = (
            ("src/app.py", "safe", "release", "true", "false"),
            (".github/scripts/retro-hygiene.sh", "runtime", "pending", "false", "false"),
            (".github/scripts/check_devcontainer.py", "runtime", "pending", "false", "true"),
            (".github/scripts/setup-ruleset.sh", "bootstrap", "failure", "false", "false"),
            (".github/workflows/ci.yml", "bootstrap", "failure", "false", "false"),
            (".Codex/DevContainer/devcontainer.json", "invalid", "failure", "false", "false"),
        )
        for path, classification, decision, run_quality, secure in cases:
            with self.subTest(path=path), FakeTask35GitHub() as fixture:
                fixture.files = [{"filename": path, "status": "modified"}]
                completed, outputs = fixture.run("admission")
                self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertEqual(classification, outputs["classification"])
                self.assertEqual(decision, outputs["decision"])
                self.assertEqual(run_quality, outputs["run_quality"])
                self.assertEqual(secure, outputs["secure_applicable"])

    def test_every_task33_trust_control_maps_to_exactly_one_class(self) -> None:
        runtime_paths = (
            ".codex/devcontainer/devcontainer.json",
            ".devcontainer/codex-adlc/devcontainer.json",
            ".github/scripts/check_devcontainer.py",
            ".github/scripts/materialize_devcontainer.py",
            ".github/scripts/preflight_devcontainer.py",
            ".github/scripts/check-skills.sh",
            ".github/scripts/tests/test_devcontainer.py",
        )
        bootstrap_paths = (
            ".github/workflows/ci.yml",
            ".github/scripts/setup-ruleset.sh",
            ".github/scripts/tests/test_ci_guards.py",
            ".github/CODEOWNERS",
        )
        for expected, paths in (("runtime", runtime_paths), ("bootstrap", bootstrap_paths)):
            for path in paths:
                with self.subTest(path=path), FakeTask35GitHub() as fixture:
                    fixture.files = [{"filename": path, "status": "modified"}]
                    completed, outputs = fixture.run("admission")
                    self.assertEqual(0, completed.returncode, completed.stderr)
                    self.assertEqual(expected, outputs["classification"])

    def test_rename_provenance_and_severity_precedence_are_fail_closed(self) -> None:
        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {
                    "filename": "docs/moved.md",
                    "previous_filename": ".github/scripts/check_devcontainer.py",
                    "status": "renamed",
                },
                {"filename": ".github/workflows/new.yml", "status": "added"},
            ]
            completed, outputs = fixture.run("admission")
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("bootstrap", outputs["classification"])

        cases = (
            ("./src//../.github/scripts/check-skills.sh", "runtime", 0),
            ("./.github/workflows/../workflows/ci.yml", "bootstrap", 0),
            (".Codex/DevContainer/devcontainer.json", "invalid", 0),
            ("../escape", None, 1),
            ("/absolute", None, 1),
            ("windows\\path", None, 1),
            ("bad\npath", None, 1),
        )
        for path, expected, must_fail in cases:
            with self.subTest(path=repr(path)), FakeTask35GitHub() as fixture:
                fixture.files = [{"filename": path, "status": "modified"}]
                completed, outputs = fixture.run("admission")
                if must_fail:
                    self.assertNotEqual(0, completed.returncode)
                    self.assertNotEqual("release", outputs.get("decision"))
                else:
                    self.assertEqual(0, completed.returncode, completed.stderr)
                    self.assertEqual(expected, outputs["classification"])

        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {
                    "filename": ".Codex/DevContainer/new.json",
                    "previous_filename": "docs/old.md",
                    "status": "renamed",
                }
            ]
            completed, outputs = fixture.run("admission")
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("invalid", outputs["classification"])

    def test_fork_is_never_released_by_pull_request_target(self) -> None:
        with FakeTask35GitHub() as fixture:
            fixture.head_repository = "outside/fork"
            fixture.head_repository_id = 200
            completed, outputs = fixture.run("admission")
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("pending", outputs["decision"])
            self.assertEqual("false", outputs["run_quality"])

    def test_head_drift_count_mismatch_and_malformed_pagination_fail_without_release(self) -> None:
        mutations = ("drift", "count", "link", "repository", "default-branch")
        for mutation in mutations:
            with self.subTest(mutation=mutation), FakeTask35GitHub() as fixture:
                if mutation == "drift":
                    fixture.drift_after_pr_call = 1
                elif mutation == "count":
                    fixture.changed_files_override = 2
                elif mutation == "link":
                    fixture.malformed_files_link = True
                elif mutation == "repository":
                    fixture.repository_metadata_id = 999
                else:
                    fixture.default_branch = "trunk"
                completed, outputs = fixture.run("admission")
                self.assertNotEqual(0, completed.returncode)
                self.assertNotEqual("release", outputs.get("decision"))

        for call in range(2, 7):
            with self.subTest(recheck_call=call), FakeTask35GitHub() as fixture:
                fixture.pr_overrides_by_call[call] = {"head_sha": "2" * 40}
                completed, outputs = fixture.run("admission")
                self.assertNotEqual(0, completed.returncode)
                self.assertNotEqual("release", outputs.get("decision"))

        field_cases = (
            ("number", 8),
            ("state", "closed"),
            ("head_repo_id", 200),
            ("head_repo_full_name", "outside/fork"),
            ("head_ref", "moved"),
            ("base_sha", "b" * 40),
            ("base_ref", "trunk"),
            ("changed_files", 2),
            ("author_id", 99),
        )
        for field, value in field_cases:
            with self.subTest(field=field), FakeTask35GitHub() as fixture:
                fixture.pr_overrides_by_call[2] = {field: value}
                completed, outputs = fixture.run("admission")
                self.assertNotEqual(0, completed.returncode)
                self.assertNotEqual("release", outputs.get("decision"))

        with FakeTask35GitHub() as fixture:
            fixture.files_by_call[2] = [
                {"filename": "src/replaced.py", "status": "modified"}
            ]
            completed, outputs = fixture.run("admission")
            self.assertNotEqual(0, completed.returncode)
            self.assertNotEqual("release", outputs.get("decision"))

        with FakeTask35GitHub() as fixture:
            fixture.files_link_override = (
                '<https://attacker.invalid/files?page=2>; rel="next"'
            )
            completed, outputs = fixture.run("admission")
            self.assertNotEqual(0, completed.returncode)
            self.assertNotEqual("release", outputs.get("decision"))

        with FakeTask35GitHub() as fixture:
            fixture.files_link_override = (
                f'<{fixture.url}/repos/{fixture.repository}/issues/7/comments?page=2>; '
                'rel="next"'
            )
            completed, outputs = fixture.run("admission")
            self.assertNotEqual(0, completed.returncode)
            self.assertNotEqual("release", outputs.get("decision"))

    def test_exact_sole_unedited_human_authorization_releases_runtime(self) -> None:
        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
            ]
            fixture.comments = [fixture.authorization_comment()]
            event = fixture.event("issue_comment", "created")
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("release", outputs["decision"])
            self.assertEqual("true", outputs["run_quality"])
            self.assertEqual("true", outputs["run_secure"])

        with FakeTask35GitHub() as fixture:
            fixture.head_repository = "outside/fork"
            fixture.head_repository_id = 200
            fixture.files = [{"filename": "docs/readme.md", "status": "modified"}]
            fixture.comments = [fixture.authorization_comment()]
            event = fixture.event("issue_comment", "created")
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("release", outputs["decision"])
            self.assertEqual("outside/fork", outputs["head_repository"])
            self.assertEqual("true", outputs["run_quality"])

    def test_file_and_comment_pagination_are_complete_before_release(self) -> None:
        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": "src/app.py", "status": "modified"},
                {"filename": ".github/workflows/late.yml", "status": "added"},
            ]
            fixture.files_page_size = 1
            completed, outputs = fixture.run("admission")
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("bootstrap", outputs["classification"])
            self.assertEqual("failure", outputs["decision"])

        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
            ]
            unrelated = fixture.authorization_comment(500)
            unrelated["body"] = "not authorization"
            fixture.comments = [unrelated, fixture.authorization_comment(501)]
            fixture.comments_page_size = 1
            event = fixture.event("issue_comment", "created")
            event["comment"] = fixture.comments[1]
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("release", outputs["decision"])
            comment_gets = [
                request
                for request in fixture.requests
                if request[0] == "GET" and "/comments?" in request[1]
            ]
            self.assertGreaterEqual(len(comment_gets), 4)

    def test_duplicate_exact_authorization_and_unrelated_comment_do_not_release(self) -> None:
        with FakeTask35GitHub() as fixture:
            fixture.files = [{"filename": ".github/scripts/check-skills.sh", "status": "modified"}]
            fixture.comments = [
                fixture.authorization_comment(501),
                fixture.authorization_comment(502),
            ]
            event = fixture.event("issue_comment", "created")
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertNotEqual("release", outputs.get("decision"))

        with FakeTask35GitHub() as fixture:
            unrelated = fixture.authorization_comment()
            unrelated["body"] = "looks good"
            fixture.comments = [unrelated]
            event = fixture.event("issue_comment", "created")
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("noop", outputs["decision"])
            self.assertEqual("false", outputs["publish"])

    def test_authorization_negatives_never_release(self) -> None:
        cases = ("wrong-body", "stale", "bot", "author", "read", "wrong-issue")
        for case in cases:
            with self.subTest(case=case), FakeTask35GitHub() as fixture:
                fixture.files = [
                    {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
                ]
                comment = fixture.authorization_comment()
                if case == "wrong-body":
                    comment["body"] += " extra"
                elif case == "stale":
                    comment["body"] = (
                        "/authorize-secure-devcontainer-runtime " + "2" * 40
                    )
                elif case == "bot":
                    comment["user"] = {"id": 22, "login": "review-bot", "type": "Bot"}
                elif case == "author":
                    comment["user"] = {"id": 11, "login": "pull-author", "type": "User"}
                elif case == "read":
                    fixture.permission = "read"
                else:
                    comment["issue_url"] = (
                        f"{fixture.url}/repos/{fixture.repository}/issues/99"
                    )
                fixture.comments = [comment]
                event = fixture.event("issue_comment", "created")
                completed, outputs = fixture.run(
                    "admission", event_name="issue_comment", event=event
                )
                if case == "wrong-issue":
                    self.assertNotEqual(0, completed.returncode)
                else:
                    self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertNotEqual("release", outputs.get("decision"))

        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
            ]
            fixture.comments = [fixture.authorization_comment()]
            fixture.graphql_error = True
            event = fixture.event("issue_comment", "created")
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertNotEqual("release", outputs.get("decision"))

        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
            ]
            owner_comment = fixture.authorization_comment()
            owner_comment["user"] = {"id": 1, "login": "example", "type": "User"}
            fixture.comments = [owner_comment]
            fixture.permissions["example"] = "admin"
            event = fixture.event("issue_comment", "created")
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("release", outputs["decision"])

    def test_non_authoritative_comment_deletion_is_noop(self) -> None:
        with FakeTask35GitHub() as fixture:
            comment = fixture.authorization_comment()
            comment["body"] += " extra"
            fixture.comments = []
            event = fixture.event("issue_comment", "deleted")
            event["comment"] = comment
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("noop", outputs["decision"])
            self.assertEqual("false", outputs["cancel"])

        with FakeTask35GitHub() as fixture:
            comment = fixture.authorization_comment()
            comment["issue_url"] = (
                f"{fixture.url}/repos/{fixture.repository}/issues/{fixture.pr_number}"
            )
            event = fixture.event("issue_comment", "deleted")
            event["comment"] = comment
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("noop", outputs["decision"])
            self.assertEqual("authorization-not-required", outputs["reason"])
            self.assertEqual("false", outputs["publish"])
            self.assertEqual("false", outputs["cancel"])

    def test_prior_bound_authorization_revokes_after_permission_loss(self) -> None:
        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
            ]
            comment = fixture.authorization_comment(501)
            comment["issue_url"] = (
                f"{fixture.url}/repos/{fixture.repository}/issues/{fixture.pr_number}"
            )
            replacement = fixture.authorization_comment(502)
            replacement["user"] = {
                "id": 23,
                "login": "second-reviewer",
                "type": "User",
            }
            fixture.comments = [replacement]
            fixture.permission = "read"
            fixture.permissions["second-reviewer"] = "write"
            target_url = (
                "https://github.example.invalid/example/project/actions/runs/8001"
            )
            fixture.commit_statuses = [
                {
                    "id": index,
                    "state": "pending",
                    "context": context,
                    "target_url": target_url,
                }
                for index, context in enumerate(
                    ("quality", "scaffold-self-check", "secure-devcontainer"), start=1
                )
            ]
            fixture.runs = [
                {
                    "id": 8001,
                    "status": "in_progress",
                    "path": ".github/workflows/ci.yml@main",
                    "display_title": f"CI admission PR #{fixture.pr_number}",
                    "event": "issue_comment",
                }
            ]
            matching_old_attempt = [
                {
                    "name": (
                        f"isolated candidate quality worker pr-{fixture.pr_number} "
                        f"repo-{fixture.repository_id} head-{fixture.head_sha} "
                        f"base-{fixture.base_sha} auth-501"
                    ),
                    "status": "in_progress",
                    "conclusion": None,
                }
            ]
            fixture.jobs_by_filter[(8001, "latest")] = [
                {"name": "base-owned admission controller", "status": "completed"}
            ]
            fixture.jobs_by_filter[(8001, "all")] = matching_old_attempt
            event = fixture.event("issue_comment", "deleted")
            event["comment"] = comment
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("failure", outputs["decision"])
            self.assertEqual("authorization-revoked", outputs["reason"])
            self.assertEqual("501", outputs["auth_comment_id"])
            self.assertEqual("true", outputs["cancel"])
            self.assertEqual("current-head", outputs["cancel_scope"])
            self.assertTrue(
                any(
                    method == "GET" and "filter=all" in path
                    for method, path, _ in fixture.requests
                )
            )

        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
            ]
            live = fixture.authorization_comment(501)
            live["issue_url"] = (
                f"{fixture.url}/repos/{fixture.repository}/issues/{fixture.pr_number}"
            )
            live["updated_at"] = "2026-08-12T01:03:00Z"
            live["edit_count"] = 3
            fixture.comments = [live]
            target_url = (
                "https://github.example.invalid/example/project/actions/runs/8001"
            )
            fixture.commit_statuses = [
                {
                    "id": index,
                    "state": "pending",
                    "context": context,
                    "target_url": target_url,
                }
                for index, context in enumerate(
                    ("quality", "scaffold-self-check", "secure-devcontainer"), start=1
                )
            ]
            fixture.runs = [
                {
                    "id": 8001,
                    "status": "in_progress",
                    "path": ".github/workflows/ci.yml",
                    "display_title": f"CI admission PR #{fixture.pr_number}",
                    "event": "issue_comment",
                }
            ]
            fixture.jobs = {
                8001: [
                    {
                        "name": (
                            f"isolated candidate quality worker pr-{fixture.pr_number} "
                            f"repo-{fixture.repository_id} head-{fixture.head_sha} "
                            f"base-{fixture.base_sha} auth-501"
                        ),
                        "status": "in_progress",
                        "conclusion": None,
                    }
                ]
            }
            event = fixture.event("issue_comment", "edited")
            event["comment"] = json.loads(json.dumps(live))
            event["comment"]["body"] = "authorization withdrawn"
            event["comment"]["updated_at"] = "2026-08-12T01:01:00Z"
            event["changes"] = {
                "body": {
                    "from": (
                        "/authorize-secure-devcontainer-runtime "
                        f"{fixture.head_sha}"
                    )
                }
            }
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("failure", outputs["decision"])
            self.assertEqual("authorization-revoked", outputs["reason"])
            self.assertEqual("true", outputs["cancel"])

        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
            ]
            live = fixture.authorization_comment(501)
            live["body"] = "authorization withdrawn"
            live["updated_at"] = "2026-08-12T01:03:00Z"
            live["edit_count"] = 3
            fixture.comments = [live]
            event = fixture.event("issue_comment", "edited")
            event["comment"] = live
            event["changes"] = {
                "body": {
                    "from": (
                        "/authorize-secure-devcontainer-runtime "
                        f"{fixture.head_sha}"
                    )
                }
            }
            completed, outputs = fixture.run(
                "admission", event_name="issue_comment", event=event
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("noop", outputs["decision"])
            self.assertEqual("false", outputs["publish"])
            self.assertEqual("false", outputs["cancel"])

    def test_publisher_failure_baseline_and_fixed_result_mapping(self) -> None:
        with FakeTask35GitHub() as fixture:
            extra = {
                "ACCEPTED_PR": str(fixture.pr_number),
                "ACCEPTED_HEAD": fixture.head_sha,
                "ACCEPTED_REPOSITORY": fixture.repository,
                "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                "ACCEPTED_BASE": fixture.base_sha,
                "ACCEPTED_CHANGED_FILES": str(len(fixture.files)),
                "ACCEPTED_DIFF_DIGEST": fixture.diff_digest(),
                "ACCEPTED_CLASS": "safe",
                "ACCEPTED_SECURE": "false",
                "DECISION": "release",
                "DECISION_REASON": "same-repository-safe",
                "ACCEPTED_AUTH_COMMENT": "0",
                "QUALITY_RESULT": "success",
                "SCAFFOLD_RESULT": "success",
                "SECURE_RESULT": "skipped",
                "LEDGER_RESULT": "success",
            }
            target_url = "https://github.example.invalid/example/project/actions/runs/9001"
            fixture.commit_statuses = [
                {
                    "id": index,
                    "state": "pending",
                    "context": context,
                    "target_url": target_url,
                }
                for index, context in enumerate(
                    ("quality", "scaffold-self-check", "secure-devcontainer"), start=1
                )
            ]
            completed, _ = fixture.run("publisher", extra_env=extra)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual(["failure", "failure", "failure"], [p["state"] for p in fixture.status_posts[:3]])
            self.assertEqual(
                ["success", "success", "success"],
                [p["state"] for p in fixture.status_posts[-3:]],
            )
            self.assertEqual(
                ["quality", "scaffold-self-check", "secure-devcontainer"],
                [p["context"] for p in fixture.status_posts[-3:]],
            )

        with FakeTask35GitHub() as fixture:
            extra["SECURE_RESULT"] = "success"
            target_url = "https://github.example.invalid/example/project/actions/runs/9001"
            fixture.commit_statuses = [
                {
                    "id": index,
                    "state": "pending",
                    "context": context,
                    "target_url": target_url,
                }
                for index, context in enumerate(
                    ("quality", "scaffold-self-check", "secure-devcontainer"), start=1
                )
            ]
            completed, _ = fixture.run("publisher", extra_env=extra)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("failure", fixture.status_posts[-1]["state"])

        for result in ("failure", "cancelled", "skipped"):
            with self.subTest(applicable_result=result), FakeTask35GitHub() as fixture:
                local = dict(extra)
                local["QUALITY_RESULT"] = result
                local["SECURE_RESULT"] = "skipped"
                target_url = (
                    "https://github.example.invalid/example/project/actions/runs/9001"
                )
                fixture.commit_statuses = [
                    {
                        "id": index,
                        "state": "pending",
                        "context": context,
                        "target_url": target_url,
                    }
                    for index, context in enumerate(
                        ("quality", "scaffold-self-check", "secure-devcontainer"), start=1
                    )
                ]
                completed, _ = fixture.run("publisher", extra_env=local)
                self.assertEqual(0, completed.returncode, completed.stderr)
                final = {item["context"]: item["state"] for item in fixture.status_posts[-3:]}
                self.assertEqual("failure", final["quality"])

        with FakeTask35GitHub() as fixture:
            local = dict(extra)
            local.update(
                {
                    "QUALITY_RESULT": "success",
                    "SCAFFOLD_RESULT": "success",
                    "SECURE_RESULT": "skipped",
                    "LEDGER_RESULT": "failure",
                }
            )
            target_url = "https://github.example.invalid/example/project/actions/runs/9001"
            fixture.commit_statuses = [
                {
                    "id": index,
                    "state": "pending",
                    "context": context,
                    "target_url": target_url,
                }
                for index, context in enumerate(
                    ("quality", "scaffold-self-check", "secure-devcontainer"), start=1
                )
            ]
            completed, _ = fixture.run("publisher", extra_env=local)
            self.assertEqual(0, completed.returncode, completed.stderr)
            final = {item["context"]: item["state"] for item in fixture.status_posts[-3:]}
            self.assertEqual("failure", final["scaffold-self-check"])

    def test_authorized_runtime_preflight_and_publisher_recheck_live_authorization(self) -> None:
        def environment(fixture: FakeTask35GitHub) -> dict[str, str]:
            return {
                "ACCEPTED_PR": str(fixture.pr_number),
                "ACCEPTED_HEAD": fixture.head_sha,
                "ACCEPTED_REPOSITORY": fixture.repository,
                "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                "ACCEPTED_BASE": fixture.base_sha,
                "ACCEPTED_CHANGED_FILES": str(len(fixture.files)),
                "ACCEPTED_DIFF_DIGEST": fixture.diff_digest(),
                "ACCEPTED_CLASS": "runtime",
                "ACCEPTED_SECURE": "true",
                "DECISION": "release",
                "DECISION_REASON": "exact-human-authorization",
                "ACCEPTED_AUTH_COMMENT": "501",
                "QUALITY_RESULT": "success",
                "SCAFFOLD_RESULT": "success",
                "SECURE_RESULT": "success",
                "LEDGER_RESULT": "success",
            }

        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
            ]
            fixture.comments = [fixture.authorization_comment(501)]
            extra = environment(fixture)
            preflight, _ = fixture.run("preflight", extra_env=extra)
            self.assertEqual(0, preflight.returncode, preflight.stderr)
            publisher, _ = fixture.run("publisher", extra_env=extra)
            self.assertEqual(0, publisher.returncode, publisher.stderr)
            final = {item["context"]: item["state"] for item in fixture.status_posts[-3:]}
            self.assertEqual(
                {
                    "quality": "success",
                    "scaffold-self-check": "success",
                    "secure-devcontainer": "success",
                },
                final,
            )

        with FakeTask35GitHub() as fixture:
            fixture.files = [
                {"filename": ".github/scripts/check_devcontainer.py", "status": "modified"}
            ]
            fixture.comments = [fixture.authorization_comment(501)]
            extra = environment(fixture)
            preflight, _ = fixture.run("preflight", extra_env=extra)
            self.assertEqual(0, preflight.returncode, preflight.stderr)
            fixture.permission = "read"
            publisher, _ = fixture.run("publisher", extra_env=extra)
            self.assertNotEqual(0, publisher.returncode)
            self.assertFalse(
                any(item.get("state") == "success" for item in fixture.status_posts)
            )

    def test_status_api_uncertainty_never_posts_success(self) -> None:
        with FakeTask35GitHub() as fixture:
            fixture.status_failure_at = 1
            extra = {
                "ACCEPTED_PR": str(fixture.pr_number),
                "ACCEPTED_HEAD": fixture.head_sha,
                "ACCEPTED_REPOSITORY": fixture.repository,
                "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                "ACCEPTED_BASE": fixture.base_sha,
                "ACCEPTED_CHANGED_FILES": str(len(fixture.files)),
                "ACCEPTED_DIFF_DIGEST": fixture.diff_digest(),
                "ACCEPTED_CLASS": "safe",
                "ACCEPTED_SECURE": "false",
                "DECISION": "release",
                "DECISION_REASON": "same-repository-safe",
                "ACCEPTED_AUTH_COMMENT": "0",
                "QUALITY_RESULT": "success",
                "SCAFFOLD_RESULT": "success",
                "SECURE_RESULT": "skipped",
                "LEDGER_RESULT": "success",
            }
            target_url = "https://github.example.invalid/example/project/actions/runs/9001"
            fixture.commit_statuses = [
                {
                    "id": index,
                    "state": "pending",
                    "context": context,
                    "target_url": target_url,
                }
                for index, context in enumerate(
                    ("quality", "scaffold-self-check", "secure-devcontainer"), start=1
                )
            ]
            completed, _ = fixture.run("publisher", extra_env=extra)
            self.assertNotEqual(0, completed.returncode)
            self.assertFalse(any(post.get("state") == "success" for post in fixture.status_posts))

        for committed_failure_at in (4, 5, 6):
            with (
                self.subTest(committed_failure_at=committed_failure_at),
                FakeTask35GitHub() as fixture,
            ):
                target_url = (
                    "https://github.example.invalid/example/project/actions/runs/9001"
                )
                fixture.commit_statuses = [
                    {
                        "id": index,
                        "state": "pending",
                        "context": context,
                        "target_url": target_url,
                    }
                    for index, context in enumerate(
                        ("quality", "scaffold-self-check", "secure-devcontainer"),
                        start=1,
                    )
                ]
                fixture.status_commit_then_failure_at = committed_failure_at
                extra = {
                    "ACCEPTED_PR": str(fixture.pr_number),
                    "ACCEPTED_HEAD": fixture.head_sha,
                    "ACCEPTED_REPOSITORY": fixture.repository,
                    "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                    "ACCEPTED_BASE": fixture.base_sha,
                    "ACCEPTED_CHANGED_FILES": str(len(fixture.files)),
                    "ACCEPTED_DIFF_DIGEST": fixture.diff_digest(),
                    "ACCEPTED_CLASS": "safe",
                    "ACCEPTED_SECURE": "false",
                    "DECISION": "release",
                    "DECISION_REASON": "same-repository-safe",
                    "ACCEPTED_AUTH_COMMENT": "0",
                    "QUALITY_RESULT": "success",
                    "SCAFFOLD_RESULT": "success",
                    "SECURE_RESULT": "skipped",
                    "LEDGER_RESULT": "success",
                }
                completed, _ = fixture.run("publisher", extra_env=extra)
                self.assertNotEqual(0, completed.returncode)
                latest = {}
                for status in fixture.commit_statuses:
                    latest.setdefault(status["context"], status["state"])
                self.assertEqual(
                    {
                        "quality": "failure",
                        "scaffold-self-check": "failure",
                        "secure-devcontainer": "failure",
                    },
                    latest,
                )

        for field, value in (
            ("sha", "2" * 40),
            ("context", "wrong-context"),
            ("state", "success"),
            ("target_url", "https://attacker.invalid/run"),
        ):
            with self.subTest(field=field), FakeTask35GitHub() as fixture:
                fixture.status_response_overrides[field] = value
                extra = {
                    "ACCEPTED_PR": str(fixture.pr_number),
                    "ACCEPTED_HEAD": fixture.head_sha,
                    "ACCEPTED_REPOSITORY": fixture.repository,
                    "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                    "ACCEPTED_BASE": fixture.base_sha,
                    "ACCEPTED_CHANGED_FILES": str(len(fixture.files)),
                    "ACCEPTED_DIFF_DIGEST": fixture.diff_digest(),
                    "ACCEPTED_CLASS": "safe",
                    "ACCEPTED_SECURE": "false",
                    "DECISION": "release",
                    "DECISION_REASON": "same-repository-safe",
                    "ACCEPTED_AUTH_COMMENT": "0",
                }
                completed, _ = fixture.run("preflight", extra_env=extra)
                self.assertNotEqual(0, completed.returncode)
                self.assertFalse(
                    any(post.get("state") == "success" for post in fixture.status_posts)
                )

        with FakeTask35GitHub() as fixture:
            fixture.fail_get_suffix = f"/pulls/{fixture.pr_number}"
            extra = {
                "ACCEPTED_PR": str(fixture.pr_number),
                "ACCEPTED_HEAD": fixture.head_sha,
                "ACCEPTED_REPOSITORY": fixture.repository,
                "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                "ACCEPTED_BASE": fixture.base_sha,
                "ACCEPTED_CHANGED_FILES": str(len(fixture.files)),
                "ACCEPTED_DIFF_DIGEST": fixture.diff_digest(),
                "ACCEPTED_CLASS": "safe",
                "ACCEPTED_SECURE": "false",
                "DECISION": "release",
                "DECISION_REASON": "same-repository-safe",
                "ACCEPTED_AUTH_COMMENT": "0",
            }
            completed, _ = fixture.run("preflight", extra_env=extra)
            self.assertNotEqual(0, completed.returncode)
            self.assertFalse(any(post.get("state") == "success" for post in fixture.status_posts))

        with FakeTask35GitHub() as fixture:
            fixture.files_by_call[2] = [
                {"filename": "src/replaced.py", "status": "modified"}
            ]
            extra = {
                "ACCEPTED_PR": str(fixture.pr_number),
                "ACCEPTED_HEAD": fixture.head_sha,
                "ACCEPTED_REPOSITORY": fixture.repository,
                "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                "ACCEPTED_BASE": fixture.base_sha,
                "ACCEPTED_CHANGED_FILES": str(len(fixture.files)),
                "ACCEPTED_DIFF_DIGEST": fixture.diff_digest(),
                "ACCEPTED_CLASS": "safe",
                "ACCEPTED_SECURE": "false",
                "DECISION": "release",
                "DECISION_REASON": "same-repository-safe",
                "ACCEPTED_AUTH_COMMENT": "0",
            }
            completed, _ = fixture.run("preflight", extra_env=extra)
            self.assertNotEqual(0, completed.returncode)
            self.assertFalse(any(post.get("state") == "success" for post in fixture.status_posts))

    def test_newer_run_status_ownership_blocks_stale_final_publisher(self) -> None:
        with FakeTask35GitHub() as fixture:
            fixture.commit_statuses = [
                {
                    "id": index,
                    "state": "pending",
                    "context": context,
                    "target_url": "https://github.example.invalid/example/project/actions/runs/9999",
                }
                for index, context in enumerate(
                    ("quality", "scaffold-self-check", "secure-devcontainer"), start=1
                )
            ]
            extra = {
                "ACCEPTED_PR": str(fixture.pr_number),
                "ACCEPTED_HEAD": fixture.head_sha,
                "ACCEPTED_REPOSITORY": fixture.repository,
                "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                "ACCEPTED_BASE": fixture.base_sha,
                "ACCEPTED_CHANGED_FILES": str(len(fixture.files)),
                "ACCEPTED_DIFF_DIGEST": fixture.diff_digest(),
                "ACCEPTED_CLASS": "safe",
                "ACCEPTED_SECURE": "false",
                "DECISION": "release",
                "DECISION_REASON": "same-repository-safe",
                "ACCEPTED_AUTH_COMMENT": "0",
                "QUALITY_RESULT": "success",
                "SCAFFOLD_RESULT": "success",
                "SECURE_RESULT": "skipped",
                "LEDGER_RESULT": "success",
            }
            completed, _ = fixture.run("publisher", extra_env=extra)
            self.assertNotEqual(0, completed.returncode)
            self.assertEqual([], fixture.status_posts)

        with FakeTask35GitHub() as fixture:
            target_url = "https://github.example.invalid/example/project/actions/runs/9001"
            fixture.commit_statuses = [
                {
                    "id": index,
                    "state": "pending",
                    "context": context,
                    "target_url": target_url,
                }
                for index, context in enumerate(
                    ("quality", "scaffold-self-check", "secure-devcontainer"), start=1
                )
            ]
            fixture.statuses_page_size = 1
            extra = {
                "ACCEPTED_PR": str(fixture.pr_number),
                "ACCEPTED_HEAD": fixture.head_sha,
                "ACCEPTED_REPOSITORY": fixture.repository,
                "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                "ACCEPTED_BASE": fixture.base_sha,
                "ACCEPTED_CHANGED_FILES": str(len(fixture.files)),
                "ACCEPTED_DIFF_DIGEST": fixture.diff_digest(),
                "ACCEPTED_CLASS": "safe",
                "ACCEPTED_SECURE": "false",
                "DECISION": "release",
                "DECISION_REASON": "same-repository-safe",
                "ACCEPTED_AUTH_COMMENT": "0",
                "QUALITY_RESULT": "success",
                "SCAFFOLD_RESULT": "success",
                "SECURE_RESULT": "skipped",
                "LEDGER_RESULT": "success",
            }
            completed, _ = fixture.run("publisher", extra_env=extra)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("success", fixture.status_posts[-1]["state"])

    def test_cancellation_requires_exact_job_name_binding(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        cancellation = workflow.split("  cancellation-controller:\n", 1)[1].split(
            "\n  status-preflight:", 1
        )[0]
        self.assertIn("github.run_attempt == 1", cancellation)
        self.assertIn("RUN_ATTEMPT: ${{ github.run_attempt }}", cancellation)
        self.assertIn("pull-requests: read", cancellation)

        with FakeTask35GitHub() as fixture:
            old_head = "2" * 40
            fixture.runs_page_size = 1
            fixture.jobs_page_size = 1
            fixture.runs = [
                {
                    "id": 8001,
                    "status": "in_progress",
                    "path": ".github/workflows/ci.yml",
                    "display_title": f"CI admission PR #{fixture.pr_number}",
                    "event": "pull_request_target",
                },
                {
                    "id": 8002,
                    "status": "in_progress",
                    "path": ".github/workflows/ci.yml",
                    "display_title": "CI admission PR #999",
                    "event": "pull_request_target",
                },
            ]
            fixture.jobs = {
                8001: [
                    {"name": "base-owned admission controller"},
                    {
                        "name": (
                            f"isolated candidate quality worker pr-{fixture.pr_number} "
                            f"repo-{fixture.repository_id} head-{old_head} base-{fixture.base_sha} auth-0"
                        )
                    }
                ],
                8002: [
                    {
                        "name": (
                            f"isolated candidate quality worker pr-999 "
                            f"repo-{fixture.repository_id} head-{old_head} base-{fixture.base_sha} auth-0"
                        )
                    }
                ],
            }
            completed, _ = fixture.run(
                "cancel",
                extra_env={
                    "ACCEPTED_PR": str(fixture.pr_number),
                    "ACCEPTED_HEAD": fixture.head_sha,
                    "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                    "ACCEPTED_BASE": fixture.base_sha,
                    "ACCEPTED_AUTH_COMMENT": "0",
                    "CANCEL_SCOPE": "prior-head",
                },
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual([8001], fixture.cancelled)
            queried_statuses = {
                parse_qs(urlsplit(path).query).get("status", [None])[0]
                for method, path, _ in fixture.requests
                if method == "GET" and "/actions/workflows/ci.yml/runs?" in path
            }
            self.assertEqual(
                {"requested", "waiting", "pending", "queued", "in_progress"},
                queried_statuses,
            )

        with FakeTask35GitHub() as fixture:
            old_head = "3" * 40
            common = {
                "id": 8010,
                "path": ".github/workflows/ci.yml@main",
                "display_title": f"CI admission PR #{fixture.pr_number}",
                "event": "pull_request_target",
                "workflow_id": 900,
                "run_number": 44,
                "run_attempt": 1,
                "head_branch": "main",
                "head_sha": fixture.base_sha,
            }
            fixture.runs = [
                {**common, "status": "requested"},
                {**common, "status": "in_progress"},
            ]
            fixture.jobs = {
                8010: [
                    {
                        "name": (
                            f"isolated candidate quality worker pr-{fixture.pr_number} "
                            f"repo-{fixture.repository_id} head-{old_head} "
                            f"base-{fixture.base_sha} auth-0"
                        )
                    }
                ]
            }
            completed, _ = fixture.run(
                "cancel",
                extra_env={
                    "ACCEPTED_PR": str(fixture.pr_number),
                    "ACCEPTED_HEAD": fixture.head_sha,
                    "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                    "ACCEPTED_BASE": fixture.base_sha,
                    "ACCEPTED_AUTH_COMMENT": "0",
                    "CANCEL_SCOPE": "prior-head",
                },
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual([8010], fixture.cancelled)

        with FakeTask35GitHub() as fixture:
            common = {
                "id": 8011,
                "status": "requested",
                "path": ".github/workflows/ci.yml",
                "display_title": f"CI admission PR #{fixture.pr_number}",
                "event": "pull_request_target",
            }
            fixture.runs = [
                common,
                {**common, "status": "queued", "event": "issue_comment"},
            ]
            completed, _ = fixture.run(
                "cancel",
                extra_env={
                    "ACCEPTED_PR": str(fixture.pr_number),
                    "ACCEPTED_HEAD": fixture.head_sha,
                    "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                    "ACCEPTED_BASE": fixture.base_sha,
                    "ACCEPTED_AUTH_COMMENT": "0",
                    "CANCEL_SCOPE": "prior-head",
                },
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertEqual([], fixture.cancelled)

        with FakeTask35GitHub() as fixture:
            completed, _ = fixture.run(
                "cancel",
                extra_env={
                    "ACCEPTED_PR": str(fixture.pr_number),
                    "ACCEPTED_HEAD": fixture.head_sha,
                    "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                    "ACCEPTED_BASE": fixture.base_sha,
                    "ACCEPTED_AUTH_COMMENT": "0",
                    "CANCEL_SCOPE": "prior-head",
                    "RUN_ATTEMPT": "2",
                },
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertEqual([], fixture.cancelled)

        with FakeTask35GitHub() as fixture:
            fixture.pr_overrides_by_call[1] = {"head_sha": "4" * 40}
            completed, _ = fixture.run(
                "cancel",
                extra_env={
                    "ACCEPTED_PR": str(fixture.pr_number),
                    "ACCEPTED_HEAD": fixture.head_sha,
                    "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                    "ACCEPTED_BASE": fixture.base_sha,
                    "ACCEPTED_AUTH_COMMENT": "0",
                    "CANCEL_SCOPE": "prior-head",
                },
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertEqual([], fixture.cancelled)

        with FakeTask35GitHub() as fixture:
            fixture.runs = [
                {
                    "id": 8003,
                    "status": "in_progress",
                    "path": ".github/workflows/ci.yml",
                    "display_title": f"CI admission PR #{fixture.pr_number}",
                    "event": "issue_comment",
                }
            ]
            fixture.jobs = {
                8003: [
                    {
                        "name": (
                            f"isolated candidate quality worker pr-{fixture.pr_number} "
                            f"repo-{fixture.repository_id} head-{fixture.head_sha} "
                            f"base-{fixture.base_sha} auth-501"
                        ),
                        "status": "in_progress",
                        "conclusion": None,
                    },
                    {
                        "name": (
                            f"isolated candidate scaffold worker pr-{fixture.pr_number} "
                            f"repo-{fixture.repository_id} head-{fixture.head_sha} "
                            f"base-{fixture.base_sha} auth-502"
                        ),
                        "status": "in_progress",
                        "conclusion": None,
                    },
                ]
            }
            completed, _ = fixture.run(
                "cancel",
                event_name="issue_comment",
                extra_env={
                    "ACCEPTED_PR": str(fixture.pr_number),
                    "ACCEPTED_HEAD": fixture.head_sha,
                    "ACCEPTED_REPOSITORY_ID": str(fixture.repository_id),
                    "ACCEPTED_BASE": fixture.base_sha,
                    "ACCEPTED_AUTH_COMMENT": "501",
                    "CANCEL_SCOPE": "current-head",
                },
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual([], fixture.cancelled)
            self.assertTrue(any("filter=latest" in path for _, path, _ in fixture.requests))


class Task35RulesetHelperTests(unittest.TestCase):
    script = ROOT / ".github/scripts/setup-ruleset.sh"

    def run_helper(
        self,
        arguments: list[str],
        *,
        input_text: str = "",
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(self.script), *arguments],
            input=input_text,
            text=True,
            capture_output=True,
            env={**os.environ, **(environment or {})},
            timeout=10,
            check=False,
        )

    def make_fake_gh(self, directory: pathlib.Path) -> pathlib.Path:
        executable = directory / "gh"
        executable.write_text(
            textwrap.dedent(
                f"""\
                #!{sys.executable}
                import json
                import os
                import sys

                with open(os.environ["GH_LOG"], "a", encoding="utf-8") as stream:
                    stream.write(json.dumps({{"args": sys.argv[1:], "host": os.environ.get("GH_HOST")}}) + "\\n")
                args = sys.argv[1:]
                if args[:2] == ["auth", "status"]:
                    raise SystemExit(0)
                if not args or args[0] != "api":
                    raise SystemExit(91)
                if "--method" in args:
                    method = args[args.index("--method") + 1]
                    if method != "POST":
                        raise SystemExit(92)
                    payload = json.load(sys.stdin)
                    if os.environ.get("FAKE_NORMALIZE") == "1":
                        pr = next(rule for rule in payload["rules"] if rule["type"] == "pull_request")
                        pr["parameters"].update({{
                            "required_reviewers": [],
                            "dismissal_restriction": {{"enabled": False, "allowed_actors": []}},
                            "ignore_approvals_from_contributors": False,
                        }})
                        status = next(rule for rule in payload["rules"] if rule["type"] == "required_status_checks")
                        status["parameters"]["do_not_enforce_on_create"] = False
                    payload["id"] = 42
                    print(json.dumps(payload, separators=(",", ":")))
                    raise SystemExit(0)
                endpoint = args[-1]
                if endpoint.endswith("/rulesets/42"):
                    print(os.environ["FAKE_EXISTING"])
                elif "rulesets?" in endpoint:
                    print(os.environ.get("FAKE_LIST", "[[]]"))
                else:
                    raise SystemExit(93)
                """
            ),
            encoding="utf-8",
        )
        executable.chmod(0o755)
        return executable

    def test_dry_run_is_hermetic_and_source_binds_exact_three_contexts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = pathlib.Path(temporary)
            log = temp / "gh.log"
            self.make_fake_gh(temp)
            completed = self.run_helper(
                ["--dry-run", "--integration-id", "123456"],
                environment={
                    "PATH": f"{temp}:{os.environ['PATH']}",
                    "GH_LOG": str(log),
                    "GH_HOST": "enterprise.invalid",
                },
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertFalse(log.exists())
            payload = json.loads(completed.stdout)
            self.assertEqual("disabled", payload["enforcement"])
            contexts = next(
                rule["parameters"]["required_status_checks"]
                for rule in payload["rules"]
                if rule["type"] == "required_status_checks"
            )
            self.assertEqual(
                [
                    {"context": "quality", "integration_id": 123456},
                    {"context": "scaffold-self-check", "integration_id": 123456},
                    {"context": "secure-devcontainer", "integration_id": 123456},
                ],
                contexts,
            )

    def test_mode_and_integration_id_errors_happen_before_any_gh_call(self) -> None:
        cases = (
            [],
            ["--dry-run"],
            ["--dry-run", "--integration-id", "0"],
            ["--dry-run", "--integration-id", "01"],
            ["--dry-run", "--apply", "--integration-id", "12"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            temp = pathlib.Path(temporary)
            log = temp / "gh.log"
            self.make_fake_gh(temp)
            environment = {"PATH": f"{temp}:{os.environ['PATH']}", "GH_LOG": str(log)}
            for arguments in cases:
                with self.subTest(arguments=arguments):
                    log.unlink(missing_ok=True)
                    completed = self.run_helper(arguments, environment=environment)
                    self.assertEqual(2, completed.returncode)
                    self.assertFalse(log.exists())

    def test_apply_requires_exact_confirmation_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = pathlib.Path(temporary)
            log = temp / "gh.log"
            self.make_fake_gh(temp)
            completed = self.run_helper(
                [
                    "--apply",
                    "--integration-id",
                    "123456",
                    "--repo",
                    "example/project",
                ],
                input_text="yes\n",
                environment={"PATH": f"{temp}:{os.environ['PATH']}", "GH_LOG": str(log)},
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertFalse(log.exists())

    def test_apply_host_pins_and_creates_only_one_disabled_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = pathlib.Path(temporary)
            log = temp / "gh.log"
            self.make_fake_gh(temp)
            confirmation = (
                "apply disabled ruleset adlc-default-branch to "
                "github.com/example/project with integration ID 123456\n"
            )
            completed = self.run_helper(
                [
                    "--apply",
                    "--integration-id",
                    "123456",
                    "--repo",
                    "example/project",
                ],
                input_text=confirmation,
                environment={
                    "PATH": f"{temp}:{os.environ['PATH']}",
                    "GH_LOG": str(log),
                    "GH_HOST": "enterprise.invalid",
                    "FAKE_LIST": "[[]]",
                    "FAKE_NORMALIZE": "1",
                },
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(3, len(records))
            self.assertTrue(all(record["host"] == "github.com" for record in records))
            self.assertTrue(all("--hostname" in record["args"] for record in records))
            methods = [
                record["args"][record["args"].index("--method") + 1]
                for record in records
                if "--method" in record["args"]
            ]
            self.assertEqual(["POST"], methods)

    def test_compatible_disabled_reuse_and_incompatible_active_refusal_never_write(self) -> None:
        dry = self.run_helper(["--dry-run", "--integration-id", "123456"])
        self.assertEqual(0, dry.returncode, dry.stderr)
        compatible = json.loads(dry.stdout)
        compatible["id"] = 42
        pr = next(rule for rule in compatible["rules"] if rule["type"] == "pull_request")
        pr["parameters"].update(
            {
                "required_reviewers": [],
                "dismissal_restriction": {"enabled": False, "allowed_actors": []},
                "ignore_approvals_from_contributors": False,
            }
        )
        status = next(
            rule for rule in compatible["rules"] if rule["type"] == "required_status_checks"
        )
        status["parameters"]["do_not_enforce_on_create"] = False
        for enforcement, expected in (("disabled", 0), ("active", 1)):
            with self.subTest(enforcement=enforcement), tempfile.TemporaryDirectory() as temporary:
                temp = pathlib.Path(temporary)
                log = temp / "gh.log"
                self.make_fake_gh(temp)
                existing = {**compatible, "enforcement": enforcement}
                confirmation = (
                    "apply disabled ruleset adlc-default-branch to "
                    "github.com/example/project with integration ID 123456\n"
                )
                completed = self.run_helper(
                    [
                        "--apply",
                        "--integration-id",
                        "123456",
                        "--repo",
                        "example/project",
                    ],
                    input_text=confirmation,
                    environment={
                        "PATH": f"{temp}:{os.environ['PATH']}",
                        "GH_LOG": str(log),
                        "FAKE_LIST": '[[{"id":42,"name":"adlc-default-branch"}]]',
                        "FAKE_EXISTING": json.dumps(existing, separators=(",", ":")),
                    },
                )
                self.assertEqual(expected, completed.returncode)
                records = [
                    json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()
                ]
                self.assertFalse(any("--method" in record["args"] for record in records))

    def test_unsafe_normalized_ruleset_defaults_are_incompatible(self) -> None:
        dry = self.run_helper(["--dry-run", "--integration-id", "123456"])
        self.assertEqual(0, dry.returncode, dry.stderr)
        unsafe_cases = (
            ("bypass-missing", lambda value: value.pop("bypass_actors")),
            ("bypass-null", lambda value: value.update({"bypass_actors": None})),
            ("bypass-false", lambda value: value.update({"bypass_actors": False})),
            ("reviewers", lambda value: value["rules"][0]["parameters"].update(
                {"required_reviewers": [{"type": "Team", "id": 99}]}
            )),
            ("reviewers-null", lambda value: value["rules"][0]["parameters"].update(
                {"required_reviewers": None}
            )),
            ("reviewers-false", lambda value: value["rules"][0]["parameters"].update(
                {"required_reviewers": False}
            )),
            ("dismissal", lambda value: value["rules"][0]["parameters"].update(
                {"dismissal_restriction": {"enabled": True, "allowed_actors": []}}
            )),
            ("dismissal-false", lambda value: value["rules"][0]["parameters"].update(
                {"dismissal_restriction": False}
            )),
            ("contributors", lambda value: value["rules"][0]["parameters"].update(
                {"ignore_approvals_from_contributors": True}
            )),
            ("contributors-null", lambda value: value["rules"][0]["parameters"].update(
                {"ignore_approvals_from_contributors": None}
            )),
            ("create", lambda value: value["rules"][1]["parameters"].update(
                {"do_not_enforce_on_create": True}
            )),
            ("create-null", lambda value: value["rules"][1]["parameters"].update(
                {"do_not_enforce_on_create": None}
            )),
        )
        for name, mutate in unsafe_cases:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as temporary:
                value = json.loads(dry.stdout)
                value["id"] = 42
                mutate(value)
                temp = pathlib.Path(temporary)
                log = temp / "gh.log"
                self.make_fake_gh(temp)
                confirmation = (
                    "apply disabled ruleset adlc-default-branch to "
                    "github.com/example/project with integration ID 123456\n"
                )
                completed = self.run_helper(
                    ["--apply", "--integration-id", "123456", "--repo", "example/project"],
                    input_text=confirmation,
                    environment={
                        "PATH": f"{temp}:{os.environ['PATH']}",
                        "GH_LOG": str(log),
                        "FAKE_LIST": '[[{"id":42,"name":"adlc-default-branch"}]]',
                        "FAKE_EXISTING": json.dumps(value, separators=(",", ":")),
                    },
                )
                self.assertNotEqual(0, completed.returncode)
                records = [
                    json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()
                ]
                self.assertFalse(any("--method" in record["args"] for record in records))

    def test_helper_has_no_mutating_update_or_any_source_escape_hatch(self) -> None:
        text = self.script.read_text(encoding="utf-8")
        self.assertNotIn("--checks", text)
        for method in ("PATCH", "PUT", "DELETE"):
            self.assertNotIn(f"--method {method}", text)
        self.assertNotIn("integration_id: null", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
