#!/usr/bin/env bash
# Regression tests for the Codex escalation-wording authority guard.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
# shellcheck source=/dev/null
. "$HERE/lib.sh"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/escalationtest.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
CASE_N=0

new_case() {
  CASE_N=$((CASE_N + 1))
  CASE="$WORK/case$CASE_N"
  init_sandbox_repo "$CASE"
  mkdir -p "$CASE/.github/scripts" "$CASE/.agents/skills/session-orchestration" "$CASE/.codex/agents"
  cp "$REPO_ROOT/.github/scripts/check-escalation-wording.sh" "$CASE/.github/scripts/"
}

new_case
echo 'Escalate according to the normative session skill.' > "$CASE/.codex/agents/extra.toml"
stage_all "$CASE"
expect_rc 0 "custom agent without a count passes" \
  bash "$CASE/.github/scripts/check-escalation-wording.sh"

new_case
echo 'After two failures, escalate to the user.' > "$CASE/.codex/agents/extra.toml"
stage_all "$CASE"
expect_rc_grep 1 'outside the normative' "custom agent count duplication fails" \
  bash "$CASE/.github/scripts/check-escalation-wording.sh"

new_case
echo 'After three same-signature failures, escalate.' > \
  "$CASE/.agents/skills/session-orchestration/SKILL.md"
stage_all "$CASE"
expect_rc 0 "normative session skill may state the budget" \
  bash "$CASE/.github/scripts/check-escalation-wording.sh"

t_summary
