#!/usr/bin/env bash
# Create or validate a source-bound, enforcement-disabled default-branch
# ruleset proposal. This helper cannot activate, update, or delete a ruleset.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: setup-ruleset.sh (--dry-run | --apply) --integration-id <positive-id> [options]

Create, or reuse by exact name, an enforcement-disabled default-branch
ruleset proposal requiring pull-request review and these exact source-bound
status contexts:
  - quality
  - scaffold-self-check
  - secure-devcontainer

Options:
  --dry-run                  Print exact request JSON without GitHub calls.
  --apply                    Confirm, then create or validate the proposal.
  --integration-id <id>     Positive GitHub App integration ID for all checks.
  -R, --repo <owner/repo>    GitHub.com repository. Default: origin remote.
  --name <name>              Proposal name. Default: adlc-default-branch.
  -h, --help                 Show this help and exit.

Live apply is deliberately fail-closed. It targets github.com, requires an
exact confirmation before the first GitHub call, creates only enforcement
"disabled", and never overwrites, activates, updates, or deletes a ruleset.
Any existing same-name ruleset must match the complete proposal exactly.
EOF
}

usage_error() {
  echo "error: $*" >&2
  echo "Run '$(basename "$0") --help' for usage." >&2
  exit 2
}

MODE=""
REPO=""
INTEGRATION_ID=""
NAME="adlc-default-branch"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run|--apply)
      [[ -z "$MODE" ]] || usage_error "choose exactly one of --dry-run or --apply"
      MODE="$1"
      shift
      ;;
    --integration-id)
      [[ -n "${2:-}" ]] || usage_error "--integration-id requires a value"
      INTEGRATION_ID="$2"
      shift 2
      ;;
    -R|--repo)
      [[ -n "${2:-}" ]] || usage_error "$1 requires an owner/repo argument"
      REPO="$2"
      shift 2
      ;;
    --name)
      [[ -n "${2:-}" ]] || usage_error "--name requires a value"
      NAME="$2"
      shift 2
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

[[ -n "$MODE" ]] || usage_error "choose exactly one of --dry-run or --apply"
[[ "$INTEGRATION_ID" =~ ^[1-9][0-9]*$ ]] || \
  usage_error "--integration-id must be a canonical positive integer"

repo_re='^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$'
if [[ -n "$REPO" && ! "$REPO" =~ $repo_re ]]; then
  usage_error "repository must be owner/repo, got: $REPO"
fi
name_re='^[A-Za-z0-9][A-Za-z0-9 ._:/-]{0,99}$'
[[ "$NAME" =~ $name_re ]] || \
  usage_error "ruleset name must be one safe line of at most 100 characters"

command -v jq >/dev/null 2>&1 || {
  echo "error: jq not found on PATH" >&2
  exit 1
}

# GitHub requires the full pull-request parameter set below and at least one
# allowed merge method. Every required status is bound to the same reviewed
# GitHub App integration; an any-source representation is never emitted.
PAYLOAD="$(jq -en \
  --arg name "$NAME" \
  --argjson integration_id "$INTEGRATION_ID" '
    {
      name: $name,
      target: "branch",
      enforcement: "disabled",
      bypass_actors: [],
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
            required_status_checks: [
              {context: "quality", integration_id: $integration_id},
              {context: "scaffold-self-check", integration_id: $integration_id},
              {context: "secure-devcontainer", integration_id: $integration_id}
            ]
          }
        }
      ]
    }
  ')"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "dry-run: source-bound disabled ruleset proposal; no GitHub calls made." >&2
  printf '%s\n' "$PAYLOAD"
  exit 0
fi

if [[ -z "$REPO" ]]; then
  command -v git >/dev/null 2>&1 || {
    echo "error: git not found on PATH" >&2
    exit 1
  }
  origin="$(git config --get remote.origin.url || true)"
  case "$origin" in
    https://github.com/*)
      REPO="${origin#https://github.com/}"
      ;;
    git@github.com:*)
      REPO="${origin#git@github.com:}"
      ;;
    ssh://git@github.com/*)
      REPO="${origin#ssh://git@github.com/}"
      ;;
    *)
      echo "error: origin must identify an exact github.com owner/repo" >&2
      echo "Pass --repo owner/repo explicitly after reviewing the target." >&2
      exit 1
      ;;
  esac
  REPO="${REPO%.git}"
fi
[[ "$REPO" =~ $repo_re ]] || usage_error "repository must be owner/repo, got: $REPO"

confirmation="apply disabled ruleset $NAME to github.com/$REPO with integration ID $INTEGRATION_ID"
echo "Live proposal target: github.com/$REPO" >&2
echo "Ruleset name: $NAME" >&2
echo "Required-check integration ID: $INTEGRATION_ID" >&2
echo "Type exactly: $confirmation" >&2
IFS= read -r answer || answer=""
[[ "$answer" == "$confirmation" ]] || {
  echo "Cancelled; no GitHub calls were made." >&2
  exit 1
}

command -v gh >/dev/null 2>&1 || {
  echo "error: gh CLI not found on PATH" >&2
  exit 1
}
GH_HOST=github.com gh auth status --hostname github.com >/dev/null

