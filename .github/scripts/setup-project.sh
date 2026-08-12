#!/usr/bin/env bash
# Create or reuse a repository-linked Projects v2 roadmap and schedule Issues.
# Projects are user/org-owned; the repository link makes the roadmap visible
# from the repository while the Issue graph remains planning truth.

set -euo pipefail

if [[ -n "${BASH_SOURCE[0]:-}" && -r "$(dirname "${BASH_SOURCE[0]}")/feedback-lib.sh" ]]; then
  # shellcheck source=/dev/null
  if . "$(dirname "${BASH_SOURCE[0]}")/feedback-lib.sh" 2>/dev/null; then
    feedback_arm setup-project || true
  fi
fi

usage() {
  cat <<'EOF'
Usage:
  setup-project.sh init [options]
  setup-project.sh dates --project <number> --issue <number> \
    --start <YYYY-MM-DD> --target <YYYY-MM-DD> [options]
  setup-project.sh --help

Commands:
  init    Create or reuse "<repo> roadmap", ensure Start date, Target date,
          and Kind (Epic, Task) fields, then link it to the repository.
  dates   Add or reuse an Issue item, set its dates, and derive Kind from its
          type:epic or type:task label.

Options:
  --owner <login>          Project owner. Default: repository owner.
  --title <title>          init only. Default: "<repo> roadmap".
  --project <number>       dates only. Project number printed by init.
  --issue <number>         dates only. Issue number to schedule.
  --start <YYYY-MM-DD>     dates only. Start date.
  --target <YYYY-MM-DD>    dates only. Target date, not before Start date.
  -R, --repo <owner/repo>  Target repository. Default: current repository.
  --dry-run                Print planned actions without calling GitHub.
  --apply                  Explicitly authorize live GitHub changes.
  -h, --help               Show this help and exit.

Projects v2 requires an authenticated gh CLI with the project scope and an
account allowed to create/link Projects. Organization policy or account tier
may limit those operations. The helper creates Roadmap, Kanban, and Backlog
views by exact name where the API permits it; selecting date fields and grouping
the Roadmap by Kind remain manual UI steps.
EOF
}

fail() {
  echo "error: $*" >&2
  exit 1
}

usage_error() {
  echo "error: $*" >&2
  echo "Run '$(basename "$0") --help' for usage." >&2
  exit 2
}

require_tools() {
  command -v gh >/dev/null 2>&1 || fail "gh CLI not found on PATH"
  command -v jq >/dev/null 2>&1 || fail "jq not found on PATH"
  # owner/repo and Project owner arguments do not carry a hostname. Fix the
  # live process to the github.com support boundary so GH_HOST cannot retarget
  # an approved preview to a same-named resource on another host.
  export GH_HOST=github.com
  gh auth status --hostname github.com >/dev/null 2>&1 \
    || fail "gh is not authenticated; run 'gh auth login --hostname github.com'"
}

REPO=""
REPO_NAME=""
REPO_OWNER=""
DRY_RUN="false"
MODE=""

select_mode() {
  local requested="$1"
  if [[ -n "$MODE" && "$MODE" != "$requested" ]]; then
    usage_error "choose exactly one of --dry-run or --apply"
  fi
  MODE="$requested"
  if [[ "$requested" == "dry-run" ]]; then
    DRY_RUN="true"
  fi
}

require_mode() {
  [[ -n "$MODE" ]] || usage_error \
    "choose --dry-run (no GitHub writes) or --apply (live GitHub changes)"
}

infer_repo_from_git() {
  local remote=""
  command -v git >/dev/null 2>&1 || return 1
  remote="$(git remote get-url origin 2>/dev/null || true)"
  case "$remote" in
    https://github.com/*)
      REPO="${remote#https://github.com/}"
      ;;
    ssh://git@github.com/*)
      REPO="${remote#ssh://git@github.com/}"
      ;;
    git@github.com:*)
      REPO="${remote#git@github.com:}"
      ;;
    *)
      return 1
      ;;
  esac
  REPO="${REPO%.git}"
}

