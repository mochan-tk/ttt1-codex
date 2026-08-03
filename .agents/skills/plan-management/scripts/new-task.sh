#!/usr/bin/env bash
# Preview or create one Task Issue with its ADLC tracking edges.
#
# Usage:
#   new-task.sh --dry-run --title "Task: outcome" --body task-body.md \
#     --parent 12 --origin 12 --exec app [--blocked-by 10,11] \
#     [--repo owner/repo] [--ready]
#   new-task.sh --apply --title "Task: outcome" --body task-body.md \
#     --parent 12 --origin 12 --exec app [--blocked-by 10,11] \
#     [--repo owner/repo] [--ready]
#
# Modes (choose exactly one):
#   --dry-run  Validate and transform the body locally, print the intended
#              action, and exit without invoking gh or contacting GitHub.
#   --apply    Explicitly authorize GitHub preflight and live Issue creation.
#
# With neither mode, the helper refuses before any gh command. The body must
# contain "- Origin: #<origin-issue>" or the matching filled "- Origin: #N"
# line. The completion PR must later contain "Closes #N".

set -euo pipefail

mode=""
title=""
body=""
parent=""
origin=""
exec_surface=""
blocked_by=""
repo=""
ready=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      if [[ -n "$mode" && "$mode" != "dry-run" ]]; then
        echo "error: choose exactly one of --dry-run or --apply" >&2
        exit 2
      fi
      mode="dry-run"
      shift
      ;;
    --apply)
      if [[ -n "$mode" && "$mode" != "apply" ]]; then
        echo "error: choose exactly one of --dry-run or --apply" >&2
        exit 2
      fi
      mode="apply"
      shift
      ;;
    -t|--title)
      [[ $# -ge 2 ]] || { echo "error: $1 requires a value" >&2; exit 2; }
      title="$2"
      shift 2
      ;;
    -b|--body)
      [[ $# -ge 2 ]] || { echo "error: $1 requires a file" >&2; exit 2; }
      body="$2"
      shift 2
      ;;
    -p|--parent)
      [[ $# -ge 2 ]] || { echo "error: $1 requires an Epic number" >&2; exit 2; }
      parent="$2"
      shift 2
      ;;
    -o|--origin)
      [[ $# -ge 2 ]] || { echo "error: $1 requires an Issue number" >&2; exit 2; }
      origin="$2"
      shift 2
      ;;
    -e|--exec)
      [[ $# -ge 2 ]] || { echo "error: $1 requires a surface" >&2; exit 2; }
      exec_surface="$2"
      shift 2
      ;;
    -d|--blocked-by)
      [[ $# -ge 2 ]] || { echo "error: $1 requires comma-separated Issues" >&2; exit 2; }
      blocked_by="$2"
      shift 2
      ;;
    -R|--repo)
      [[ $# -ge 2 ]] || { echo "error: $1 requires owner/repo" >&2; exit 2; }
      repo="$2"
      shift 2
      ;;
    --ready)
      ready=true
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

# Safety gate: make live intent explicit before validation runs any command
# outside the local filesystem.
[[ -n "$mode" ]] || {
  echo "error: choose --dry-run (no GitHub access) or --apply (live GitHub creation); no gh command was run" >&2
  exit 2
}

[[ -n "$title" && -n "$body" && -n "$parent" && -n "$origin" && -n "$exec_surface" ]] || {
  echo "error: --title, --body, --parent, --origin, and --exec are required" >&2
  exit 2
}
[[ -f "$body" ]] || { echo "error: body file not found: $body" >&2; exit 2; }
[[ "$parent" =~ ^[0-9]+$ ]] || { echo "error: --parent must be an Issue number" >&2; exit 2; }
[[ "$origin" =~ ^[0-9]+$ ]] || { echo "error: --origin must be an Issue number" >&2; exit 2; }
if [[ -n "$blocked_by" && ! "$blocked_by" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
  echo "error: --blocked-by must be comma-separated Issue numbers" >&2
  exit 2
fi
if [[ -n "$repo" && ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  echo "error: --repo must use owner/repo format" >&2
  exit 2
fi
case "$exec_surface" in
  cloud|app|cli|ide) ;;
  *) echo "error: --exec must be cloud, app, cli, or ide" >&2; exit 2 ;;
esac

task_body=$(mktemp "${TMPDIR:-/tmp}/adlc-task-body.XXXXXX")
cleanup() {
  [[ -n "${task_body:-}" && -f "$task_body" ]] && rm -f -- "$task_body"
}
trap cleanup EXIT

if grep -Fq -- '- Origin: #<origin-issue>' "$body"; then
  sed "s|- Origin: #<origin-issue>|- Origin: #${origin}|" "$body" > "$task_body"
elif grep -Eq "^- Origin: #${origin}[[:space:]]*$" "$body"; then
  cp "$body" "$task_body"
else
  echo "error: body must contain '- Origin: #<origin-issue>' or '- Origin: #${origin}'" >&2
  exit 2
fi

labels="type:task,exec:${exec_surface}"
if $ready; then
  labels+=",ai:ready"
fi

if [[ "$mode" == "dry-run" ]]; then
  echo "Mode: dry-run (no gh invocation; no GitHub access)"
  echo "Intended action: create one Task Issue"
  printf 'Repository: %s\n' "${repo:-current repository}"
  printf 'Title: %s\n' "$title"
  printf 'Labels: %s\n' "$labels"
  printf 'Sub-issue parent: Epic #%s\n' "$parent"
  printf 'Blocked by: %s\n' "${blocked_by:-none}"
  printf 'Origin reference: #%s\n' "$origin"
  echo 'Completion PR body: Closes #<new-task-number>'
  echo "--- Transformed body ---"
  sed -n '1,$p' "$task_body"
  echo "--- End transformed body ---"
  exit 0
fi

[[ "$mode" == "apply" ]] || {
  echo "error: internal mode error" >&2
  exit 2
}

# LIVE GITHUB BOUNDARY: every gh lookup and mutation is below this line and is
# reachable only after the caller explicitly supplies --apply.
command -v gh >/dev/null 2>&1 || {
  echo "error: gh CLI is required for --apply" >&2
  exit 1
}

repo_args=()
if [[ -n "$repo" ]]; then
  repo_args=(--repo "$repo")
fi

# gh creates the Issue before it attaches some relationships. Fail early for
# invalid references, labels, or an older CLI so a predictable input error does
# not leave an unwired Task behind.
create_help=$(gh issue create --help)
grep -Fq -- '--parent' <<< "$create_help" || {
  echo "error: this gh version does not support sub-issue --parent" >&2
  exit 1
}
if [[ -n "$blocked_by" ]]; then
  grep -Fq -- '--blocked-by' <<< "$create_help" || {
    echo "error: this gh version does not support dependency --blocked-by" >&2
    exit 1
  }
fi

parent_labels=$(gh issue view "$parent" \
  ${repo_args[@]+"${repo_args[@]}"} \
  --json labels \
  --template '{{range .labels}}{{.name}}{{"\n"}}{{end}}') || {
    echo "error: parent Epic #${parent} is not readable" >&2
    exit 1
  }
grep -Fxq 'type:epic' <<< "$parent_labels" || {
  echo "error: parent #${parent} is not labeled type:epic" >&2
  exit 1
}

preflight_issue() {
  local number="$1" role="$2"
  gh issue view "$number" \
    ${repo_args[@]+"${repo_args[@]}"} \
    --json number \
    --template '{{.number}}' >/dev/null || {
      echo "error: ${role} Issue #${number} is not readable" >&2
      exit 1
    }
}

preflight_issue "$origin" "origin"
remaining_blockers="$blocked_by"
while [[ -n "$remaining_blockers" ]]; do
  if [[ "$remaining_blockers" == *,* ]]; then
    blocker="${remaining_blockers%%,*}"
    remaining_blockers="${remaining_blockers#*,}"
  else
    blocker="$remaining_blockers"
    remaining_blockers=""
  fi
  preflight_issue "$blocker" "blocker"
done

available_labels=$(gh label list \
  ${repo_args[@]+"${repo_args[@]}"} \
  --limit 200 \
  --json name \
  --template '{{range .}}{{.name}}{{"\n"}}{{end}}')
for required_label in "type:task" "exec:${exec_surface}"; do
  grep -Fxq "$required_label" <<< "$available_labels" || {
    echo "error: required label does not exist: ${required_label}" >&2
    exit 1
  }
done
if $ready; then
  grep -Fxq 'ai:ready' <<< "$available_labels" || {
    echo "error: required label does not exist: ai:ready" >&2
    exit 1
  }
fi

create_args=(
  --title "$title"
  --body-file "$task_body"
  --label "type:task"
  --label "exec:${exec_surface}"
  --parent "$parent"
)
if [[ -n "$blocked_by" ]]; then
  create_args+=(--blocked-by "$blocked_by")
fi
if $ready; then
  create_args+=(--label "ai:ready")
fi

url=$(gh issue create \
  ${repo_args[@]+"${repo_args[@]}"} \
  "${create_args[@]}")
number="${url##*/}"
[[ "$number" =~ ^[0-9]+$ ]] || {
  echo "error: could not derive created Issue number from: $url" >&2
  exit 1
}

printf 'Created Task #%s under Epic #%s: %s\n' "$number" "$parent" "$url"
printf 'Origin edge: #%s -> #%s\n' "$origin" "$number"
if [[ -n "$blocked_by" ]]; then
  printf 'Dependency edge: #%s blocked by %s\n' "$number" "$blocked_by"
fi
printf 'Completion PR body must contain: Closes #%s\n' "$number"
