#!/usr/bin/env bash
# Validate the Codex-native skill surface and named scaffold contracts.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

command -v python3 >/dev/null 2>&1 || {
  echo "check-skills: ERROR — python3 is required" >&2
  exit 2
}
command -v ruby >/dev/null 2>&1 || {
  echo "check-skills: ERROR — ruby is required for YAML validation" >&2
  exit 2
}

TOML_PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3; do
  if command -v "$candidate" >/dev/null 2>&1 \
    && "$candidate" -I -c \
      'import sys, tomllib; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' \
      >/dev/null 2>&1; then
    TOML_PYTHON="$candidate"
    break
  fi
done
if [[ -z "$TOML_PYTHON" ]]; then
  echo "check-skills: ERROR — Python 3.11+ with standard-library tomllib is required for Codex TOML validation" >&2
  exit 2
fi

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
  task-routing session-orchestration verification retro codex-automation
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

"$TOML_PYTHON" -I - "$ROOT" <<'PY'
from __future__ import annotations

import pathlib
import re
import sys
import tomllib
from collections.abc import Iterator
from typing import Any

root = pathlib.Path(sys.argv[1]).resolve()
config_path = root / ".codex/config.toml"
agents_root = root / ".codex/agents"
expected_agents = {"explorer", "orchestrator", "planner", "reviewer"}
allowed_config_root_keys = {"agents", "mcp_servers"}
allowed_agents_config_keys = {"enabled"}
project_agent_keys = {
    "name",
    "description",
    "sandbox_mode",
    "developer_instructions",
}
model_pin_keys = {
    "model",
    "model_provider",
    "model_reasoning_effort",
    "reasoning_effort",
}
credential_key = re.compile(
    r"(?:^|[_-])(?:api[_-]?key|access[_-]?token|auth[_-]?token|credential|password|private[_-]?key|secret|token)(?:$|[_-])",
    re.IGNORECASE,
)
personal_path_key = re.compile(
    r"(?:^|[_-])(?:cwd|home|path|working[_-]?directory|workspace)(?:$|[_-])",
    re.IGNORECASE,
)
personal_path_value = re.compile(
    r"(?:^|[\s='\"])(?:~[/\\]|/Users/|/home/[^/\s]+/|[A-Za-z]:[/\\]Users[/\\])",
    re.IGNORECASE,
)
errors: list[str] = []