resolve_repo() {
  if [[ -z "$REPO" ]]; then
    infer_repo_from_git || usage_error \
      "could not infer a GitHub.com origin; pass -R owner/repo"
  fi
  local repo_re='^[^/[:space:]]+/[^/[:space:]]+$'
  [[ "$REPO" =~ $repo_re ]] || \
    usage_error "repository must be owner/repo, got: $REPO"
  REPO_NAME="${REPO##*/}"
  REPO_OWNER="${REPO%%/*}"
}

# `gh project field-list` does not expose DATE versus TEXT. Query the GraphQL
# field union so an existing same-name field cannot be silently reused with an
# incompatible data type.
# shellcheck disable=SC2016
project_fields_json() {
  gh api graphql \
    -f query='query($id: ID!) {
      node(id: $id) {
        ... on ProjectV2 {
          fields(first: 100) {
            nodes {
              __typename
              ... on ProjectV2Field { id name dataType }
              ... on ProjectV2SingleSelectField {
                id
                name
                options { id name }
              }
              ... on ProjectV2IterationField { id name }
            }
          }
        }
      }
    }' \
    -F id="$1" \
    | jq -ce '.data.node.fields.nodes'
}

# The JSON argument to these helpers is the array returned above.
# shellcheck disable=SC2016
field_count() {
  printf '%s' "$1" \
    | jq -r --arg name "$2" '[.[] | select(.name == $name)] | length'
}

# shellcheck disable=SC2016
field_id() {
  printf '%s' "$1" \
    | jq -r --arg name "$2" \
        '[.[] | select(.name == $name) | .id] | first // empty'
}

# shellcheck disable=SC2016
field_data_type() {
  printf '%s' "$1" \
    | jq -r --arg name "$2" \
        '[.[] | select(.name == $name) | .dataType] | first // empty'
}

# shellcheck disable=SC2016
field_node_type() {
  printf '%s' "$1" \
    | jq -r --arg name "$2" \
        '[.[] | select(.name == $name) | .__typename] | first // empty'
}

# shellcheck disable=SC2016
option_count() {
  printf '%s' "$1" \
    | jq -r --arg name "$2" --arg option "$3" \
        '[.[] | select(.name == $name) | .options[]?
          | select(.name == $option)] | length'
}

# shellcheck disable=SC2016
option_id() {
  printf '%s' "$1" \
    | jq -r --arg name "$2" --arg option "$3" \
        '[.[] | select(.name == $name) | .options[]?
          | select(.name == $option) | .id] | first // empty'
}

require_roadmap_fields() {
  local fields_json="$1" project="$2" field_name="" count=""
  local data_type="" node_type="" option=""
  for field_name in "Start date" "Target date"; do
    count="$(field_count "$fields_json" "$field_name")"
    [[ "$count" == "1" ]] || \
      fail "project #$project must have exactly one '$field_name' field"
    data_type="$(field_data_type "$fields_json" "$field_name")"
    [[ "$data_type" == "DATE" ]] || \
      fail "field '$field_name' on project #$project must have DATE type"
  done

  count="$(field_count "$fields_json" "Kind")"
  [[ "$count" == "1" ]] || \
    fail "project #$project must have exactly one 'Kind' field"
  node_type="$(field_node_type "$fields_json" "Kind")"
  [[ "$node_type" == "ProjectV2SingleSelectField" ]] || \
    fail "field 'Kind' on project #$project must have SINGLE_SELECT type"
  for option in "Epic" "Task"; do
    count="$(option_count "$fields_json" "Kind" "$option")"
    [[ "$count" == "1" ]] || \
      fail "field 'Kind' on project #$project must have one '$option' option"
  done
}

