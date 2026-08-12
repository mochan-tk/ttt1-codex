#!/usr/bin/env bash
# Static regression checks for the adopter-feedback form and receiver workflow.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
# shellcheck source=/dev/null
. "$HERE/lib.sh"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/feedbackreceiver.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

cat > "$WORK/check.rb" <<'RUBY'
# encoding: UTF-8
require "yaml"

root = ARGV.fetch(0)
form = YAML.safe_load(File.read(File.join(root, ".github/ISSUE_TEMPLATE/feedback.yml"), encoding: "UTF-8"), aliases: false)
raise "missing title marker" unless form.fetch("title").start_with?("[adopter-feedback] ")
raise "missing adopter label" unless form.fetch("labels").include?("from:adopter")
options = form.fetch("body").find { |item| item["type"] == "dropdown" }
  .fetch("attributes").fetch("options")
%w[scaffold-init setup-labels setup-project setup-ruleset setup-sources].each do |name|
  raise "missing script #{name}" unless options.include?(name)
end

workflow = File.read(File.join(root, ".github/workflows/adopter-feedback.yml"), encoding: "UTF-8")
raise "workflow must not check out" if workflow.include?("actions/checkout")
raise "workflow must not call external actions" if workflow.match?(/^\s*uses:/)
raise "workflow permission drift" unless workflow.match?(/^permissions:\n  issues: write$/)
raise "untrusted interpolation in run" if workflow.match?(/run:.*\$\{\{/)
raise "body marker not anchored" unless workflow.include?("'<!-- adopter-feedback:v1 -->'*)")
raise "title marker missing" unless workflow.include?("'[adopter-feedback]'*)")
raise "missing-label bootstrap missing" unless workflow.include?("repos/$REPO/labels/from%3Aadopter")
raise "label creation missing" unless workflow.include?("-f 'name=from:adopter'")

labels = File.read(File.join(root, ".github/scripts/setup-labels.sh"), encoding: "UTF-8")
raise "label bootstrap missing" unless labels.include?("ensure_label \"from:adopter\"")
puts "feedback receiver OK"
RUBY

expect_rc_grep 0 'feedback receiver OK' \
  "form, workflow, marker, permissions, and label stay synchronized" \
  ruby "$WORK/check.rb" "$REPO_ROOT"

# Execute the workflow's shell body against a recording gh shim. This catches
# GitHub API contract drift that static marker checks cannot see.
ruby - "$REPO_ROOT/.github/workflows/adopter-feedback.yml" > "$WORK/receiver.sh" <<'RUBY'
# encoding: UTF-8
require "yaml"
document = YAML.safe_load(File.read(ARGV.fetch(0), encoding: "UTF-8"), aliases: false)
puts document.fetch("jobs").fetch("classify").fetch("steps").first.fetch("run")
RUBY

CALLS="$WORK/gh-calls.log"
mkdir -p "$WORK/bin"
cat > "$WORK/bin/gh" <<'SHIM'
#!/usr/bin/env bash
set -u
printf '%s\n' "$*" >> "$GH_CALLS"
case "$*" in
  "api repos/acme/widget/labels/from%3Aadopter")
    [ "${LABEL_EXISTS:-0}" = "1" ] ;;
  "api -X POST repos/acme/widget/labels -f name=from:adopter -f color=D4C5F9 -f description=Consent-gated or manually filed adopter feedback")
    exit 0 ;;
  "api -X POST repos/acme/widget/issues/17/labels -f labels[]=from:adopter")
    exit 0 ;;
  *) echo "unsupported gh invocation: $*" >&2; exit 64 ;;
esac
SHIM
chmod +x "$WORK/bin/gh"

run_receiver() {
  local body="$1" title="$2" exists="${3:-0}"
  GH_CALLS="$CALLS" LABEL_EXISTS="$exists" PATH="$WORK/bin:$PATH" \
    ISSUE_BODY="$body" ISSUE_TITLE="$title" ISSUE_NUMBER=17 REPO=acme/widget \
    GH_TOKEN=fixture /bin/bash -e "$WORK/receiver.sh"
}

: > "$CALLS"
expect_rc_grep 0 'nothing to do' "an ordinary Issue causes no classification" \
  run_receiver 'ordinary body' 'ordinary title'
if [ ! -s "$CALLS" ]; then
  t_ok "an ordinary Issue makes no gh call"
else
  t_fail "an ordinary Issue makes no gh call"
fi

: > "$CALLS"
expect_rc_grep 0 'applied from:adopter' \
  "a helper marker bootstraps and attaches the missing label" \
  run_receiver '<!-- adopter-feedback:v1 --> body' 'failure report'
if grep -q '^api -X POST repos/acme/widget/labels -f name=from:adopter' "$CALLS" \
  && grep -q '^api -X POST repos/acme/widget/issues/17/labels ' "$CALLS"; then
  t_ok "missing-label path creates the repository label before attachment"
else
  t_fail "missing-label path creates the repository label before attachment"
  sed 's/^/    # /' "$CALLS"
fi

: > "$CALLS"
INJECTION="$WORK/untrusted-title-ran"
expect_rc_grep 0 'applied from:adopter' \
  "a title marker with shell text remains inert" \
  run_receiver 'ordinary body' "[adopter-feedback] \$(touch $INJECTION)" 1
if [ ! -e "$INJECTION" ] \
  && ! grep -q '^api -X POST repos/acme/widget/labels ' "$CALLS" \
  && grep -q '^api -X POST repos/acme/widget/issues/17/labels ' "$CALLS"; then
  t_ok "existing-label path skips creation and does not execute Issue text"
else
  t_fail "existing-label path skips creation and does not execute Issue text"
fi

t_summary
