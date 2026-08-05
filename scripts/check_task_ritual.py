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
INITIAL_PLAN_HEADING = re.compile(r"^##[ \t]+Plan(?:[ \t]+.*)?$")
REVISED_PLAN_HEADING = re.compile(r"^##[ \t]+Revised[ \t]+Plan(?:[ \t]+.*)?$")
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")
TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}


class ApiError(RuntimeError):
    """A fail-closed GitHub API acquisition error."""


@dataclass(frozen=True)
class CommentRecord:
    identifier: int
    body: str
    created_at: datetime
    updated_at: datetime
    kind: str

    @property
    def chronology(self) -> tuple[datetime, int]:
        return self.created_at, self.identifier


class GitHubApi:
    def __init__(
        self,
        token: str,
        base_url: str = "https://api.github.com",
        attempts: int = 3,
        timeout: int = 20,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")
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


def _comment_records(comments: Sequence[Mapping[str, Any]], errors: list[str]) -> list[CommentRecord]:
    records: list[CommentRecord] = []
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
        records.append(
            CommentRecord(identifier, body, created_at, updated_at, _comment_kind(body))
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
        errors.append(f"closing Issue #{task_number} is not labeled type:task")

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

    records = _comment_records(comments, errors)
    claims = [record for record in records if record.kind == "claim"]
    initial_plans = [record for record in records if record.kind == "initial-plan"]
    plans = [record for record in records if record.kind in {"initial-plan", "revised-plan"}]
    if not claims:
        errors.append(f"Task #{task_number} has no leading ## Start or ## Resume comment")
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
        record.identifier for record in plans if record.created_at != record.updated_at
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

    api = GitHubApi(token, api_url)
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
            commits = api.get_paginated(f"repos/{repository}/pulls/{pr_number}/commits")
            errors = validate_ritual(
                repository,
                server_url,
                pull_request,
                issue,
                comments,
                commits,
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