cmd_init() {
  local owner="" title=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --owner)
        [[ -n "${2:-}" ]] || usage_error "--owner requires a login"
        owner="$2"
        shift 2
        ;;
      --title)
        [[ -n "${2:-}" ]] || usage_error "--title requires a value"
        title="$2"
        shift 2
        ;;
      -R|--repo)
        [[ -n "${2:-}" ]] || usage_error "$1 requires an owner/repo argument"
        REPO="$2"
        shift 2
        ;;
      --dry-run)
        select_mode "dry-run"
        shift
        ;;
      --apply)
        select_mode "apply"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        usage_error "unknown argument for init: $1"
        ;;
    esac
  done

  require_mode

  if [[ "$DRY_RUN" != "true" ]]; then
    require_tools
  fi
  resolve_repo
  [[ -n "$owner" ]] || owner="$REPO_OWNER"
  [[ -n "$title" ]] || title="$REPO_NAME roadmap"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "Would create or reuse project '$title' owned by $owner."
    echo "Would ensure DATE fields 'Start date' and 'Target date'."
    echo "Would ensure SINGLE_SELECT field 'Kind' with options Epic and Task."
    echo "Would ensure Roadmap, Kanban, and Backlog views by exact name."
    echo "Would link the project to $REPO."
    echo "Dry run complete; no GitHub calls were made."
    return 0
  fi

  local number=""
  # shellcheck disable=SC2016
  number="$(gh project list --owner "$owner" --limit 100 --format json \
    | jq -r --arg title "$title" \
        '[.projects[] | select(.title == $title) | .number] | first // empty')"

  if [[ -n "$number" ]]; then
    echo "Reusing project #$number ('$title') owned by $owner."
  else
    local closed_number=""
    # shellcheck disable=SC2016
    closed_number="$(gh project list --owner "$owner" --closed --limit 100 \
      --format json | jq -r --arg title "$title" \
        '[.projects[] | select(.title == $title and .closed == true) | .number] | first // empty')"
    if [[ "$closed_number" =~ ^[1-9][0-9]*$ ]]; then
      fail "project '$title' owned by '$owner' exists but is closed (#$closed_number); reopen it explicitly before rerunning init"
    fi
    number="$(gh project create --owner "$owner" --title "$title" \
      --format json --jq '.number')"
    if ! [[ "$number" =~ ^[1-9][0-9]*$ ]]; then
      # shellcheck disable=SC2016
      number="$(gh project list --owner "$owner" --limit 100 --format json \
        | jq -r --arg title "$title" \
            '[.projects[] | select(.title == $title) | .number] | first // empty')"
    fi
    echo "Created project #$number ('$title') owned by $owner."
  fi

  [[ "$number" =~ ^[1-9][0-9]*$ ]] || \
    fail "could not determine the number of project '$title' owned by '$owner'"

  local project_json="" project_id="" url="" fields_json=""
  local field_name="" count="" data_type="" node_type="" option=""
  project_json="$(gh project view "$number" --owner "$owner" --format json)"
  project_id="$(printf '%s' "$project_json" | jq -r '.id')"
  url="$(printf '%s' "$project_json" | jq -r '.url')"
  fields_json="$(project_fields_json "$project_id")"

  # Preflight every same-name field before creating anything. A conflicting
  # field is never deleted or rewritten automatically.
  for field_name in "Start date" "Target date"; do
    count="$(field_count "$fields_json" "$field_name")"
    [[ "$count" -le 1 ]] || \
      fail "project #$number has multiple '$field_name' fields"
    if [[ "$count" == "1" ]]; then
      data_type="$(field_data_type "$fields_json" "$field_name")"
      [[ "$data_type" == "DATE" ]] || \
        fail "existing field '$field_name' must have DATE type"
    fi
  done
  count="$(field_count "$fields_json" "Kind")"
  [[ "$count" -le 1 ]] || fail "project #$number has multiple 'Kind' fields"
  if [[ "$count" == "1" ]]; then
    node_type="$(field_node_type "$fields_json" "Kind")"
    [[ "$node_type" == "ProjectV2SingleSelectField" ]] || \
      fail "existing field 'Kind' must have SINGLE_SELECT type"
    for option in "Epic" "Task"; do
      count="$(option_count "$fields_json" "Kind" "$option")"
      [[ "$count" == "1" ]] || \
        fail "existing field 'Kind' must have one '$option' option"
    done
  fi

  for field_name in "Start date" "Target date"; do
    if [[ "$(field_count "$fields_json" "$field_name")" == "0" ]]; then
      gh project field-create "$number" --owner "$owner" \
        --name "$field_name" --data-type DATE >/dev/null
      echo "Created DATE field '$field_name'."
    else
      echo "Field '$field_name' already exists with DATE type; skipping."
    fi
  done

  if [[ "$(field_count "$fields_json" "Kind")" == "0" ]]; then
    gh project field-create "$number" --owner "$owner" --name "Kind" \
      --data-type SINGLE_SELECT --single-select-options "Epic,Task" >/dev/null
    echo "Created SINGLE_SELECT field 'Kind' (Epic, Task)."
  else
    echo "Field 'Kind' already has SINGLE_SELECT options Epic and Task; skipping."
  fi

  local existing_views="" view_spec="" view_name="" view_layout=""
  # shellcheck disable=SC2016
  existing_views="$(gh api graphql -f query='
    query($id: ID!) {
      node(id: $id) { ... on ProjectV2 { views(first: 50) { nodes { name } } } }
    }' -f id="$project_id" --jq '.data.node.views.nodes[].name' 2>/dev/null || true)"
  for view_spec in "Roadmap:ROADMAP_LAYOUT" "Kanban:BOARD_LAYOUT" "Backlog:TABLE_LAYOUT"; do
    view_name="${view_spec%%:*}"
    view_layout="${view_spec##*:}"
    if printf '%s\n' "$existing_views" | grep -Fxq "$view_name"; then
      echo "View '$view_name' already exists; skipping."
      continue
    fi
    # shellcheck disable=SC2016
    if gh api graphql -f query='
      mutation($p: ID!, $n: String!, $l: ProjectV2ViewLayout!) {
        createProjectV2View(input: {projectId: $p, name: $n, layout: $l}) {
          projectV2View { id }
        }
      }' -f p="$project_id" -f n="$view_name" -f l="$view_layout" >/dev/null 2>&1; then
      echo "Created '$view_name' view ($view_layout)."
    else
      echo "warning: could not create '$view_name'; add it in the Project UI."
    fi
  done

  gh project link "$number" --owner "$owner" --repo "$REPO"
  echo "Linked project #$number to $REPO."

  echo "Project number: $number"
  echo "Project URL:    $url"
  echo "Manual step: configure the Roadmap view to use Start date and Target"
  echo "date, then group it by Kind. The Issue graph remains planning authority."
}