def relative(path: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def load_toml(path: pathlib.Path) -> dict[str, Any] | None:
    name = relative(path)
    if not path.is_file():
        errors.append(f"{name}: missing")
        return None
    try:
        with path.open("rb") as stream:
            document = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        errors.append(f"{name}: invalid TOML: {error}")
        return None
    if not isinstance(document, dict):
        errors.append(f"{name}: TOML root must be a table")
        return None
    return document


def walk_settings(value: Any, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            path = (*prefix, str(key))
            yield path, child
            yield from walk_settings(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_settings(child, (*prefix, f"[{index}]"))


def check_portability(document: dict[str, Any], name: str) -> None:
    reported: set[tuple[str, tuple[str, ...]]] = set()
    for path, value in walk_settings(document):
        key = path[-1]
        normalized = key.lower().replace("-", "_")
        if normalized in model_pin_keys:
            finding = ("model", path)
            if finding not in reported:
                errors.append(f"{name}: model pin setting {'.'.join(path)!r} is not portable")
                reported.add(finding)
        if credential_key.search(key):
            finding = ("credential", path)
            if finding not in reported:
                errors.append(f"{name}: credential setting {'.'.join(path)!r} is not allowed")
                reported.add(finding)
        if personal_path_key.search(key):
            finding = ("path-key", path)
            if finding not in reported:
                errors.append(f"{name}: personal-path setting {'.'.join(path)!r} is not allowed")
                reported.add(finding)
        if isinstance(value, str) and personal_path_value.search(value):
            finding = ("path-value", path)
            if finding not in reported:
                errors.append(f"{name}: {'.'.join(path)!r} contains a personal path")
                reported.add(finding)


config = load_toml(config_path)
if config is not None:
    config_name = relative(config_path)
    check_portability(config, config_name)
    unexpected_root_keys = set(config) - allowed_config_root_keys
    if unexpected_root_keys:
        errors.append(
            f"{config_name}: unsupported root keys: "
            + ", ".join(sorted(unexpected_root_keys))
        )
    agents_config = config.get("agents")
    if not isinstance(agents_config, dict):
        errors.append(f"{config_name}: agents must be a table")
    else:
        unexpected_agent_keys = set(agents_config) - allowed_agents_config_keys
        if unexpected_agent_keys:
            errors.append(
                f"{config_name}: unsupported agents keys: "
                + ", ".join(sorted(unexpected_agent_keys))
            )
        if agents_config.get("enabled") is not True:
            errors.append(f"{config_name}: agents.enabled must be boolean true")
    mcp_config = config.get("mcp_servers")
    if mcp_config is not None and not isinstance(mcp_config, dict):
        errors.append(f"{config_name}: mcp_servers must be a table when present")

if not agents_root.is_dir():
    errors.append(".codex/agents: missing")
    agent_paths: list[pathlib.Path] = []
else:
    agent_paths = sorted(path for path in agents_root.glob("*.toml") if path.is_file())

actual_agents = {path.stem for path in agent_paths}
for name in sorted(expected_agents - actual_agents):
    errors.append(f".codex/agents/{name}.toml: missing required project agent")

for path in agent_paths:
    document = load_toml(path)
    if document is None:
        continue
    name = relative(path)
    check_portability(document, name)
    if path.stem in expected_agents and set(document) != project_agent_keys:
        errors.append(
            f"{name}: bundled agent keys must be exactly name, description, "
            "sandbox_mode, and developer_instructions"
        )
    elif not project_agent_keys.issubset(document):
        errors.append(
            f"{name}: required keys are name, description, sandbox_mode, and "
            "developer_instructions"
        )
    expected_name = path.stem
    if document.get("name") != expected_name:
        errors.append(f"{name}: name must equal filename stem {expected_name!r}")
    for key in ("description", "developer_instructions"):
        value = document.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name}: {key} must be a non-empty string")
    if path.stem in expected_agents and document.get("sandbox_mode") != "read-only":
        errors.append(f"{name}: bundled coordination agents must use sandbox_mode 'read-only'")

if errors:
    print(f"check-skills: FAIL — {len(errors)} Codex TOML validation error(s)", file=sys.stderr)
    for error in errors:
        print(f"  {error}", file=sys.stderr)
    raise SystemExit(1)
PY

python3 - "$ROOT" <<'PY'
from __future__ import annotations

import pathlib
import json
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
    "codex-automation",
}
errors: list[str] = []

control_prefixes = (
    ".github/docs/",
    ".github/connectors/",
    ".github/scripts/",
    ".agents/",
    ".codex/",
    "plugin/agentic-dev-kit-for-codex/",
)
required_control_files = {
    "AGENTS.md",
    "SCAFFOLD-CHANGELOG.md",
    ".github/CODEOWNERS",
    ".github/docs/AGENTIC-DEV-KIT-LICENSE.txt",
    ".github/docs/AGENTIC-DEV-KIT-NOTICE.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/epic.yml",
    ".github/ISSUE_TEMPLATE/task.yml",
    ".github/ISSUE_TEMPLATE/feedback.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/dependabot.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/retro-hygiene.yml",
    ".github/workflows/adopter-feedback.yml",
}
optional_control_files = {"README.md", "CONTRIBUTING.md", "NOTICE.md", "SECURITY.md"}
control_files = required_control_files | optional_control_files


def in_control_scope(item: str) -> bool:
    return item in control_files or item.startswith(control_prefixes)


tracked = [
    item
    for item in subprocess.run(
        ["git", "ls-files", "-z"], check=True, stdout=subprocess.PIPE
    ).stdout.decode("utf-8").split("\0")
    if item
]
tracked_set = set(tracked)
control_tracked = sorted(item for item in tracked if in_control_scope(item))
for item in sorted(required_control_files - tracked_set):
    errors.append(f"required scaffold contract is not tracked: {item}")

if not skills_root.is_dir():
    print("check-skills: FAIL — .agents/skills is missing", file=sys.stderr)
    raise SystemExit(1)

actual_skills = {path.name for path in skills_root.iterdir() if path.is_dir()}
for name in sorted(expected_skills - actual_skills):
    errors.append(f"missing skill directory: .agents/skills/{name}")


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
    if name == "project-onboarding":
        for boundary_phrase in (
            "plugin-only",
            "partial",
            "Do not invoke, fabricate, or silently substitute a missing helper",
            "template or installer",
        ):
            if boundary_phrase not in skill_text:
                errors.append(
                    f"{skill_path.relative_to(root)}: missing plugin boundary "
                    f"{boundary_phrase!r}"
                )

plugin_root = root / "plugin/agentic-dev-kit-for-codex"
manifest_path = plugin_root / ".codex-plugin/plugin.json"
plugin_status = "plugin omitted by installer boundary"
canonical_readme = root / "README.md"
canonical_distribution = (
    canonical_readme.is_file()
    and canonical_readme.read_text(encoding="utf-8").startswith("# Agentic Dev Kit for Codex\n")
)
if canonical_distribution and not plugin_root.exists():
    errors.append("plugin/agentic-dev-kit-for-codex: canonical distribution plugin is missing")
if plugin_root.exists():
    plugin_status = "synchronized plugin package"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{manifest_path.relative_to(root)}: invalid or missing JSON: {error}")
        manifest = {}
    if manifest.get("name") != "agentic-dev-kit-for-codex":
        errors.append(f"{manifest_path.relative_to(root)}: name must match the plugin directory")
    if manifest.get("skills") != "./skills/":
        errors.append(f"{manifest_path.relative_to(root)}: skills must equal './skills/'")
    if manifest.get("license") != "MIT":
        errors.append(f"{manifest_path.relative_to(root)}: license must equal 'MIT'")
    interface = manifest.get("interface", {})
    if not isinstance(interface, dict):
        errors.append(f"{manifest_path.relative_to(root)}: interface must be an object")
        interface = {}
    if "Full GitHub governance requires the repository template or installer" not in str(
        interface.get("longDescription", "")
    ):
        errors.append(
            f"{manifest_path.relative_to(root)}: interface must disclose the plugin-only boundary"
        )

    if canonical_distribution:
        changelog_path = root / "SCAFFOLD-CHANGELOG.md"
        changelog_text = changelog_path.read_text(encoding="utf-8")
        candidate_match = re.search(
            r"^\*\*Current candidate:\*\* v([^\s]+)$", changelog_text, re.MULTILINE
        )
        plugin_version = manifest.get("version")
        if not candidate_match:
            errors.append(f"{changelog_path.relative_to(root)}: current candidate is missing")
        elif plugin_version != candidate_match.group(1):
            errors.append(
                f"{manifest_path.relative_to(root)}: version {plugin_version!r} must match "
                f"changelog current candidate {candidate_match.group(1)!r}"
            )
        if isinstance(plugin_version, str) and not re.search(
            rf"^### v{re.escape(plugin_version)}(?:\s|$)", changelog_text, re.MULTILINE
        ):
            errors.append(
                f"{changelog_path.relative_to(root)}: missing version heading for "
                f"plugin {plugin_version!r}"
            )

    plugin_license = plugin_root / "LICENSE"
    root_license = root / "LICENSE"
    if not plugin_license.is_file():
        errors.append(f"{plugin_license.relative_to(root)}: standalone package license is missing")
    elif root_license.is_file() and plugin_license.read_bytes() != root_license.read_bytes():
        errors.append(f"{plugin_license.relative_to(root)}: must match the repository MIT license")
    plugin_notice = plugin_root / "NOTICE.md"
    if not plugin_notice.is_file():
        errors.append(f"{plugin_notice.relative_to(root)}: standalone package notice is missing")
    else:
        notice_text = plugin_notice.read_text(encoding="utf-8")
        for required_notice in (
            "agentic-dev-kit-for-copilot",
            "f466c7e169243e2bea03b4b33a20f8c557328d96",
        ):
            if required_notice not in notice_text:
                errors.append(
                    f"{plugin_notice.relative_to(root)}: missing attribution {required_notice!r}"
                )

    plugin_skills_root = plugin_root / "skills"
    for name in sorted(expected_skills):
        canonical = skills_root / name
        packaged = plugin_skills_root / name
        if not packaged.is_dir():
            errors.append(f"{packaged.relative_to(root)}: packaged skill is missing")
            continue
        canonical_files = {
            path.relative_to(canonical).as_posix(): path
            for path in canonical.rglob("*")
            if path.is_file()
        }
        packaged_files = {
            path.relative_to(packaged).as_posix(): path
            for path in packaged.rglob("*")
            if path.is_file()
        }
        if canonical_files.keys() != packaged_files.keys():
            errors.append(f"{packaged.relative_to(root)}: file set differs from the canonical skill")
            continue
        for relative_name, canonical_path in canonical_files.items():
            if canonical_path.read_bytes() != packaged_files[relative_name].read_bytes():
                errors.append(
                    f"{packaged_files[relative_name].relative_to(root)}: differs from canonical "
                    f".agents/skills/{name}/{relative_name}"
                )
            canonical_mode = canonical_path.stat().st_mode & 0o111
            packaged_mode = packaged_files[relative_name].stat().st_mode & 0o111
            if canonical_mode != packaged_mode:
                errors.append(
                    f"{packaged_files[relative_name].relative_to(root)}: executable mode differs "
                    f"from canonical .agents/skills/{name}/{relative_name}"
                )

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

for item in control_tracked:
    path = root / item
    if path.name.endswith((".prompt.md", ".agent.md")):
        errors.append(f"deprecated agent-facing file exists: {item}")

agents_path = root / "AGENTS.md"
if not agents_path.is_file():
    errors.append("AGENTS.md is missing")
elif len(agents_path.read_text(encoding="utf-8").splitlines()) > 200:
    errors.append("AGENTS.md exceeds its 200-line constitution ceiling")

# Named control-plane content may use Unicode punctuation and the deliberate
# phase symbols α/β, but alphabetic prose must be Latin-script English.
allowed_non_latin_letters = {"α", "β"}
for item in control_tracked:
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

shell_files = [
    item
    for item in control_tracked
    if item.endswith(".sh")
    and item.startswith((".github/scripts/", ".agents/"))
]
for item in shell_files:
    result = subprocess.run(["bash", "-n", str(root / item)], capture_output=True, text=True)
    if result.returncode:
        errors.append(f"{item}: bash -n failed: {result.stderr.strip()}")

if errors:
    print(f"check-skills: FAIL — {len(errors)} validation error(s)", file=sys.stderr)
    for error in errors:
        print(f"  {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    f"check-skills: OK — 9 Codex skills, {plugin_status}, metadata, "
    "Codex TOML configuration, path policy, English-only control-plane content, "
    f"and {len(shell_files)} shell file(s) validated."
)
PY
