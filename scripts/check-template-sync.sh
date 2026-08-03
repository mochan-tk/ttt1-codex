#!/usr/bin/env bash
# Verify that GitHub Issue forms and gh CLI body templates expose the same
# canonical Epic and Task work-order contracts.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v python3 >/dev/null 2>&1 || {
  echo "check-template-sync: ERROR — python3 is required" >&2
  exit 2
}
command -v ruby >/dev/null 2>&1 || {
  echo "check-template-sync: ERROR — ruby is required for YAML validation" >&2
  exit 2
}

ruby - "$ROOT" <<'RUBY'
# encoding: UTF-8
require "psych"
require "yaml"

def find_duplicate_keys(node, relative, errors)
  case node
  when Psych::Nodes::Mapping
    seen = {}
    node.children.each_slice(2) do |key, value|
      name = key.respond_to?(:value) ? key.value : "<complex key>"
      errors << "#{relative}: duplicate YAML key #{name.inspect}" if seen[name]
      seen[name] = true
      find_duplicate_keys(value, relative, errors)
    end
  when Psych::Nodes::Sequence, Psych::Nodes::Document, Psych::Nodes::Stream
    node.children.each { |child| find_duplicate_keys(child, relative, errors) }
  end
end

root = ARGV.fetch(0)
schemas = {
  ".github/ISSUE_TEMPLATE/task.yml" => {
    labels: [
      "Origin", "Objective", "Context & references", "Acceptance criteria",
      "Out of scope", "File ownership", "Verification", "Risk gate",
      "Routing — Surface", "Routing — Suggested role",
      "Routing — Model/reasoning tier", "Routing — Parallel-safe", "Handoff notes"
    ],
    optional: ["Handoff notes"]
  },
  ".github/ISSUE_TEMPLATE/epic.yml" => {
    labels: [
      "Origin", "Outcome", "Context & references", "Success criteria",
      "Scope & non-goals", "Phase outline", "Tracking graph", "Verification"
    ],
    optional: ["Tracking graph"]
  }
}
errors = []

schemas.each do |relative, schema|
  path = File.join(root, relative)
  begin
    source = File.read(path)
    tree = Psych.parse_stream(source)
    find_duplicate_keys(tree, relative, errors)
    document = YAML.safe_load(source, aliases: false)
  rescue StandardError => error
    errors << "#{relative}: invalid YAML: #{error.message.lines.first.strip}"
    next
  end
  unless document.is_a?(Hash) && document["body"].is_a?(Array)
    errors << "#{relative}: root must be a mapping with a body sequence"
    next
  end

  fields = document["body"].select { |entry| entry.is_a?(Hash) && entry["type"] != "markdown" }
  labels = fields.map { |field| field.dig("attributes", "label") }
  ids = fields.map { |field| field["id"] }
  errors << "#{relative}: every field needs a string id" unless ids.all? { |id| id.is_a?(String) && !id.empty? }
  errors << "#{relative}: field ids must be unique" unless ids.uniq.length == ids.length
  errors << "#{relative}: parsed labels differ from the canonical schema" unless labels == schema[:labels]

  required = fields.each_with_object([]) do |field, values|
    values << field.dig("attributes", "label") if field.dig("validations", "required") == true
  end
  expected_required = schema[:labels] - schema[:optional]
  unless required.sort == expected_required.sort
    errors << "#{relative}: required fields must be exactly #{expected_required.join(', ')}"
  end
end

unless errors.empty?
  warn "check-template-sync: FAIL — YAML/form validation failed"
  errors.each { |error| warn "  #{error}" }
  exit 1
end
RUBY

python3 - "$ROOT" <<'PY'
from __future__ import annotations

import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])


def form_labels(path: pathlib.Path) -> list[str]:
    labels: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s+label:\s*(.+?)\s*$", line)
        if match:
            labels.append(match.group(1).strip('"\''))
    return labels