cmd_dates() {
  local owner="" project="" issue="" start="" target=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --owner)
        [[ -n "${2:-}" ]] || usage_error "--owner requires a login"
        owner="$2"
        shift 2
        ;;
      --project)
        [[ -n "${2:-}" ]] || usage_error "--project requires a number"
        project="$2"
        shift 2
        ;;
      --issue)
        [[ -n "${2:-}" ]] || usage_error "--issue requires a number"
        issue="$2"
        shift 2
        ;;
      --start)
        [[ -n "${2:-}" ]] || usage_error "--start requires YYYY-MM-DD"
        start="$2"
        shift 2
        ;;
      --target)
        [[ -n "${2:-}" ]] || usage_error "--target requires YYYY-MM-DD"
        target="$2"
        shift 2
        ;;
      -R|--repo)
        [[ -n "${2:-}" ]] || usage_error "$1 requires an owner/repo argument"
        REPO="$2"
        shift 2
        ;;
      --dry-run)
        select_mode "dry-run"
        shift
        ;;
      --apply)
        select_mode "apply"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        usage_error "unknown argument for dates: $1"
        ;;
    esac
  done


  require_mode

  [[ -n "$project" && -n "$issue" && -n "$start" && -n "$target" ]] || \
    usage_error "dates requires --project, --issue, --start, and --target"

  local number_re='^[0-9]+$' date_re='^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
  [[ "$project" =~ $number_re ]] || \
    usage_error "--project must be a number, got: $project"
  [[ "$issue" =~ $number_re ]] || \
    usage_error "--issue must be a number, got: $issue"
  [[ "$start" =~ $date_re ]] || \
    usage_error "--start must be YYYY-MM-DD, got: $start"
  [[ "$target" =~ $date_re ]] || \
    usage_error "--target must be YYYY-MM-DD, got: $target"
  if [[ "$target" < "$start" ]]; then
    usage_error "--target ($target) is earlier than --start ($start)"
  fi

  if [[ "$DRY_RUN" != "true" ]]; then
    require_tools
  fi
  resolve_repo
  [[ -n "$owner" ]] || owner="$REPO_OWNER"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "Would add or reuse $REPO issue #$issue in project #$project owned by $owner."
    echo "Would set Start date = $start and Target date = $target."
    echo "Would set Kind from type:epic or type:task when present."
    echo "Dry run complete; no GitHub calls were made."
    return 0
  fi

  local issue_json="" issue_url="" issue_labels="" project_json=""
  local project_id="" fields_json="" start_field_id=""
  local target_field_id="" item_id=""
  issue_json="$(gh issue view "$issue" --repo "$REPO" --json url,labels)"
  issue_url="$(printf '%s' "$issue_json" | jq -r '.url')"
  issue_labels="$(printf '%s' "$issue_json" | jq -r '.labels[].name')"
  project_json="$(gh project view "$project" --owner "$owner" --format json)"
  project_id="$(printf '%s' "$project_json" | jq -r '.id')"
  fields_json="$(project_fields_json "$project_id")"
  require_roadmap_fields "$fields_json" "$project"
  start_field_id="$(field_id "$fields_json" "Start date")"
  target_field_id="$(field_id "$fields_json" "Target date")"

  item_id="$(gh project item-add "$project" --owner "$owner" \
    --url "$issue_url" --format json --jq '.id')"
  gh project item-edit --id "$item_id" --project-id "$project_id" \
    --field-id "$start_field_id" --date "$start" >/dev/null
  gh project item-edit --id "$item_id" --project-id "$project_id" \
    --field-id "$target_field_id" --date "$target" >/dev/null
  echo "Scheduled $REPO issue #$issue: $start through $target."

  local kind="" kind_field_id="" kind_option_id=""
  if printf '%s\n' "$issue_labels" | grep -Fxq "type:epic"; then
    kind="Epic"
  elif printf '%s\n' "$issue_labels" | grep -Fxq "type:task"; then
    kind="Task"
  fi
  if [[ -z "$kind" ]]; then
    echo "Note: no type:epic or type:task label; Kind remains unset."
    return 0
  fi

  kind_field_id="$(field_id "$fields_json" "Kind")"
  kind_option_id="$(option_id "$fields_json" "Kind" "$kind")"
  gh project item-edit --id "$item_id" --project-id "$project_id" \
    --field-id "$kind_field_id" \
    --single-select-option-id "$kind_option_id" >/dev/null
  echo "Set Kind = $kind for issue #$issue."
}

case "${1:-}" in
  init)
    shift
    cmd_init "$@"
    ;;
  dates)
    shift
    cmd_dates "$@"
    ;;
  -h|--help)
    usage
    ;;
  "")
    usage_error "missing command (init or dates)"
    ;;
  *)
    usage_error "unknown command: $1"
    ;;
esac
