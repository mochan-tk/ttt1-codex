#!/usr/bin/env bash
# Build the deterministic ADLC retro-hygiene report and, only when explicitly
# authorized, create the idempotent monthly review Issue.
#
# Usage:
#   .github/scripts/retro-hygiene.sh [-R owner/repo]
#   .github/scripts/retro-hygiene.sh --create-issue [-R owner/repo]
#   .github/scripts/retro-hygiene.sh --help
#
# Report mode is read-only. --create-issue is the sole mutation mode. The
# workflow grants issues:write only to its scheduled or explicitly requested
# creation job.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUDGET_TARGET=150
CREATE_ISSUE=0
REPOSITORY=""

usage() { sed -n '2,/^$/{s/^# \{0,1\}//p;}' "$0"; }
fail() { echo "retro-hygiene: error — $*" >&2; exit 1; }
usage_error() {
  echo "retro-hygiene: error — $*" >&2
  echo "Run '$(basename "$0") --help' for usage." >&2
  exit 2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --create-issue) CREATE_ISSUE=1 ;;
    -R|--repo)
      [ -n "${2:-}" ] || usage_error "$1 requires owner/repo"
      REPOSITORY="$2"
      shift
      ;;
    -h|--help) usage; exit 0 ;;
    *) usage_error "unknown argument: $1" ;;
  esac
  shift
done

command -v gh >/dev/null 2>&1 || fail "gh CLI is required"
if [ -z "$REPOSITORY" ]; then
  REPOSITORY="$(gh repo view --json nameWithOwner --jq .nameWithOwner)" \
    || fail "could not resolve the current GitHub repository"
fi
if [[ ! "$REPOSITORY" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  usage_error "repository must be owner/repo: $REPOSITORY"
fi

MONTH="$(date -u +%Y-%m)"
ISSUE_TITLE="Retro hygiene review ${MONTH}"
MARKER="<!-- adlc-retro-hygiene:${MONTH} -->"

list_candidates() {
  gh issue list -R "$REPOSITORY" --label retro:candidate --state open --limit 1000 \
    --json number,title,comments,createdAt,url \
    --jq 'def marked:
            test("^\\s*(?:<!--\\s*retro-occurrence\\s*-->\\s*)?Occurrence(?:\\s+evidence)?:\\s*"; "i");
          def evidence:
            (test("https://github\\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:issues|pull)/[0-9]+"; "i")
             or test("(^|[[:space:](])(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#[0-9]+([^0-9]|$)"));
          .[] | [.number,
                 (1 + ([.comments[] | (.body // "") | select(marked)] | length)),
                 ([.comments[] | (.body // "") | select((evidence) and (marked | not))] | length),
                 (((now - (.createdAt | fromdateiso8601)) / 86400) | floor),
                 .title,
                 .url] | @tsv'
}

budget_rows() {
  local found file relative lines status
  found=0
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    found=1
    relative="${file#"$ROOT"/}"
    lines="$(wc -l < "$file" | tr -d '[:space:]')"
    status="under target"
    if [ "$lines" -gt "$BUDGET_TARGET" ]; then
      status="**OVER TARGET**"
    fi
    printf '| `%s` | %s | %s | %s |\n' "$relative" "$lines" "$BUDGET_TARGET" "$status"
  done < <(git -C "$ROOT" ls-files 'AGENTS.md' '**/AGENTS.md' \
    | while IFS= read -r relative; do printf '%s/%s\n' "$ROOT" "$relative"; done \
    | LC_ALL=C sort)
  [ "$found" -eq 1 ] || fail "no AGENTS.md file found for budget measurement"
}

build_report() {
  local candidates number occurrences unclassified age title url status
  local total overdue unclassified_total rows budgets
  candidates="$(list_candidates)" || fail "could not read retro:candidate Issues from $REPOSITORY"
  total=0
  overdue=0
  unclassified_total=0
  rows=""
  while IFS=$'\t' read -r number occurrences unclassified age title url; do
    [ -n "$number" ] || continue
    total=$((total + 1))
    status="ok"
    if [ "$occurrences" -ge 2 ]; then
      status="**PROMOTION OVERDUE**"
      overdue=$((overdue + 1))
    elif [ "$unclassified" -gt 0 ]; then
      status="**CONFIRM OCCURRENCE EVIDENCE**"
    fi
    unclassified_total=$((unclassified_total + unclassified))
    title="${title//|/\\|}"
    rows="${rows}| [#${number}](${url}) | ${title} | ${occurrences} | ${unclassified} | ${age} | ${status} |
"
  done <<EOF
$candidates
EOF

  if [ "$total" -eq 0 ]; then
    rows="No open \`retro:candidate\` Issues — the candidate ledger is clean."
  else
    rows="| Issue | Title | Confirmed occurrences | Unmarked evidence links | Age (days) | Status |
|---|---|---:|---:|---:|---|
${rows}
${total} open candidate(s); ${overdue} at or above the two-occurrence promotion threshold; ${unclassified_total} historical unmarked evidence-link comment(s)."
  fi
  budgets="$(budget_rows)" || fail "could not measure the always-on budget"

  cat <<EOF
# ${ISSUE_TITLE}

Deterministic retro-loop snapshot for \`${REPOSITORY}\`. Confirmed occurrence
count is the candidate filing plus comments marked \`Occurrence:\` or
\`Occurrence evidence:\`. Unmarked GitHub Issue/PR links are surfaced for
confirmation instead of being silently ignored or falsely counted. Their
append-only historical count remains visible after a later marked comment
confirms the occurrence. Two confirmed occurrences of the same root-cause
class make promotion due; human review still decides the system change.

## Open retro candidates

${rows}

## Always-on instruction budget

| File | Lines | Target | Status |
|---|---:|---:|---|
${budgets}

## Next steps

Use \`.agents/skills/retro/SKILL.md\` to inspect occurrence evidence, promote
overdue candidates through a reviewed \`retro:\` PR, and trim or demote
always-on guidance that exceeds the target. This report does not promote or
close candidates automatically. Confirm an unmarked evidence-link comment by
adding a new marked occurrence comment that cites it; never edit the old one.
EOF
}

existing_review() {
  gh issue list -R "$REPOSITORY" --state all --limit 1000 \
    --json title,body,url \
    --jq ".[] | select(.title == \"${ISSUE_TITLE}\" or ((.body // \"\") | contains(\"${MARKER}\"))) | .url" \
    | sed -n '1p'
}

create_review_issue() {
  local existing body
  existing="$(existing_review)" || fail "could not perform the monthly Issue preflight"
  if [ -n "$existing" ]; then
    echo "Idempotent skip — monthly review already exists: $existing"
    return 0
  fi

  # Repeat the all-state exact-title/marker lookup immediately before the
  # mutation. Workflow-level repository concurrency serializes normal runs;
  # this second check also narrows races with manual invocations.
  existing="$(existing_review)" || fail "could not perform the final monthly Issue check"
  if [ -n "$existing" ]; then
    echo "Idempotent skip — monthly review already exists: $existing"
    return 0
  fi

  body="${REPORT}

${MARKER}"
  gh issue create -R "$REPOSITORY" --title "$ISSUE_TITLE" \
    --label needs:human --body "$body"
}

REPORT="$(build_report)" || fail "could not build the hygiene report"
printf '%s\n' "$REPORT"

if [ "$CREATE_ISSUE" -eq 1 ]; then
  create_review_issue
fi
