#!/usr/bin/env bash
# Run the platform-neutral shell regression suites ported from the source kit.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tests=(
  test-changelog-refs.sh
  test-connectors.sh
  test-escalation-wording.sh
  test-feedback-lib.sh
  test-feedback-receiver.sh
  test-scaffold-init.sh
  test-setup-labels.sh
  test-setup-project.sh
  test-setup-sources.sh
  test-workflow-permissions.sh
)

passed=0
for test_file in "${tests[@]}"; do
  echo "==> $test_file"
  bash "$HERE/$test_file"
  passed=$((passed + 1))
done

echo "portable-tests: OK — $passed suite(s) passed."
