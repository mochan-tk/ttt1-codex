#!/usr/bin/env bash
# Report whether a copied scaffold has replaced its onboarding sentinels with
# measured project commands and eligible review ownership.
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
TUNABLE_FILES=(
  ".github/workflows/ci.yml"
  ".github/CODEOWNERS"
)
SENTINEL="CUSTOMIZE:"

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

append_finding() {
  if [ -n "$FINDINGS" ]; then
    FINDINGS="${FINDINGS}
$1"
  else
    FINDINGS="$1"
  fi
}

if [ "$REPOSITORY" != "$CANONICAL_REPOSITORY" ]; then
  for tunable_file in "${TUNABLE_FILES[@]}"; do
    if [ ! -f "$tunable_file" ]; then
      append_finding "${tunable_file}:1:missing required tunable target"
      continue
    fi
    while IFS= read -r finding; do
      [ -n "$finding" ] || continue
      append_finding "$finding"
    done < <(grep -nHF "$SENTINEL" "$tunable_file" || true)
  done
fi

if [ "$MODE" = "quiet" ]; then
  [ -z "$FINDINGS" ]
  exit
fi

if [ "$MODE" = "ci" ]; then
  if [ -n "$FINDINGS" ]; then
    while IFS=: read -r file line _; do
      [ -n "$file" ] || continue
      printf '::warning file=%s,line=%s::Scaffold onboarding is incomplete. Run $project-onboarding and replace or restore this copied-template target.\n' \
        "$file" "$line"
    done <<EOF
$FINDINGS
EOF
  fi
  exit 0
fi

if [ "$REPOSITORY" = "$CANONICAL_REPOSITORY" ]; then
  echo "TUNED: canonical scaffold source; copied-template sentinels are intentionally retained."
  echo "Copies with a different GitHub origin must replace them through \$project-onboarding."
  exit 0
fi

if [ -z "$FINDINGS" ]; then
  echo "TUNED: no copied-template onboarding sentinel remains in the tunable targets."
  exit 0
fi

echo "NOT TUNED: this copied scaffold has incomplete onboarding targets."
while IFS= read -r finding; do
  [ -n "$finding" ] || continue
  printf '  %s\n' "$finding"
done <<EOF
$FINDINGS
EOF
cat <<'EOF'

Measured next steps:
  1. Invoke $project-onboarding and complete the project's agreement merge
     before applying measured setup.
  2. Replace the CI CUSTOMIZE block with measured gates and replace every
     template CODEOWNER with an eligible owner or team.
  3. Run the scaffold checks documented in README.md.
  4. Review the disabled ruleset, complete one license trial Task with a
     non-author human review, and then create the first Epic.
EOF
exit 1
