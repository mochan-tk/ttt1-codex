#!/usr/bin/env bash
# Validate the Codex-native skill surface and repository-wide scaffold rules.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v python3 >/dev/null 2>&1 || {
  echo "check-skills: ERROR — python3 is required" >&2
  exit 2
}
command -v ruby >/dev/null 2>&1 || {
  echo "check-skills: ERROR — ruby is required for YAML validation" >&2
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
skills = %w[
  project-onboarding context-collection context-distillation plan-management
  task-routing session-orchestration verification retro
]
expected_interface = %w[display_name short_description default_prompt]
errors = []

skills.each do |name|
  skill_relative = ".agents/skills/#{name}/SKILL.md"
  skill_path = File.join(root, skill_relative)
  if File.file?(skill_path)
    lines = File.readlines(skill_path)
    closing = (1...lines.length).find { |index| lines[index].strip == "---" }
    if lines.empty? || lines.first.strip != "---" || closing.nil?
      errors << "#{skill_relative}: frontmatter delimiters are invalid"
    else
      frontmatter = lines[1...closing].join
      begin
        tree = Psych.parse_stream(frontmatter)
        find_duplicate_keys(tree, skill_relative, errors)
        document = YAML.safe_load(frontmatter, aliases: false)
        unless document.is_a?(Hash) && document.keys.sort == %w[description name]
          errors << "#{skill_relative}: frontmatter keys must be exactly name, description"
        end
        if document.is_a?(Hash)
          errors << "#{skill_relative}: name must equal #{name.inspect}" unless document["name"] == name
          unless document["description"].is_a?(String) && !document["description"].empty?
            errors << "#{skill_relative}: description must be a non-empty string"
          end
        end
      rescue StandardError => error
        errors << "#{skill_relative}: invalid frontmatter YAML: #{error.message.lines.first.strip}"
      end
    end
  else
    errors << "#{skill_relative}: missing"
  end

  relative = ".agents/skills/#{name}/agents/openai.yaml"
  path = File.join(root, relative)
  unless File.file?(path)
    errors << "#{relative}: missing"
    next
  end
  source = File.read(path)
  begin
    tree = Psych.parse_stream(source)
    find_duplicate_keys(tree, relative, errors)
    document = YAML.safe_load(source, aliases: false)
  rescue StandardError => error
    errors << "#{relative}: invalid YAML: #{error.message.lines.first.strip}"
    next
  end
  unless document.is_a?(Hash) && document.keys == ["interface"]
    errors << "#{relative}: root must contain only the interface mapping"
    next
  end
  interface = document["interface"]
  unless interface.is_a?(Hash) && interface.keys.sort == expected_interface.sort
    errors << "#{relative}: interface keys must be exactly #{expected_interface.join(', ')}"
    next
  end
  interface.each do |key, value|
    errors << "#{relative}: #{key} must be a non-empty string" unless value.is_a?(String) && !value.empty?
  end
  token = "$" + name
  unless interface["default_prompt"].is_a?(String) && interface["default_prompt"].include?(token)
    errors << "#{relative}: default_prompt must invoke #{token}"
  end
end

unless errors.empty?
  warn "check-skills: FAIL — YAML metadata validation failed"
  errors.each { |error| warn "  #{error}" }
  exit 1
end
RUBY

python3 - "$ROOT" <<'PY'
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import unicodedata

root = pathlib.Path(sys.argv[1]).resolve()
skills_root = root / ".agents/skills"
expected_skills = {
    "project-onboarding",
    "context-collection",
    "context-distillation",
    "plan-management",
    "task-routing",
    "session-orchestration",
    "verification",
    "retro",
}
errors: list[str] = []

if not skills_root.is_dir():
    print("check-skills: FAIL — .agents/skills is missing", file=sys.stderr)
    raise SystemExit(1)

actual_skills = {path.name for path in skills_root.iterdir() if path.is_dir()}
for name in sorted(expected_skills - actual_skills):
    errors.append(f"missing skill directory: .agents/skills/{name}")
for name in sorted(actual_skills - expected_skills):
    errors.append(f"unexpected skill directory: .agents/skills/{name}")


def frontmatter(text: str, path: pathlib.Path) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        errors.append(f"{path}: frontmatter must start on line 1")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"{path}: frontmatter closing delimiter is missing")
        return {}
    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([a-z_]+):\s*(.+)$", line)
        if not match:
            errors.append(f"{path}: invalid frontmatter line: {line!r}")
            continue
        values[match.group(1)] = match.group(2).strip().strip('"\'')
    return values


