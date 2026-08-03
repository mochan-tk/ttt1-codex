#!/usr/bin/env bash
# Ensure the canonical ADLC label set. Live runs are idempotent because
# `gh label create --force` creates missing labels and refreshes existing ones.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: setup-labels.sh [options]

Ensure the 11 canonical ADLC labels.

Options:
  -R, --repo <owner/repo>  Target repository. Default: current repository.
  --dry-run                Print planned label changes; do not call GitHub.
  -h, --help               Show this help and exit.
EOF
}

usage_error() {
  echo "error: $*" >&2
  echo "Run '$(basename "$0") --help' for usage." >&2
  exit 2
}

REPO=""
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -R|--repo)
      [[ -n "${2:-}" ]] || usage_error "$1 requires an owner/repo argument"
      REPO="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage_error "unknown argument: $1"
      ;;
  esac
done

repo_re='^[^/[:space:]]+/[^/[:space:]]+$'
if [[ -n "$REPO" && ! "$REPO" =~ $repo_re ]]; then
  usage_error "repository must be owner/repo, got: $REPO"
fi

if [[ "$DRY_RUN" != "true" ]]; then
  command -v gh >/dev/null 2>&1 || {
    echo "error: gh CLI not found on PATH" >&2
    exit 1
  }
fi

ensure_label() {
  local name="$1" color="$2" description="$3"
  if [[ "$DRY_RUN" == "true" ]]; then
    printf "Would ensure label '%s' (color %s): %s\n" \
      "$name" "$color" "$description"
  elif [[ -n "$REPO" ]]; then
    gh label create "$name" --repo "$REPO" --color "$color" \
      --description "$description" --force
  else
    gh label create "$name" --color "$color" \
      --description "$description" --force
  fi
}

ensure_label "type:epic" "5319E7" "Outline item; parent of Task sub-issues"
ensure_label "type:task" "0E8A16" "Self-contained work order for one Codex session"
ensure_label "ai:ready" "1D76DB" "Brief is complete and dispatchable when unblocked"
ensure_label "needs:human" "B60205" "Human judgment or trust decision required"
ensure_label "needs:replan" "D93F0B" "Plan or scope must change before work continues"
ensure_label "risk:high" "D93F0B" "Plan comment requires human approval before implementation"
ensure_label "exec:cloud" "C2E0C6" "Route: Codex cloud task; asynchronous and parallel"
ensure_label "exec:app" "BFDADC" "Route: Codex app task; steerable and worktree-isolated"
ensure_label "exec:cli" "FEF2C0" "Route: Codex CLI; terminal-first local or scripted work"
ensure_label "exec:ide" "F9D0C4" "Route: Codex IDE; human-close ambiguous or environment-bound work"
ensure_label "retro:candidate" "EDEDED" "Observed scaffold friction; promote on repeated occurrence"

if [[ "$DRY_RUN" == "true" ]]; then
  if [[ -n "$REPO" ]]; then
    echo "Dry run complete for $REPO; no GitHub calls were made."
  else
    echo "Dry run complete for the current repository; no GitHub calls were made."
  fi
else
  echo "Done. 11 labels ensured."
fi