# A compatible object has exactly the proposal's trust-relevant fields. API
# metadata is ignored, but no additional rule, context, bypass, ref target, or
# stronger enforcement is accepted.
ruleset_is_compatible() {
  printf '%s' "$1" | jq -e \
    --arg name "$NAME" \
    --argjson integration_id "$INTEGRATION_ID" '
      def expected_checks:
        [
          {context: "quality", integration_id: $integration_id},
          {context: "scaffold-self-check", integration_id: $integration_id},
          {context: "secure-devcontainer", integration_id: $integration_id}
        ] | sort_by(.context);
      def exact_pr:
        {
          allowed_merge_methods: ["merge", "squash", "rebase"],
          dismiss_stale_reviews_on_push: true,
          require_code_owner_review: true,
          require_last_push_approval: true,
          required_approving_review_count: 1,
          required_review_thread_resolution: true
        };
      def normalized_pr_is_safe($parameters):
        ((($parameters | has("required_reviewers")) | not)
         or ($parameters.required_reviewers | type == "array" and length == 0))
        and ((($parameters | has("dismissal_restriction")) | not)
             or ($parameters.dismissal_restriction
                 == {enabled: false, allowed_actors: []}))
        and ((($parameters | has("ignore_approvals_from_contributors")) | not)
             or $parameters.ignore_approvals_from_contributors == false)
        and (($parameters
              | del(.required_reviewers,
                    .dismissal_restriction,
                    .ignore_approvals_from_contributors)) == exact_pr);
      def normalized_status_is_safe($parameters):
        ((($parameters | has("do_not_enforce_on_create")) | not)
         or $parameters.do_not_enforce_on_create == false)
        and (($parameters | del(.do_not_enforce_on_create)
              | keys | sort)
             == ["required_status_checks", "strict_required_status_checks_policy"]);
      ([.rules[]? | select(.type == "pull_request")]) as $pr_rules
      | ([.rules[]? | select(.type == "required_status_checks")]) as $status_rules
      | .name == $name
        and .target == "branch"
        and .enforcement == "disabled"
        and (.bypass_actors | type == "array" and length == 0)
        and .conditions == {ref_name: {include: ["~DEFAULT_BRANCH"], exclude: []}}
        and (.rules | type == "array" and length == 2)
        and ($pr_rules | length == 1)
        and ($status_rules | length == 1)
        and normalized_pr_is_safe($pr_rules[0].parameters)
        and ($status_rules[0].parameters.strict_required_status_checks_policy == true)
        and normalized_status_is_safe($status_rules[0].parameters)
        and (($status_rules[0].parameters.required_status_checks
              | sort_by(.context)) == expected_checks)
    ' >/dev/null
}

list_json="$(GH_HOST=github.com gh api --hostname github.com --paginate --slurp \
  "repos/$REPO/rulesets?targets=branch&includes_parents=false")"
matching_ids="$(printf '%s' "$list_json" | jq -r --arg name "$NAME" \
  '[.[][] | select(.name == $name) | .id] | .[]')"
matching_count="$(printf '%s\n' "$matching_ids" | sed '/^$/d' | wc -l | tr -d ' ')"

if [[ "$matching_count" -gt 1 ]]; then
  echo "error: multiple rulesets named '$NAME' exist; refusing an ambiguous target." >&2
  exit 1
fi

if [[ "$matching_count" == "1" ]]; then
  ruleset_id="$matching_ids"
  [[ "$ruleset_id" =~ ^[1-9][0-9]*$ ]] || {
    echo "error: existing ruleset has an invalid id" >&2
    exit 1
  }
  ruleset_json="$(GH_HOST=github.com gh api --hostname github.com \
    "repos/$REPO/rulesets/$ruleset_id")"
  if ! ruleset_is_compatible "$ruleset_json"; then
    echo "error: ruleset '$NAME' (id: $ruleset_id) is incompatible." >&2
    echo "No update was attempted; inspect and reconcile it manually." >&2
    echo "Inspect: GH_HOST=github.com gh api --hostname github.com repos/$REPO/rulesets/$ruleset_id" >&2
    exit 1
  fi
  echo "Reusing compatible disabled ruleset '$NAME' (id: $ruleset_id)."
  echo "No changes made; a human must review any future enforcement decision."
  exit 0
fi

response="$(printf '%s' "$PAYLOAD" | GH_HOST=github.com gh api \
  --hostname github.com --method POST "repos/$REPO/rulesets" --input -)"
ruleset_id="$(printf '%s' "$response" | jq -r '.id // empty')"
[[ "$ruleset_id" =~ ^[1-9][0-9]*$ ]] || {
  echo "error: create response did not contain a positive ruleset id" >&2
  exit 1
}
if ! ruleset_is_compatible "$response"; then
  echo "error: created ruleset response did not preserve the disabled proposal" >&2
  echo "Inspect ruleset id $ruleset_id manually; this helper will not modify it." >&2
  exit 1
fi

echo "Created disabled ruleset '$NAME' (id: $ruleset_id) on github.com/$REPO."
echo "Inspect: GH_HOST=github.com gh api --hostname github.com repos/$REPO/rulesets/$ruleset_id"
echo "A human must verify source identity and decide whether to enable enforcement."
