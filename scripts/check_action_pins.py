#!/usr/bin/env python3
"""Fail when a tracked workflow uses a mutable external Action reference."""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW_PATHSPECS = (
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
)
USES_LINE = re.compile(r"^[ \t]*(?:-[ \t]+)?uses[ \t]*:[ \t]*(?P<value>.*)$")
FULL_SHA_REFERENCE = re.compile(r"^[^/@\s]+/[^@\s]+@[0-9A-Fa-f]{40}$")
VERSION_COMMENT = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def validate_workflow_text(path: str, text: str) -> tuple[list[Violation], int]:
    """Return violations and the number of Action references inspected."""

    violations: list[Violation] = []
    reference_count = 0

    for line_number, line in enumerate(text.splitlines(), 1):
        match = USES_LINE.match(line)
        if not match:
            continue

        reference_count += 1
        raw_value = match.group("value").strip()
        reference_part, separator, comment_part = raw_value.partition("#")
        reference = _unquote(reference_part.strip())
        version = comment_part.strip() if separator else ""

        if not reference:
            violations.append(Violation(path, line_number, "uses: reference is empty"))
            continue

        if reference.startswith("./"):
            continue

        problems: list[str] = []
        if not FULL_SHA_REFERENCE.fullmatch(reference):
            problems.append("external Action must be pinned to a full 40-hex commit SHA")
        if not VERSION_COMMENT.fullmatch(version):
            problems.append("external Action must end with a readable '# vX.Y.Z' comment")
        if problems:
            violations.append(Violation(path, line_number, "; ".join(problems)))

    return violations, reference_count


def tracked_workflow_paths(root: pathlib.Path) -> list[pathlib.Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", *WORKFLOW_PATHSPECS],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    )
    entries = result.stdout.decode("utf-8").split("\0")
    return [root / entry for entry in sorted(item for item in entries if item)]


def validate_paths(root: pathlib.Path, paths: Iterable[pathlib.Path]) -> tuple[list[Violation], int, int]:
    violations: list[Violation] = []
    reference_count = 0
    file_count = 0

    for path in paths:
        file_count += 1
        relative = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
        found, count = validate_workflow_text(relative, path.read_text(encoding="utf-8"))
        violations.extend(found)
        reference_count += count

    return violations, reference_count, file_count


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=pathlib.Path,
        help="Optional workflow paths. By default, inspect tracked workflow YAML files.",
    )
    parser.add_argument("--root", type=pathlib.Path, default=ROOT, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = args.root.resolve()
    paths = [(root / path).resolve() if not path.is_absolute() else path.resolve() for path in args.paths]

    try:
        if not paths:
            paths = tracked_workflow_paths(root)
        if not paths:
            print("check-action-pins: FAIL — no tracked workflow YAML files found", file=sys.stderr)
            return 1
        violations, reference_count, file_count = validate_paths(root, paths)
    except (OSError, subprocess.CalledProcessError, UnicodeError) as error:
        print(f"check-action-pins: ERROR — validator could not inspect workflows: {error}", file=sys.stderr)
        return 2

    if violations:
        print(f"check-action-pins: FAIL — {len(violations)} mutable or unreadable reference(s)", file=sys.stderr)
        for violation in violations:
            print(f"  {violation.render()}", file=sys.stderr)
        return 1

    print(
        "check-action-pins: OK — "
        f"{reference_count} Action reference(s) across {file_count} tracked workflow file(s) are immutable."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
