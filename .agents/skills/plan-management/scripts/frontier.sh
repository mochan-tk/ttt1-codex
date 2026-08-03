#!/usr/bin/env bash
# Print the actionable ADLC frontier from GitHub.
#
# Frontier = open AND type:task AND ai:ready AND every blocked-by issue CLOSED.
#
# Usage:
#   frontier.sh [--repo owner/repo] [--all]
#
# --all also prints ready Tasks that still have open or unknown blockers.

set -euo pipefail

repo_args=()
show_all=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -R|--repo)
      [[ $# -ge 2 ]] || { echo "error: $1 requires owner/repo" >&2; exit 2; }
      repo_args=(--repo "$2")
      shift 2
      ;;
    --all)
      show_all=true
      shift
      ;;
    -h|--help)
      grep '^# ' "$0" | sed 's/^# //'
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

command -v gh >/dev/null 2>&1 || {
  echo "error: gh CLI is required" >&2
  exit 1
}

candidates=$(gh issue list \
  ${repo_args[@]+"${repo_args[@]}"} \
  --state open \
  --label "type:task" \
  --label "ai:ready" \
  --limit 200 \
  --json number,title \
  --template '{{range .}}{{.number}}{{"\t"}}{{.title}}{{"\n"}}{{end}}')

if [[ -z "$candidates" ]]; then
  echo "No open type:task issues labeled ai:ready."
  exit 0
fi

blocked_report=""
lookup_failed=false

echo "== Actionable frontier =="
while IFS=$'\t' read -r number title; do
  [[ -n "$number" ]] || continue

  blocker_rows=""
  if ! blocker_rows=$(gh issue view "$number" \
    ${repo_args[@]+"${repo_args[@]}"} \
    --json blockedBy \
    --template '{{range .blockedBy.nodes}}{{.state}}{{"\t"}}{{.url}}{{"\n"}}{{end}}'); then
    blocked_report+=$(printf '#%s\t%s\t(dependency lookup failed)\n' "$number" "$title")
    blocked_report+=$'\n'
    lookup_failed=true
    continue
  fi

  open_blockers=""
  while IFS=$'\t' read -r state url; do
    [[ -n "$state" ]] || continue
    if [[ "$state" != "CLOSED" ]]; then
      open_blockers+="${open_blockers:+, }${url:-unknown blocker}"
    fi
  done <<< "$blocker_rows"

  if [[ -z "$open_blockers" ]]; then
    printf '#%s\t%s\n' "$number" "$title"
  else
    blocked_report+=$(printf '#%s\t%s\t(waiting on: %s)\n' \
      "$number" "$title" "$open_blockers")
    blocked_report+=$'\n'
  fi
done <<< "$candidates"

if $show_all && [[ -n "$blocked_report" ]]; then
  echo
  echo "== Ready but blocked =="
  printf '%s' "$blocked_report"
fi

if $lookup_failed; then
  echo "error: at least one dependency lookup failed; uncertain Tasks were excluded" >&2
  exit 1
fi
