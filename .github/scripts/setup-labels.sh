#!/usr/bin/env bash
# Ensure the canonical ADLC label set. Live runs require --apply and are idempotent because
# `gh label create --force` creates missing labels and refreshes existing ones.

set -euo pipefail

# Unexpected interactive failures may offer a privacy-minimized upstream
# report. CI, non-interactive use, missing metadata, or no explicit consent is
# always silent; deleting feedback-lib.sh disables the offer.
if [[ -n "${BASH_SOURCE[0]:-}" && -r "$(dirname "${BASH_SOURCE[0]}")/feedback-lib.sh" ]]; then
  # shellcheck source=/dev/null
  if . "$(dirname "${BASH_SOURCE[0]}")/feedback-lib.sh" 2>/dev/null; then
    feedback_arm setup-labels || true
  fi
fi

usage() {
  cat <<'EOF'
Usage: setup-labels.sh [options]

Ensure the 12 canonical ADLC labels.

Options:
  -R, --repo <owner/repo>  Target repository. Default: current repository.
  --dry-run                Print planned label changes; do not call GitHub.
  --apply                  Explicitly authorize live GitHub changes.
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
MODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -R|--repo)
      [[ -n "${2:-}" ]] || usage_error "$1 requires an owner/repo argument"
      REPO="$2"
      shift 2
      ;;
    --dry-run)
      [[ -z "$MODE" || "$MODE" == "dry-run" ]] || usage_error "choose exactly one of --dry-run or --apply"
      MODE="dry-run"
      DRY_RUN="true"
      shift
      ;;
    --apply)
      [[ -z "$MODE" || "$MODE" == "apply" ]] || usage_error "choose exactly one of --dry-run or --apply"
      MODE="apply"
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

[[ -n "$MODE" ]] || usage_error "choose --dry-run (no GitHub writes) or --apply (live GitHub changes)"

repo_re='^[^/[:space:]]+/[^/[:space:]]+$'
if [[ -z "$REPO" ]]; then
  remote="$(git remote get-url origin 2>/dev/null || true)"
  case "$remote" in
    https://github.com/*) REPO="${remote#https://github.com/}" ;;
    ssh://git@github.com/*) REPO="${remote#ssh://git@github.com/}" ;;
    git@github.com:*) REPO="${remote#git@github.com:}" ;;
    *) usage_error "could not infer a GitHub.com origin; pass -R owner/repo" ;;
  esac
  REPO="${REPO%.git}"
fi
if [[ ! "$REPO" =~ $repo_re ]]; then
  usage_error "repository must be owner/repo, got: $REPO"
fi

if [[ "$DRY_RUN" != "true" ]]; then
  command -v gh >/dev/null 2>&1 || {
    echo "error: gh CLI not found on PATH" >&2
    exit 1
  }
  gh auth status --hostname github.com >/dev/null 2>&1 || {
    echo "error: gh is not authenticated; run 'gh auth login --hostname github.com'" >&2
    exit 1
  }
fi

ensure_label() {
  local name="$1" color="$2" description="$3"
  if [[ "$DRY_RUN" == "true" ]]; then
    printf "Would ensure label '%s' (color %s): %s\n" \
      "$name" "$color" "$description"
  else
    gh label create "$name" --repo "github.com/$REPO" --color "$color" \
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
ensure_label "from:adopter" "D4C5F9" "Consent-gated or manually filed adopter feedback"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry run complete for github.com/$REPO; no GitHub calls were made."
else
  echo "Done. 12 labels ensured in github.com/$REPO by explicit --apply."
fi