def body_headings(path: pathlib.Path) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"^##\s+(.+?)\s*$", path.read_text(encoding="utf-8"), re.MULTILINE)
    ]


def ensure_unique(values: list[str], path: pathlib.Path) -> list[str]:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    return [f"{path}: duplicate section {value!r}" for value in duplicates]


task_form = root / ".github/ISSUE_TEMPLATE/task.yml"
task_body = root / ".agents/skills/plan-management/templates/task-body.md"
epic_form = root / ".github/ISSUE_TEMPLATE/epic.yml"
epic_body = root / ".agents/skills/plan-management/templates/epic-body.md"
paths = (task_form, task_body, epic_form, epic_body)

missing = [str(path.relative_to(root)) for path in paths if not path.is_file()]
if missing:
    print("check-template-sync: FAIL — missing canonical file(s):", file=sys.stderr)
    for path in missing:
        print(f"  {path}", file=sys.stderr)
    raise SystemExit(1)

expected_task_form = {
    "Origin",
    "Objective",
    "Context & references",
    "Acceptance criteria",
    "Out of scope",
    "File ownership",
    "Verification",
    "Risk gate",
    "Routing — Surface",
    "Routing — Suggested role",
    "Routing — Model/reasoning tier",
    "Routing — Parallel-safe",
    "Handoff notes",
}
expected_task_body = expected_task_form - {"Origin"}

expected_epic_form = {
    "Origin",
    "Outcome",
    "Context & references",
    "Success criteria",
    "Scope & non-goals",
    "Phase outline",
    "Tracking graph",
    "Verification",
}
expected_epic_body = {
    "Outcome",
    "Success criteria",
    "Scope & non-goals",
    "Phase outline",
    "References",
    "Tracking",
}

observed = {
    task_form: form_labels(task_form),
    task_body: body_headings(task_body),
    epic_form: form_labels(epic_form),
    epic_body: body_headings(epic_body),
}
expected = {
    task_form: expected_task_form,
    task_body: expected_task_body,
    epic_form: expected_epic_form,
    epic_body: expected_epic_body,
}

errors: list[str] = []
for path, values in observed.items():
    errors.extend(ensure_unique(values, path.relative_to(root)))
    actual = set(values)
    wanted = expected[path]
    for value in sorted(wanted - actual):
        errors.append(f"{path.relative_to(root)}: missing canonical section {value!r}")
    for value in sorted(actual - wanted):
        errors.append(f"{path.relative_to(root)}: unexpected section {value!r}")

task_body_text = task_body.read_text(encoding="utf-8")
epic_body_text = epic_body.read_text(encoding="utf-8")
if not re.search(r"^- Origin:\s*#", task_body_text, re.MULTILINE):
    errors.append(f"{task_body.relative_to(root)}: Context must contain an Origin #N field")
if not re.search(r"^- Origin:\s*#", epic_body_text, re.MULTILINE):
    errors.append(f"{epic_body.relative_to(root)}: Tracking must contain an Origin #N field")

# The form and CLI template use deliberately different presentation labels in
# two Epic fields. Assert those mappings explicitly so later drift is visible.
epic_aliases = {
    "Context & references": "References",
    "Tracking graph": "Tracking",
}
for form_name, body_name in epic_aliases.items():
    if form_name not in observed[epic_form] or body_name not in observed[epic_body]:
        errors.append(f"Epic mapping drift: {form_name!r} must map to {body_name!r}")

# Epic verification is a required form-only field because the CLI template is
# used during graph creation, before an executor receives a runnable Task.
if "Verification" not in observed[epic_form]:
    errors.append("Epic form must retain its required Verification field")

if errors:
    print(f"check-template-sync: FAIL — {len(errors)} contract mismatch(es)", file=sys.stderr)
    for error in errors:
        print(f"  {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    "check-template-sync: OK — Task and Epic form/template contracts match "
    "their canonical sections and provenance fields."
)
PY
