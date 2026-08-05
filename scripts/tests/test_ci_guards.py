#!/usr/bin/env python3
"""Regression fixtures for the deterministic CI guards."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest
from unittest import mock
from urllib.error import URLError


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_action_pins as action_pins  # noqa: E402
import check_task_ritual as task_ritual  # noqa: E402


SHA_A = "1" * 40
SHA_B = "a" * 40
REPOSITORY = "example/project"
SERVER_URL = "https://github.com"


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
    return task_ritual.validate_ritual(
        REPOSITORY,
        SERVER_URL,
        fixture["pull_request"],
        fixture["issue"],
        fixture["comments"],
        fixture["commits"],
    )


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

    def test_discovery_requests_yml_and_yaml_tracked_paths(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b".github/workflows/a.yaml\0.github/workflows/b.yml\0",
        )
        with mock.patch.object(action_pins.subprocess, "run", return_value=completed) as run:
            paths = action_pins.tracked_workflow_paths(ROOT)
        self.assertEqual(
            [ROOT / ".github/workflows/a.yaml", ROOT / ".github/workflows/b.yml"],
            paths,
        )
        command = run.call_args.args[0]
        self.assertIn(".github/workflows/*.yml", command)
        self.assertIn(".github/workflows/*.yaml", command)


class TaskRitualTests(unittest.TestCase):
    def test_valid_task_ritual_passes(self) -> None:
        self.assertEqual([], ritual_errors(valid_fixture()))

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
        self.assertIn("not labeled type:task", "\n".join(ritual_errors(fixture)))

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
