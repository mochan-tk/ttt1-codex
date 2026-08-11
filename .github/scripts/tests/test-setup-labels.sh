#!/usr/bin/env bash
# Hermetic contract tests for preview-first label bootstrap.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/lib.sh"
SCRIPT="$HERE/../setup-labels.sh"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/labeltest.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
CALLS="$WORK/gh-calls.log"
mkdir -p "$WORK/bin"
cat > "$WORK/bin/gh" <<'SHIM'
#!/usr/bin/env bash
set -u
printf '%s\n' "$*" >> "$GH_CALLS"
case "$*" in
  "auth status --hostname github.com") [ "${AUTH_FAIL:-0}" != "1" ] ;;
  label\ create\ *) exit 0 ;;
  *) echo "unsupported gh invocation: $*" >&2; exit 64 ;;
esac
SHIM
chmod +x "$WORK/bin/gh"
PATH="$WORK/bin:$PATH"
export PATH GH_CALLS="$CALLS"

run_script() { /bin/bash "$SCRIPT" "$@" </dev/null; }
reset_calls() { : > "$CALLS"; }

expect_rc_grep 0 'Usage: setup-labels\.sh' "--help prints usage" \
  run_script --help
expect_rc_grep 2 'choose --dry-run.*--apply' \
  "missing mode is rejected before any GitHub call" run_script
expect_rc_grep 2 'choose exactly one' "conflicting modes are rejected" \
  run_script --dry-run --apply
expect_rc_grep 2 'repository must be owner/repo' "malformed repository is rejected" \
  run_script --repo invalid --dry-run

reset_calls
preview="$(run_script --repo acme/widget --dry-run)"
if [ "$(printf '%s\n' "$preview" | grep -c '^Would ensure label')" = "12" ] \
  && printf '%s\n' "$preview" | grep -q "label 'from:adopter'"; then
  t_ok "dry-run previews all 12 canonical labels"
else
  t_fail "dry-run previews all 12 canonical labels"
fi
if [ ! -s "$CALLS" ]; then
  t_ok "dry-run makes no gh calls"
else
  t_fail "dry-run makes no gh calls"
fi

reset_calls
expect_rc_grep 0 '12 labels ensured in github.com/acme/widget by explicit --apply' \
  "--apply completes with an authenticated gh shim" \
  run_script --repo acme/widget --apply
if [ "$(grep -c '^label create ' "$CALLS")" = "12" ] \
  && grep -q '^label create from:adopter --repo github.com/acme/widget .*--force$' "$CALLS"; then
  t_ok "--apply uses idempotent forced creation for the complete label set"
else
  t_fail "--apply uses idempotent forced creation for the complete label set"
  sed 's/^/    # /' "$CALLS"
fi

reset_calls
expect_rc_grep 0 '12 labels ensured' \
  "enterprise-default environment still writes only to github.com" \
  env GH_HOST=enterprise.example.com GH_CALLS="$CALLS" PATH="$PATH" \
    /bin/bash "$SCRIPT" --repo acme/widget --apply
if grep -q '^auth status --hostname github.com$' "$CALLS" \
  && [ "$(grep -c -- '--repo github.com/acme/widget' "$CALLS")" = "12" ] \
  && ! grep -q 'enterprise.example.com' "$CALLS"; then
  t_ok "every explicit-repository label write is host-qualified to github.com"
else
  t_fail "every explicit-repository label write is host-qualified to github.com"
fi

INFERRED_REPO="$WORK/inferred-repo"
git init -q "$INFERRED_REPO"
git -C "$INFERRED_REPO" remote add origin https://github.com/acme/inferred.git
reset_calls
preview="$(cd "$INFERRED_REPO" && GH_REPO=poison/wrong run_script --dry-run)"
if printf '%s\n' "$preview" \
    | grep -q 'Dry run complete for github.com/acme/inferred' \
   && [ ! -s "$CALLS" ]; then
  t_ok "default preview resolves and names the GitHub.com origin without gh"
else
  t_fail "default preview resolves and names the GitHub.com origin without gh"
fi

reset_calls
expect_rc_grep 0 '12 labels ensured in github.com/acme/inferred' \
  "GH_REPO cannot retarget a default-origin apply" \
  env GH_REPO=poison/wrong GH_CALLS="$CALLS" PATH="$PATH" \
    /bin/bash -c 'cd "$1" && exec /bin/bash "$2" --apply' \
    _ "$INFERRED_REPO" "$SCRIPT"
if [ "$(grep -c -- '--repo github.com/acme/inferred' "$CALLS")" = "12" ] \
   && ! grep -q 'poison/wrong' "$CALLS"; then
  t_ok "every inferred-repository write uses the reviewed origin"
else
  t_fail "every inferred-repository write uses the reviewed origin"
fi

reset_calls
expect_rc_grep 1 'gh is not authenticated' "--apply fails closed without auth" \
  env AUTH_FAIL=1 GH_CALLS="$CALLS" PATH="$PATH" /bin/bash "$SCRIPT" \
    --repo acme/widget --apply
if ! grep -q '^label create ' "$CALLS"; then
  t_ok "failed auth performs no label write"
else
  t_fail "failed auth performs no label write"
fi

t_summary