for name in sorted(expected_skills & actual_skills):
    directory = skills_root / name
    skill_path = directory / "SKILL.md"
    metadata_path = directory / "agents/openai.yaml"
    if not skill_path.is_file():
        errors.append(f"{skill_path.relative_to(root)}: missing")
        continue
    if not metadata_path.is_file():
        errors.append(f"{metadata_path.relative_to(root)}: missing")
        continue

    skill_text = skill_path.read_text(encoding="utf-8")
    values = frontmatter(skill_text, skill_path.relative_to(root))
    if values.get("name") != name:
        errors.append(f"{skill_path.relative_to(root)}: name must equal {name!r}")
    description = values.get("description", "")
    if len(description) < 40 or "Use " not in description:
        errors.append(
            f"{skill_path.relative_to(root)}: description must state behavior and a precise 'Use ...' trigger"
        )
    if len(skill_text.splitlines()) > 500:
        errors.append(f"{skill_path.relative_to(root)}: exceeds the 500-line progressive-disclosure ceiling")

    metadata = metadata_path.read_text(encoding="utf-8")
    required_keys = ("display_name:", "short_description:", "default_prompt:")
    for key in required_keys:
        if not re.search(rf"^\s*{re.escape(key)}", metadata, re.MULTILINE):
            errors.append(f"{metadata_path.relative_to(root)}: missing {key[:-1]}")
    if f"${name}" not in metadata:
        errors.append(f"{metadata_path.relative_to(root)}: default_prompt must invoke ${name}")
    short_match = re.search(r'^\s*short_description:\s*["\']?(.+?)["\']?\s*$', metadata, re.MULTILINE)
    if short_match:
        short_description = short_match.group(1).rstrip('"\'')
        if not 25 <= len(short_description) <= 64:
            errors.append(f"{metadata_path.relative_to(root)}: short_description must be 25-64 characters")
    if re.search(r"^\s*(?:model|model_reasoning_effort):", metadata, re.MULTILINE):
        errors.append(f"{metadata_path.relative_to(root)}: project metadata must not pin a model")

forbidden = [
    root / "CLAUDE.md",
    root / ".github/copilot-instructions.md",
    root / ".github/agents",
    root / ".github/instructions",
    root / ".github/prompts",
    root / ".github/skills",
    root / ".github/workflows/copilot-setup-steps.yml",
]
for path in forbidden:
    if path.exists():
        errors.append(f"forbidden compatibility path exists: {path.relative_to(root)}")

for path in root.rglob("*"):
    if ".git" in path.parts or not path.is_file():
        continue
    if path.name.endswith((".prompt.md", ".agent.md")):
        errors.append(f"deprecated agent-facing file exists: {path.relative_to(root)}")

agents_path = root / "AGENTS.md"
if not agents_path.is_file():
    errors.append("AGENTS.md is missing")
elif len(agents_path.read_text(encoding="utf-8").splitlines()) > 200:
    errors.append("AGENTS.md exceeds its 200-line constitution ceiling")

# Persistent template content may use Unicode punctuation and the deliberate
# phase symbols α/β, but alphabetic prose must be Latin-script English.
allowed_non_latin_letters = {"α", "β"}
tracked = subprocess.run(
    ["git", "ls-files", "-z"], check=True, stdout=subprocess.PIPE
).stdout.decode("utf-8").split("\0")
for item in tracked:
    if not item:
        continue
    path = root / item
    raw = path.read_bytes()
    if b"\0" in raw:
        continue
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(f"{item}: tracked scaffold text is not valid UTF-8")
        continue
    for number, line in enumerate(text.splitlines(), 1):
        for character in line:
            if not character.isalpha() or character in allowed_non_latin_letters:
                continue
            if "LATIN" not in unicodedata.name(character, ""):
                errors.append(f"{item}:{number}: persistent scaffold content must be English-only")
                break

shell_files = subprocess.run(
    ["git", "ls-files", "-z", "--", "*.sh"], check=True, stdout=subprocess.PIPE
).stdout.decode("utf-8").split("\0")
for item in shell_files:
    if not item:
        continue
    result = subprocess.run(["bash", "-n", str(root / item)], capture_output=True, text=True)
    if result.returncode:
        errors.append(f"{item}: bash -n failed: {result.stderr.strip()}")

if errors:
    print(f"check-skills: FAIL — {len(errors)} validation error(s)", file=sys.stderr)
    for error in errors:
        print(f"  {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    "check-skills: OK — 8 Codex skills, metadata, path policy, English-only content, "
    f"and {len([item for item in shell_files if item])} shell file(s) validated."
)
PY
