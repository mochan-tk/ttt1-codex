#!/usr/bin/env python3
"""Fail when a pull request lacks the accepted Task ledger ritual."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


CLOSES_LINE = re.compile(r"^Closes #([1-9][0-9]*)$", re.MULTILINE)
PLAN_LINE = re.compile(r"^[ \t]*Plan:[ \t]+(\S+)[ \t]*$", re.MULTILINE)
CLAIM_HEADING = re.compile(r"^##[ \t]+(?:Start|Resume)(?:[ \t]+.*)?$")
INITIAL_PLAN_HEADING = re.compile(
    r"^##[ \t]+Plan(?:[ \t]+\(authoritative\)|[ \t]+—[ \t]+\S.*)?$"
)
REVISED_PLAN_HEADING = re.compile(
    r"^##[ \t]+Revised[ \t]+Plan"
    r"(?:[ \t]+(?:[1-9][0-9]*|v[1-9][0-9]*(?:\.[0-9]+)*|clarification))?"
    r"(?:[ \t]+—[ \t]+\S.*)?$"
)
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")
TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}
GRAPHQL_BATCH_SIZE = 100
MAX_GRAPHQL_PAGES = 100
MAX_TOTAL_HISTORY_PAGES = 100
COMMENT_EDIT_STATE_QUERY = """
query($ids: [ID!]!) {
  nodes(ids: $ids) {
    ... on IssueComment {
      id
      body
      lastEditedAt
      includesCreatedEdit
      userContentEdits { totalCount }
    }
  }
}
"""
COMMENT_HISTORY_QUERY = """
query($id: ID!, $after: String) {
  node(id: $id) {
    ... on IssueComment {
      body
      lastEditedAt
      includesCreatedEdit
      userContentEdits(first: 100, after: $after) {
        totalCount
        nodes { diff }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""


class ApiError(RuntimeError):
    """A fail-closed GitHub API acquisition error."""


@dataclass(frozen=True)
class CommentEditState:
    body: str
    last_edited_at: str | None
    total_count: int

    @property
    def edited(self) -> bool:
        return self.last_edited_at is not None


@dataclass(frozen=True)
class CommentRecord:
    identifier: int
    body: str
    created_at: datetime
    updated_at: datetime
    kind: str
    historical_kinds: frozenset[str]
    content_edited: bool

    @property
    def chronology(self) -> tuple[datetime, int]:
        return self.created_at, self.identifier


class GitHubApi:
    def __init__(
        self,
        token: str,
        base_url: str = "https://api.github.com",
        graphql_url: str = "https://api.github.com/graphql",
        attempts: int = 3,
        timeout: int = 20,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.graphql_url = graphql_url
        self.attempts = attempts
        self.timeout = timeout
        self.sleeper = sleeper

    def _request_once(self, path: str) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        request = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "codex-adlc-task-ritual",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _graphql_once(self, query: str, variables: Mapping[str, Any]) -> Any:
        request = Request(
            self.graphql_url,
            data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
            method="POST",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "codex-adlc-task-ritual",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_json(self, path: str) -> Any:
        last_error: BaseException | None = None
        for attempt in range(1, self.attempts + 1):
            try:
                return self._request_once(path)
            except HTTPError as error:
                if error.code not in TRANSIENT_HTTP_CODES:
                    raise ApiError(f"GitHub API returned HTTP {error.code} for {path}") from error
                last_error = error
            except (URLError, TimeoutError, UnicodeError, json.JSONDecodeError) as error:
                last_error = error

            if attempt < self.attempts:
                self.sleeper(float(2 ** (attempt - 1)))

        error_name = type(last_error).__name__ if last_error is not None else "unknown error"
        raise ApiError(
            f"GitHub API request failed after {self.attempts} attempt(s) for {path}: {error_name}"
        ) from last_error

    def get_object(self, path: str) -> Mapping[str, Any]:
        payload = self.get_json(path)
        if not isinstance(payload, dict):
            raise ApiError(f"GitHub API returned a non-object for {path}")
        return payload

    def get_paginated(self, path: str) -> list[Mapping[str, Any]]:
        values: list[Mapping[str, Any]] = []
        separator = "&" if "?" in path else "?"
        for page in range(1, 101):
            page_path = f"{path}{separator}per_page=100&page={page}"
            payload = self.get_json(page_path)
            if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
                raise ApiError(f"GitHub API returned a non-object list for {page_path}")
            values.extend(payload)
            if len(payload) < 100:
                return values
        raise ApiError(f"GitHub API pagination exceeded 100 pages for {path}")

    def post_graphql(self, query: str, variables: Mapping[str, Any]) -> Mapping[str, Any]:
        last_error: BaseException | None = None
        for attempt in range(1, self.attempts + 1):
            try:
                payload = self._graphql_once(query, variables)
                if not isinstance(payload, dict):
                    raise ApiError("GitHub GraphQL returned a non-object response")
                if payload.get("errors"):
                    raise ApiError("GitHub GraphQL returned an error response")
                return payload
            except HTTPError as error:
                if error.code not in TRANSIENT_HTTP_CODES:
                    raise ApiError(f"GitHub GraphQL returned HTTP {error.code}") from error
                last_error = error
            except (URLError, TimeoutError, UnicodeError, json.JSONDecodeError) as error:
                last_error = error
            except ApiError as error:
                last_error = error

            if attempt < self.attempts:
                self.sleeper(float(2 ** (attempt - 1)))

        if last_error is None:
            error_name = "unknown error"
        elif isinstance(last_error, ApiError):
            error_name = str(last_error)
        else:
            error_name = type(last_error).__name__
        raise ApiError(
            "GitHub GraphQL request failed after "
            f"{self.attempts} attempt(s): {error_name}"
        ) from last_error

    def get_issue_comment_edit_states(
        self, node_ids: Sequence[str]
    ) -> dict[str, CommentEditState]:
        if len(set(node_ids)) != len(node_ids) or not all(node_ids):
            raise ApiError("Task comments contain duplicate or empty GraphQL node ids")

        states: dict[str, CommentEditState] = {}
        for offset in range(0, len(node_ids), GRAPHQL_BATCH_SIZE):
            batch = list(node_ids[offset : offset + GRAPHQL_BATCH_SIZE])
            payload = self.post_graphql(COMMENT_EDIT_STATE_QUERY, {"ids": batch})
            data = payload.get("data")
            nodes = data.get("nodes") if isinstance(data, dict) else None
            if not isinstance(nodes, list) or len(nodes) != len(batch):
                raise ApiError("could not read edit state for every Task comment")

            returned: set[str] = set()
            for node in nodes:
                identifier = node.get("id") if isinstance(node, dict) else None
                body = node.get("body") if isinstance(node, dict) else None
                last_edited_at = node.get("lastEditedAt") if isinstance(node, dict) else None
                includes_created = (
                    node.get("includesCreatedEdit") if isinstance(node, dict) else None
                )
                edits = node.get("userContentEdits") if isinstance(node, dict) else None
                total_count = edits.get("totalCount") if isinstance(edits, dict) else None
                if (
                    not isinstance(identifier, str)
                    or identifier not in batch
                    or not isinstance(body, str)
                    or type(total_count) is not int
                ):
                    raise ApiError("Task comment edit state contains an unknown node")
                if identifier in returned:
                    raise ApiError(f"Task comment edit state duplicated node {identifier}")
                returned.add(identifier)

                if last_edited_at is None:
                    if includes_created is not False or total_count != 0:
                        raise ApiError(
                            f"comment node {identifier} has inconsistent unedited state"
                        )
                else:
                    if not isinstance(last_edited_at, str) or not last_edited_at:
                        raise ApiError(
                            f"comment node {identifier} has an unreadable edit timestamp"
                        )
                    if includes_created is not True or total_count < 2:
                        raise ApiError(
                            f"comment node {identifier} edit history omits its creation snapshot"
                        )
                states[identifier] = CommentEditState(body, last_edited_at, total_count)

            if returned != set(batch):
                raise ApiError("could not match edit state to every Task comment")
        return states

    def _issue_comment_history_page(
        self, node_id: str, after: str | None
    ) -> tuple[str, str, int, list[str], bool, str | None]:
        payload = self.post_graphql(COMMENT_HISTORY_QUERY, {"id": node_id, "after": after})
        data = payload.get("data")
        node = data.get("node") if isinstance(data, dict) else None
        body = node.get("body") if isinstance(node, dict) else None
        last_edited_at = node.get("lastEditedAt") if isinstance(node, dict) else None
        includes_created = node.get("includesCreatedEdit") if isinstance(node, dict) else None
        edits = node.get("userContentEdits") if isinstance(node, dict) else None
        nodes = edits.get("nodes") if isinstance(edits, dict) else None
        total_count = edits.get("totalCount") if isinstance(edits, dict) else None
        page_info = edits.get("pageInfo") if isinstance(edits, dict) else None
        has_next = page_info.get("hasNextPage") if isinstance(page_info, dict) else None
        end_cursor = page_info.get("endCursor") if isinstance(page_info, dict) else None
        if (
            not isinstance(body, str)
            or not isinstance(last_edited_at, str)
            or not last_edited_at
            or includes_created is not True
            or type(total_count) is not int
            or total_count < 1
            or not isinstance(nodes, list)
            or type(has_next) is not bool
            or (has_next and (not isinstance(end_cursor, str) or not end_cursor))
        ):
            raise ApiError(f"could not read complete edit history for comment node {node_id}")

        snapshots: list[str] = []
        for edit in nodes:
            snapshot = edit.get("diff") if isinstance(edit, dict) else None
            if not isinstance(snapshot, str):
                raise ApiError(f"comment node {node_id} has an unreadable edit snapshot")
            snapshots.append(snapshot)
        return body, last_edited_at, total_count, snapshots, has_next, end_cursor

    def get_issue_comment_history(
        self, node_id: str, expected_state: CommentEditState | None = None
    ) -> list[str]:
        snapshots: list[str] = []
        seen_cursors: set[str] = set()
        after: str | None = None
        expected_body = expected_state.body if expected_state is not None else None
        expected_timestamp: str | None = None
        expected_count: int | None = None

        for _page in range(MAX_GRAPHQL_PAGES):
            body, timestamp, total_count, page_snapshots, has_next, end_cursor = (
                self._issue_comment_history_page(node_id, after)
            )
            if expected_body is None:
                expected_body = body
            if expected_timestamp is None and expected_state is not None:
                expected_timestamp = expected_state.last_edited_at
                expected_count = expected_state.total_count
            elif expected_timestamp is None:
                expected_timestamp = timestamp
                expected_count = total_count
            if (
                body != expected_body
                or timestamp != expected_timestamp
                or total_count != expected_count
            ):
                raise ApiError(f"comment node {node_id} changed while reading edit history")
            snapshots.extend(page_snapshots)
            if not has_next:
                if (
                    expected_count is None
                    or len(snapshots) != expected_count
                    or len(snapshots) < 2
                    or expected_body not in snapshots
                ):
                    raise ApiError(
                        f"could not read complete edit history for comment node {node_id}"
                    )
                return snapshots
            if end_cursor is None or end_cursor in seen_cursors:
                raise ApiError(f"edit-history cursor stalled for comment node {node_id}")
            seen_cursors.add(end_cursor)
            after = end_cursor

        raise ApiError(
            f"edit history exceeded {MAX_GRAPHQL_PAGES} pages for comment node {node_id}"
        )


def fetch_comment_histories(
    api: GitHubApi, comments: Sequence[Mapping[str, Any]]
) -> dict[int, list[str]]:
    # REST updated_at has second precision and can change without a body edit.
    # Ask GraphQL for every comment's explicit content-edit state instead.
    comments_by_node: dict[str, tuple[int, str]] = {}
    for comment in comments:
        identifier = comment.get("id")
        node_id = comment.get("node_id")
        body = comment.get("body")
        if (
            not isinstance(identifier, int)
            or not isinstance(node_id, str)
            or not node_id
            or not isinstance(body, str)
        ):
            raise ApiError("a Task comment lacks an integer id, body, or GraphQL node id")
        if node_id in comments_by_node or any(
            existing_id == identifier for existing_id, _body in comments_by_node.values()
        ):
            raise ApiError("Task comments contain duplicate ids or GraphQL node ids")
        comments_by_node[node_id] = (identifier, body)

    states = api.get_issue_comment_edit_states(list(comments_by_node))
    if set(states) != set(comments_by_node):
        raise ApiError("could not match edit state to every Task comment")
    history_pages = sum(
        (state.total_count + GRAPHQL_BATCH_SIZE - 1) // GRAPHQL_BATCH_SIZE
        for state in states.values()
        if state.edited
    )
    if history_pages > MAX_TOTAL_HISTORY_PAGES:
        raise ApiError(
            "Task comment edit histories require "
            f"{history_pages} GraphQL page(s); safety budget is {MAX_TOTAL_HISTORY_PAGES}"
        )

    histories: dict[int, list[str]] = {}
    for node_id, (identifier, body) in comments_by_node.items():
        state = states[node_id]
        if state.body != body:
            raise ApiError(f"comment node {node_id} changed while reading edit state")
        if state.edited:
            histories[identifier] = api.get_issue_comment_history(node_id, state)
    return histories


def _timestamp(value: Any, context: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context} timestamp is missing")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def _first_content_line(body: str) -> str:
    return next((line.strip() for line in body.splitlines() if line.strip()), "")


def _comment_kind(body: str) -> str:
    heading = _first_content_line(body)
    if CLAIM_HEADING.fullmatch(heading):
        return "claim"
    if REVISED_PLAN_HEADING.fullmatch(heading):
        return "revised-plan"
    if INITIAL_PLAN_HEADING.fullmatch(heading):
        return "initial-plan"
    return "other"


def _comment_records(
    comments: Sequence[Mapping[str, Any]],
    errors: list[str],
    comment_histories: Mapping[int, Sequence[str]] | None = None,
) -> list[CommentRecord]:
    records: list[CommentRecord] = []
    histories = comment_histories or {}
    for comment in comments:
        identifier = comment.get("id")
        body = comment.get("body")
        if not isinstance(identifier, int) or not isinstance(body, str):
            errors.append("Task comments contain an entry without an integer id or string body")
            continue
        try:
            created_at = _timestamp(comment.get("created_at"), f"comment {identifier} created_at")
            updated_at = _timestamp(comment.get("updated_at"), f"comment {identifier} updated_at")
        except (TypeError, ValueError) as error:
            errors.append(str(error))
            continue
        history = histories.get(identifier, ())
        if not all(isinstance(snapshot, str) for snapshot in history):
            errors.append(f"comment {identifier} has a non-string edit-history snapshot")
            history = ()
        records.append(
            CommentRecord(
                identifier=identifier,
                body=body,
                created_at=created_at,
                updated_at=updated_at,
                kind=_comment_kind(body),
                historical_kinds=frozenset(_comment_kind(snapshot) for snapshot in history),
                content_edited=identifier in histories,
            )
        )
    return records


def _plan_target(url: str, server_url: str) -> tuple[str, int, int] | None:
    parsed = urlparse(url)
    server = urlparse(server_url.rstrip("/"))
    if (parsed.scheme.casefold(), parsed.netloc.casefold()) != (
        server.scheme.casefold(),
        server.netloc.casefold(),
    ):
        return None
    parts = [part for part in parsed.path.split("/") if part]
    fragment = re.fullmatch(r"issuecomment-([1-9][0-9]*)", parsed.fragment)
    if len(parts) != 4 or parts[2] != "issues" or not parts[3].isdigit() or fragment is None:
        return None
    return f"{parts[0]}/{parts[1]}", int(parts[3]), int(fragment.group(1))


def _issue_labels(issue: Mapping[str, Any]) -> set[str]:
    labels = issue.get("labels")
    if not isinstance(labels, list):
        return set()
    names: set[str] = set()
    for label in labels:
        if isinstance(label, str):
            names.add(label)
        elif isinstance(label, dict) and isinstance(label.get("name"), str):
            names.add(label["name"])
    return names


def _commit_times(commits: Sequence[Mapping[str, Any]], errors: list[str]) -> list[datetime]:
    values: list[datetime] = []
    for index, item in enumerate(commits, 1):
        commit = item.get("commit")
        if not isinstance(commit, dict):
            errors.append(f"PR commit {index} lacks commit metadata")
            continue
        committer = commit.get("committer")
        author = commit.get("author")
        raw = committer.get("date") if isinstance(committer, dict) else None
        if raw is None and isinstance(author, dict):
            raw = author.get("date")
        try:
            values.append(_timestamp(raw, f"PR commit {index}"))
        except (TypeError, ValueError) as error:
            errors.append(str(error))
    return values


def closing_task_numbers(body: str) -> list[int]:
    return [int(value) for value in CLOSES_LINE.findall(body)]


def primary_closing_errors(body: str) -> list[str]:
    errors: list[str] = []
    task_numbers = closing_task_numbers(body)
    if len(task_numbers) != 1:
        errors.append(
            "PR body must contain exactly one canonical local 'Closes #N' line; "
            f"found {len(task_numbers)}"
        )
    first_line = _first_content_line(body)
    if re.fullmatch(r"Closes #[1-9][0-9]*", first_line) is None:
        errors.append("the canonical 'Closes #N' declaration must be the first nonblank PR-body line")
    return errors


def validate_ritual(
    repository: str,
    server_url: str,
    pull_request: Mapping[str, Any],
    issue: Mapping[str, Any],
    comments: Sequence[Mapping[str, Any]],
    commits: Sequence[Mapping[str, Any]],
    comment_histories: Mapping[int, Sequence[str]] | None = None,
) -> list[str]:
    errors: list[str] = []
    body = pull_request.get("body")
    if not isinstance(body, str):
        body = ""

    errors.extend(primary_closing_errors(body))
    task_numbers = closing_task_numbers(body)
    if errors:
        return errors
    task_number = task_numbers[0]

    if issue.get("number") != task_number:
        errors.append(f"closing Task #{task_number} did not resolve to the same Issue")
    if "type:task" not in _issue_labels(issue):
        errors.append(
            f"closing Issue #{task_number} is not labeled type:task; "
            f"apply it with: gh issue edit {task_number} --add-label type:task"
        )

    plan_urls = PLAN_LINE.findall(body)
    if len(plan_urls) != 1:
        errors.append(f"PR body must contain exactly one Plan: URL; found {len(plan_urls)}")
        return errors
    target = _plan_target(plan_urls[0], server_url)
    if target is None:
        errors.append("Plan: value is not a canonical GitHub Issue comment URL")
        return errors
    target_repository, target_issue, target_comment = target
    if target_repository.casefold() != repository.casefold() or target_issue != task_number:
        errors.append("Plan: URL must resolve to the same repository and Task as Closes #N")

    records = _comment_records(comments, errors, comment_histories)
    claims = [record for record in records if record.kind == "claim"]
    initial_plans = [record for record in records if record.kind == "initial-plan"]
    plans = [record for record in records if record.kind in {"initial-plan", "revised-plan"}]
    if not claims:
        errors.append(f"Task #{task_number} has no leading ## Start or ## Resume comment")
    edited_claim_ids = [
        record.identifier
        for record in records
        if record.content_edited
        and (record.kind == "claim" or "claim" in record.historical_kinds)
    ]
    if edited_claim_ids:
        rendered = ", ".join(f"issuecomment-{identifier}" for identifier in edited_claim_ids)
        errors.append(f"Start/Resume comments must never be edited; found {rendered}")
    if len(initial_plans) != 1:
        errors.append(
            f"Task #{task_number} must have exactly one leading ## Plan comment; "
            f"found {len(initial_plans)}"
        )
    if not plans:
        return errors

    latest_plan = max(plans, key=lambda record: record.chronology)
    if latest_plan.identifier != target_comment:
        errors.append(
            "Plan: URL must point to the latest Plan or Revised Plan comment "
            f"(expected issuecomment-{latest_plan.identifier})"
        )
    edited_plan_ids = [
        record.identifier
        for record in records
        if record.content_edited
        and (
            record.kind in {"initial-plan", "revised-plan"}
            or not record.historical_kinds.isdisjoint({"initial-plan", "revised-plan"})
        )
    ]
    if edited_plan_ids:
        rendered = ", ".join(f"issuecomment-{identifier}" for identifier in edited_plan_ids)
        errors.append(f"Plan/Revised Plan comments must never be edited; found {rendered}")
    if len(initial_plans) == 1 and claims:
        initial_plan = initial_plans[0]
        if not any(claim.chronology < initial_plan.chronology for claim in claims):
            errors.append("a ## Start or ## Resume comment must precede the initial ## Plan comment")

    commit_times = _commit_times(commits, errors)
    if not commit_times:
        errors.append("pull request has no commit timestamp to prove Plan chronology")
    elif len(initial_plans) == 1:
        initial_plan = initial_plans[0]
        if initial_plan.created_at >= min(commit_times):
            errors.append("the initial ## Plan comment must predate the earliest pull-request commit")

    return errors


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Repository as owner/name. Default: GITHUB_REPOSITORY.")
    parser.add_argument("--pr", type=int, help="Pull-request number. Default: PR_NUMBER.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repository = args.repo or os.environ.get("GITHUB_REPOSITORY", "")
    raw_pr = args.pr if args.pr is not None else os.environ.get("PR_NUMBER", "")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    graphql_url = os.environ.get("GITHUB_GRAPHQL_URL", "https://api.github.com/graphql")

    if not REPOSITORY.fullmatch(repository):
        print("check-task-ritual: ERROR — repository must be owner/name", file=sys.stderr)
        return 2
    try:
        pr_number = int(raw_pr)
    except (TypeError, ValueError):
        print("check-task-ritual: ERROR — PR number is required", file=sys.stderr)
        return 2
    if pr_number < 1 or not token:
        print("check-task-ritual: ERROR — positive PR number and GH_TOKEN are required", file=sys.stderr)
        return 2

    api = GitHubApi(token, api_url, graphql_url)
    try:
        pull_request = api.get_object(f"repos/{repository}/pulls/{pr_number}")
        body = pull_request.get("body") if isinstance(pull_request.get("body"), str) else ""
        closing_errors = primary_closing_errors(body)
        task_numbers = closing_task_numbers(body)
        if closing_errors:
            errors = closing_errors
        else:
            task_number = task_numbers[0]
            issue = api.get_object(f"repos/{repository}/issues/{task_number}")
            comments = api.get_paginated(f"repos/{repository}/issues/{task_number}/comments")
            comment_histories = fetch_comment_histories(api, comments)
            commits = api.get_paginated(f"repos/{repository}/pulls/{pr_number}/commits")
            errors = validate_ritual(
                repository,
                server_url,
                pull_request,
                issue,
                comments,
                commits,
                comment_histories,
            )
    except ApiError as error:
        print(f"check-task-ritual: FAIL — {error}", file=sys.stderr)
        return 1

    if errors:
        print(f"check-task-ritual: FAIL — {len(errors)} ledger violation(s)", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(
        f"check-task-ritual: OK — PR #{pr_number} has one Task, a preceding claim, "
        "and an immutable authoritative Plan with pre-commit initial chronology."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
