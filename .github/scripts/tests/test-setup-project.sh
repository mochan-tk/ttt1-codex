#!/usr/bin/env bash
# Hermetic regression checks for explicit Projects preview and working views.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/lib.sh"
SCRIPT="$HERE/../setup-project.sh"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/projecttest.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
CALLS="$WORK/gh-calls.log"
VIEWS="$WORK/views.txt"
CREATED="$WORK/created.log"
mkdir -p "$WORK/bin"
cat > "$WORK/bin/gh" <<'SHIM'
#!/usr/bin/env bash
set -u
printf '%s\n' "$*" >> "$GH_CALLS"
[ "${GH_HOST:-}" = "github.com" ] \
  || { echo "gh host was not fixed to github.com" >&2; exit 66; }
case "${1:-} ${2:-}" in
  "auth status")
    [ "$*" = "auth status --hostname github.com" ] || exit 66
    [ "${AUTH_FAIL:-0}" != "1" ]; exit ;;
  "project list")
    printf '{"projects":[{"number":6,"title":"r roadmap","closed":false}]}\n' ;;
  "project view")
    printf '{"id":"PVT_test","url":"https://github.com/orgs/o/projects/6"}\n' ;;
  "project link") exit 0 ;;
  "project field-create")
    echo "unexpected field creation" >&2; exit 65 ;;
  "api graphql")
    args="$*"
    case "$args" in
      *"fields(first: 100)"*)
        cat <<'JSON'
{"data":{"node":{"fields":{"nodes":[
  {"__typename":"ProjectV2Field","id":"F_start","name":"Start date","dataType":"DATE"},
  {"__typename":"ProjectV2Field","id":"F_target","name":"Target date","dataType":"DATE"},
  {"__typename":"ProjectV2SingleSelectField","id":"F_kind","name":"Kind","options":[{"id":"O_epic","name":"Epic"},{"id":"O_task","name":"Task"}]}
]}}}}
JSON
        ;;
      *"views(first: 50)"*) cat "$VIEWS_FIXTURE" ;;
      *"createProjectV2View"*)
        [ "${CREATE_FAILS:-0}" = "1" ] && exit 1
        printf '%s\n' "$args" >> "$CREATED_LOG"
        printf '{"data":{"createProjectV2View":{"projectV2View":{"id":"PVTV_x"}}}}\n' ;;
      *) echo "unsupported GraphQL call" >&2; exit 64 ;;
    esac
    ;;
  *) echo "unsupported gh invocation: $*" >&2; exit 64 ;;
esac
SHIM
chmod +x "$WORK/bin/gh"
PATH="$WORK/bin:$PATH"
export PATH GH_CALLS="$CALLS"

run_script() { /bin/bash "$SCRIPT" "$@" </dev/null; }
run_init() {
  VIEWS_FIXTURE="$1" CREATED_LOG="$2" CREATE_FAILS="${3:-0}" \
    GH_CALLS="$CALLS" GH_HOST=enterprise.example.com PATH="$PATH" \
    /bin/bash "$SCRIPT" init \
    --owner o --repo o/r --apply </dev/null 2>&1
}

expect_rc_grep 0 'Usage:' "--help prints usage" run_script --help
expect_rc_grep 2 'choose --dry-run.*--apply' "init requires an explicit mode" \
  run_script init --owner o --repo o/r
expect_rc_grep 2 'choose --dry-run.*--apply' "dates requires an explicit mode" \
  run_script dates --project 6 --issue 7 --start 2026-08-12 \
    --target 2026-08-13 --owner o --repo o/r

: > "$CALLS"
expect_rc_grep 0 'Dry run complete; no GitHub calls were made' \
  "init dry-run is network-free" \
  run_script init --owner o --repo o/r --dry-run
if [ ! -s "$CALLS" ]; then
  t_ok "init dry-run invokes no gh command"
else
  t_fail "init dry-run invokes no gh command"
fi

: > "$CALLS"
expect_rc_grep 0 'Would set Start date' "dates dry-run is network-free" \
  run_script dates --project 6 --issue 7 --start 2026-08-12 \
    --target 2026-08-13 --owner o --repo o/r --dry-run
if [ ! -s "$CALLS" ]; then
  t_ok "dates dry-run invokes no gh command"
else
  t_fail "dates dry-run invokes no gh command"
fi

