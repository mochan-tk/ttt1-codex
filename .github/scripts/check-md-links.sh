#!/usr/bin/env bash
# Validate repository-local Markdown links and documented scaffold paths.
# External URLs are intentionally not fetched: this check must be deterministic.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

command -v python3 >/dev/null 2>&1 || {
  echo "check-md-links: ERROR — python3 is required" >&2
  exit 2
}

python3 - "$ROOT" <<'PY'
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import urllib.parse

root = pathlib.Path(sys.argv[1]).resolve()
control_prefixes = (
    ".github/docs/",
    ".github/scripts/",
    ".agents/",
    ".codex/",
)
control_files = {
    "AGENTS.md",
    ".github/CODEOWNERS",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/epic.yml",
    ".github/ISSUE_TEMPLATE/task.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/dependabot.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/retro-hygiene.yml",
}


def in_control_scope(item: str) -> bool:
    return item in control_files or item.startswith(control_prefixes)


tracked = subprocess.run(
    ["git", "ls-files", "-z"],
    check=True,
    stdout=subprocess.PIPE,
).stdout.decode("utf-8").split("\0")
markdown_files = [
    pathlib.Path(item)
    for item in tracked
    if item.endswith(".md") and in_control_scope(item)
]

inline_link = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
reference_link = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
documented_path = re.compile(
    r"(?<![A-Za-z0-9_.-])"
    r"((?:\.agents|\.codex|\.github)/"
    r"[A-Za-z0-9_./*?-]+\.(?:md|ya?ml|toml|sh|json))"
)

# These are deliberate negative examples in the accepted requirements.
allowed_missing = {".github/copilot-instructions.md"}
errors: list[str] = []
checked_links = 0
checked_paths = 0
checked_external = 0


def strip_destination(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.index(">")]
    # Markdown titles follow the destination after whitespace. Repository
    # paths in this scaffold do not contain unescaped spaces.
    return value.split()[0] if value else ""


def external_destination(destination: str) -> tuple[bool, str | None]:
    try:
        parsed = urllib.parse.urlsplit(destination)
        hostname = parsed.hostname
        # Accessing port performs urllib's range and syntax validation.
        parsed.port
    except ValueError as error:
        return True, f"malformed external link ({error})"
    if not parsed.scheme and not parsed.netloc:
        return False, None
    scheme = parsed.scheme.lower()
    if scheme in {"http", "https"}:
        if not hostname or any(char.isspace() for char in hostname):
            return True, "HTTP(S) link must include a valid host"
        return True, None
    if scheme == "mailto":
        if not parsed.path or "@" not in parsed.path:
            return True, "mailto link must include an address"
        return True, None
    if scheme == "tel":
        if not parsed.path:
            return True, "tel link must include a number"
        return True, None
    if not scheme and parsed.netloc:
        if not hostname or any(char.isspace() for char in hostname):
            return True, "network-path link must include a valid host"
        return True, None
    return True, f"unsupported or malformed external-link scheme: {scheme or '<none>'}"


def local_target(source: pathlib.Path, destination: str) -> pathlib.Path | None:
    parsed = urllib.parse.urlsplit(destination)
    if not parsed.path or parsed.path == "/":
        return None
    decoded = urllib.parse.unquote(parsed.path)
    if decoded.startswith("/"):
        candidate = root / decoded.lstrip("/")
    else:
        candidate = root / source.parent / decoded
    return candidate.resolve()


for relative in markdown_files:
    source = root / relative
    text = source.read_text(encoding="utf-8")
    destinations = [match.group(1) for match in inline_link.finditer(text)]
    destinations.extend(match.group(1) for match in reference_link.finditer(text))
    for raw in destinations:
        destination = strip_destination(raw)
        is_external, external_error = external_destination(destination)
        if is_external:
            checked_external += 1
            if external_error:
                errors.append(f"{relative}: {external_error}: {destination}")
            continue
        candidate = local_target(relative, destination)
        if candidate is None:
            continue
        checked_links += 1
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"{relative}: link escapes the repository: {destination}")
            continue
        if not candidate.exists():
            errors.append(f"{relative}: missing linked path: {destination}")

    for match in documented_path.finditer(text):
        documented = match.group(1).rstrip(".,;:")
        if "*" in documented or "?" in documented or documented in allowed_missing:
            continue
        checked_paths += 1
        if not (root / documented).exists():
            errors.append(f"{relative}: missing documented path: {documented}")

if errors:
    print(f"check-md-links: FAIL — {len(errors)} unresolved reference(s)", file=sys.stderr)
    for error in sorted(set(errors)):
        print(f"  {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    "check-md-links: OK — "
    f"{len(markdown_files)} Markdown file(s), "
    f"{checked_links} local link(s), {checked_external} external link(s), "
    f"and {checked_paths} documented path reference(s) checked."
)
PY
