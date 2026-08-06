#!/usr/bin/env python3
"""Regression fixtures for the deterministic CI guards."""

from __future__ import annotations

import pathlib
import re
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


class ScaffoldContractTests(unittest.TestCase):
    def test_ci_rechecks_pull_request_body_edits_and_discovers_guard_tests(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        trigger = re.compile(
            r"(?m)^  pull_request:\n"
            r"(?:    #.*\n)*"
            r"    types: \[opened, synchronize, reopened, edited\]$"
        )
        self.assertRegex(workflow, trigger)
        discovery_command = "python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v"
        self.assertRegex(
            workflow,
            re.compile(rf"(?m)^[ \t]+run: {re.escape(discovery_command)}$"),
        )

    def test_readme_lists_guard_and_action_pin_checks(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v",
            readme,
        )
        self.assertIn("python3 scripts/check_action_pins.py", readme)


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
