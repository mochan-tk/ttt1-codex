#!/usr/bin/env bash
# Propose the default-branch review wall as an enforcement-disabled ruleset.
# This script has no option that can activate enforcement; a human reviews and
# enables the proposal separately after license evidence is accepted.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: setup-ruleset.sh [options]

Create, or reuse by exact name, an enforcement-disabled default-branch
ruleset requiring:
  - pull requests with at least one approval;
  - approval of the latest push by someone other than its pusher;
  - code-owner review for owned paths; and
  - deterministic required status checks.

Options:
  -R, --repo <owner/repo>  Target repository. Default: current repository.
  --checks <c1,c2,...>     Required check contexts.
                           Default: quality,scaffold-self-check.
  --name <name>            Ruleset name. Default: adlc-default-branch.
  --dry-run                Print request JSON; make no GitHub calls.
  -h, --help               Show this help and exit.

The script always submits enforcement "disabled" and never activates a
ruleset. Repository rulesets require Administration write permission; feature
availability can depend on repository visibility, account tier, and policy.
Before enabling it, confirm an eligible non-author human can approve and that
owned-path changes have a code owner other than the PR author; authors cannot
approve their own PRs.
EOF
}

usage_error() {
  echo "error: $*" >&2
  echo "Run '$(basename "$0") --help' for usage." >&2
  exit 2
}

REPO=""
CHECKS="quality,scaffold-self-check"
NAME="adlc-default-branch"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -R|--repo)
      [[ -n "${2:-}" ]] || usage_error "$1 requires an owner/repo argument"
      REPO="$2"
      shift 2
      ;;
    --checks)
      [[ -n "${2:-}" ]] || usage_error "--checks requires a comma-separated list"
      CHECKS="$2"
      shift 2
      ;;
    --name)
      [[ -n "${2:-}" ]] || usage_error "--name requires a value"
      NAME="$2"
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
command -v jq >/dev/null 2>&1 || {
  echo "error: jq not found on PATH" >&2
  exit 1
}

# GitHub's current ruleset API requires all pull-request booleans below and at
# least one allowed merge method. GitHub does not let PR authors approve their
# own PRs; require_last_push_approval also protects the latest reviewable push.
# shellcheck disable=SC2016
PAYLOAD="$(jq -en \
  --arg name "$NAME" \
  --arg checks "$CHECKS" \
  '($checks | split(",")
            | map(gsub("^\\s+|\\s+$"; ""))
            | map(select(length > 0))) as $contexts
   | if ($contexts | length) == 0 then error("at least one check is required")
     else {
       name: $name,
       target: "branch",
       enforcement: "disabled",
       conditions: {
         ref_name: {include: ["~DEFAULT_BRANCH"], exclude: []}
       },
       rules: [
         {
           type: "pull_request",
           parameters: {
             allowed_merge_methods: ["merge", "squash", "rebase"],
             dismiss_stale_reviews_on_push: true,
             require_code_owner_review: true,
             require_last_push_approval: true,
             required_approving_review_count: 1,
             required_review_thread_resolution: true
           }
         },
         {
           type: "required_status_checks",
           parameters: {
             strict_required_status_checks_policy: true,
             required_status_checks: ($contexts | map({context: .}))
           }
         }
       ]
     } end')"

# Accept a same-name ruleset only when it already enforces every invariant this
# script owns. Stronger additional check contexts are allowed. Enforcement is
# deliberately excluded because a human may have reviewed and activated it.
# shellcheck disable=SC2016
ruleset_is_compatible() {
  printf '%s' "$1" \
    | jq -e --arg name "$NAME" --arg checks "$CHECKS" '
        ($checks | split(",")
                 | map(gsub("^\\s+|\\s+$"; ""))
                 | map(select(length > 0))
                 | unique) as $expected_checks
        | ([.rules[]? | select(.type == "pull_request") | .parameters]
           | first // {}) as $pull_request
        | ([.rules[]? | select(.type == "required_status_checks")
                         | .parameters]
           | first // {}) as $status_checks
        | ([$status_checks.required_status_checks[]?.context]
           | unique) as $actual_checks
        | .name == $name
          and .target == "branch"
          and .conditions.ref_name.include == ["~DEFAULT_BRANCH"]
          and .conditions.ref_name.exclude == []
          and (($pull_request.required_approving_review_count // 0) >= 1)
          and $pull_request.require_code_owner_review == true
          and $pull_request.require_last_push_approval == true
          and $status_checks.strict_required_status_checks_policy == true
          and (($expected_checks - $actual_checks) | length == 0)
      ' >/dev/null
}

if [[ "$DRY_RUN" == "true" ]]; then
  if [[ -n "$REPO" ]]; then
    echo "dry-run: disabled ruleset proposal for $REPO; no GitHub calls made." >&2
  else
    echo "dry-run: disabled ruleset proposal; no GitHub calls made." >&2
  fi
  printf '%s\n' "$PAYLOAD"
  exit 0
fi

command -v gh >/dev/null 2>&1 || {
  echo "error: gh CLI not found on PATH" >&2
  exit 1
}
if [[ -z "$REPO" ]]; then
  REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
fi
[[ "$REPO" =~ $repo_re ]] || \
  usage_error "repository must be owner/repo, got: $REPO"

# Reuse an exact-name repository branch ruleset. Never overwrite a ruleset a
# human may already have reviewed or activated.
existing="$(gh api --paginate \
  "repos/$REPO/rulesets?targets=branch&includes_parents=false" \
  | jq -r --arg name "$NAME" \
      '.[] | select(.name == $name)
       | [.id, .enforcement] | @tsv' \
  | sed -n '1p')"
if [[ -n "$existing" ]]; then
  ruleset_id="${existing%%$'\t'*}"
  ruleset_json="$(gh api "repos/$REPO/rulesets/$ruleset_id")"
  if ! ruleset_is_compatible "$ruleset_json"; then
    echo "error: ruleset '$NAME' (id: $ruleset_id) is incompatible." >&2
    echo "The script will not overwrite it; inspect and reconcile it manually." >&2
    echo "Inspect: gh api repos/$REPO/rulesets/$ruleset_id" >&2
    exit 1
  fi
  enforcement="$(printf '%s' "$ruleset_json" | jq -r '.enforcement')"
  echo "Reusing ruleset '$NAME' (id: $ruleset_id, enforcement: $enforcement)."
  echo "Required default-branch, review, code-owner, and check rules match."
  echo "No changes made; inspect it before any human enforcement decision."
  exit 0
fi

response="$(printf '%s' "$PAYLOAD" \
  | gh api --method POST "repos/$REPO/rulesets" --input -)"
ruleset_id="$(printf '%s' "$response" | jq -r '.id')"
echo "Created disabled ruleset '$NAME' (id: $ruleset_id) on $REPO."
echo "Inspect: gh api repos/$REPO/rulesets/$ruleset_id"
echo "Human action after accepted license evidence: review it in Settings,"
echo "then decide whether to enable enforcement."
