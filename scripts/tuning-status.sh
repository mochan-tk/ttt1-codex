#!/usr/bin/env bash
# Report whether a copied scaffold has replaced its onboarding sentinel with
# measured project commands.
#
# Usage:
#   scripts/tuning-status.sh          Human report; 0 when tuned, 1 otherwise.
#   scripts/tuning-status.sh --quiet  No output; the same status code.
#   scripts/tuning-status.sh --ci     GitHub warning annotations; always 0.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="report"
case "${1:-}" in
  "") ;;
  --quiet) MODE="quiet" ;;
  --ci) MODE="ci" ;;
  -h|--help)
    sed -n '2,/^$/{s/^# \{0,1\}//p;}' "$0"
    exit 0
    ;;
  *)
    echo "tuning-status: unknown argument: $1" >&2
    exit 2
    ;;
esac

CANONICAL_REPOSITORY="mochan-tk/ttt1-codex"
TUNABLE_FILE=".github/workflows/ci.yml"
SENTINEL="CUSTOMIZE: replace this copied-template placeholder"

repository_slug() {
  local url
  if [ -n "${GITHUB_REPOSITORY:-}" ]; then
    printf '%s\n' "$GITHUB_REPOSITORY"
    return
  fi
  url="$(git remote get-url origin 2>/dev/null || true)"
  url="${url%.git}"
  case "$url" in
    https://github.com/*) printf '%s\n' "${url#https://github.com/}" ;;
    http://github.com/*) printf '%s\n' "${url#http://github.com/}" ;;
    git@github.com:*) printf '%s\n' "${url#git@github.com:}" ;;
    ssh://git@github.com/*) printf '%s\n' "${url#ssh://git@github.com/}" ;;
    *) printf '%s\n' "" ;;
  esac
}

REPOSITORY="$(repository_slug)"
FINDINGS=""
if [ "$REPOSITORY" != "$CANONICAL_REPOSITORY" ]; then
  if [ ! -f "$TUNABLE_FILE" ]; then
    FINDINGS="${TUNABLE_FILE}: missing tunable CI workflow"
  else
    FINDINGS="$(grep -nF "$SENTINEL" "$TUNABLE_FILE" || true)"
  fi
fi

if [ "$MODE" = "quiet" ]; then
  [ -z "$FINDINGS" ]
  exit
fi

if [ "$MODE" = "ci" ]; then
  if [ -n "$FINDINGS" ]; then
    while IFS=: read -r line _; do
      [ -n "$line" ] || continue
      printf '::warning file=%s,line=%s::Scaffold onboarding is incomplete. Run $project-onboarding and replace the CI placeholder with measured project commands.\n' \
        "$TUNABLE_FILE" "$line"
    done <<EOF
$FINDINGS
EOF
  fi
  exit 0
fi

if [ "$REPOSITORY" = "$CANONICAL_REPOSITORY" ]; then
  echo "TUNED: canonical scaffold source; the copied-template sentinel is intentionally retained."
  echo "Copies with a different GitHub origin must replace it through \$project-onboarding."
  exit 0
fi

if [ -z "$FINDINGS" ]; then
  echo "TUNED: no copied-template onboarding sentinel remains in the tunable CI workflow."
  exit 0
fi

echo "NOT TUNED: this copied scaffold still has an onboarding placeholder."
printf '  %s\n' "$FINDINGS"
cat <<'EOF'

Measured next steps:
  1. Invoke $project-onboarding and record the repository's real build, lint,
     test, and environment commands in the evidence pull request.
  2. Replace the CUSTOMIZE block in .github/workflows/ci.yml with those gates.
  3. Run the scaffold checks documented in README.md.
  4. Complete one license trial Task, review the disabled ruleset, and then
     create the first Epic from the mechanically calculated frontier.
EOF
exit 1