INFERRED_REPO="$WORK/inferred-repo"
git init -q "$INFERRED_REPO"
git -C "$INFERRED_REPO" remote add origin https://github.com/o/r.git
: > "$CALLS"
preview="$(cd "$INFERRED_REPO" && GH_REPO=poison/wrong \
  /bin/bash "$SCRIPT" init --dry-run)"
if printf '%s\n' "$preview" | grep -q 'Would link the project to o/r' \
   && [ ! -s "$CALLS" ]; then
  t_ok "default project preview resolves the GitHub.com origin without gh"
else
  t_fail "default project preview resolves the GitHub.com origin without gh"
fi

: > "$VIEWS"
: > "$CREATED"
: > "$CALLS"
out="$(cd "$INFERRED_REPO" && \
  VIEWS_FIXTURE="$VIEWS" CREATED_LOG="$CREATED" GH_CALLS="$CALLS" \
  GH_HOST=enterprise.example.com GH_REPO=poison/wrong PATH="$PATH" \
  /bin/bash "$SCRIPT" init --apply 2>&1)"
if printf '%s\n' "$out" | grep -q 'Linked project #6 to o/r' \
   && ! grep -q '^repo view ' "$CALLS" \
   && ! grep -q 'poison/wrong' "$CALLS"; then
  t_ok "GH_REPO cannot retarget default-origin Project apply"
else
  t_fail "GH_REPO cannot retarget default-origin Project apply"
  printf '%s\n' "$out" | sed 's/^/    # /'
fi

: > "$VIEWS"
: > "$CREATED"
: > "$CALLS"
out="$(run_init "$VIEWS" "$CREATED")"
missing=""
for view in Roadmap Kanban Backlog; do
  grep -q "$view" "$CREATED" || missing="$missing $view"
done
if [ -z "$missing" ]; then
  t_ok "init creates Roadmap, Kanban, and Backlog on a bare board"
else
  t_fail "init creates Roadmap, Kanban, and Backlog on a bare board (missing:$missing)"
  printf '%s\n' "$out" | sed 's/^/    # /'
fi
layouts_ok=1
grep -q 'Roadmap.*ROADMAP_LAYOUT\|ROADMAP_LAYOUT.*Roadmap' "$CREATED" || layouts_ok=0
grep -q 'Kanban.*BOARD_LAYOUT\|BOARD_LAYOUT.*Kanban' "$CREATED" || layouts_ok=0
grep -q 'Backlog.*TABLE_LAYOUT\|TABLE_LAYOUT.*Backlog' "$CREATED" || layouts_ok=0
if [ "$layouts_ok" = "1" ]; then
  t_ok "each working view uses its intended layout"
else
  t_fail "each working view uses its intended layout"
fi

printf 'Roadmap\nKanban\nBacklog\n' > "$VIEWS"
: > "$CREATED"
: > "$CALLS"
run_init "$VIEWS" "$CREATED" >/dev/null
if [ ! -s "$CREATED" ]; then
  t_ok "re-running an initialized board creates no duplicate views"
else
  t_fail "re-running an initialized board creates no duplicate views"
fi

printf 'Kanban\n' > "$VIEWS"
: > "$CREATED"
: > "$CALLS"
run_init "$VIEWS" "$CREATED" >/dev/null
if grep -q 'Roadmap' "$CREATED" && grep -q 'Backlog' "$CREATED" \
  && ! grep -q 'n=Kanban' "$CREATED"; then
  t_ok "a partial board gains only its missing views"
else
  t_fail "a partial board gains only its missing views"
fi

: > "$VIEWS"
: > "$CREATED"
: > "$CALLS"
out="$(run_init "$VIEWS" "$CREATED" 1)"
rc=$?
if [ "$rc" -eq 0 ] && printf '%s\n' "$out" | grep -q 'warning: could not create'; then
  t_ok "view API refusal warns without discarding the usable board"
else
  t_fail "view API refusal warns without discarding the usable board (rc=$rc)"
fi

: > "$CALLS"
expect_rc_grep 1 'gh is not authenticated' "live init fails closed without auth" \
  env AUTH_FAIL=1 GH_CALLS="$CALLS" PATH="$PATH" /bin/bash "$SCRIPT" init \
    --owner o --repo o/r --apply
if ! grep -q '^project ' "$CALLS"; then
  t_ok "failed auth performs no Project mutation"
else
  t_fail "failed auth performs no Project mutation"
fi

t_summary
