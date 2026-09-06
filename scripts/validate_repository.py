"""Validate RED configuration, Skill, plugin, schemas, and version alignment."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tomllib

from jsonschema import Draft202012Validator
import yaml


REPOSITORY = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_skill() -> None:
    skill_file = REPOSITORY / "plugins" / "red" / "skills" / "red" / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter")
    metadata = yaml.safe_load(match.group(1))
    if metadata.get("name") != "red" or not metadata.get("description"):
        raise ValueError("SKILL.md requires name red and a description")
    if metadata.get("metadata", {}).get("red-protocol") != "1":
        raise ValueError("SKILL.md must declare RED Protocol 1")
    for link in re.findall(r"\]\(([^)]+)\)", content):
        if not (skill_file.parent / link).is_file():
            raise ValueError(f"Broken SKILL.md link: {link}")


def validate_plugin() -> dict[str, object]:
    manifest = load_json(REPOSITORY / "plugins" / "red" / ".codex-plugin" / "plugin.json")
    required = {"name", "version", "description", "author", "license", "skills"}
    missing = required - manifest.keys()
    if missing:
        raise ValueError(f"Plugin manifest missing: {', '.join(sorted(missing))}")
    if manifest["name"] != "red" or manifest["license"] != "Apache-2.0":
        raise ValueError("Plugin identity or license is invalid")
    return manifest


def validate_versions(manifest: dict[str, object]) -> None:
    node = load_json(REPOSITORY / "cli" / "node" / "package.json")
    with (REPOSITORY / "cli" / "python" / "pyproject.toml").open("rb") as source:
        python = tomllib.load(source)
    versions = {str(node["version"]), str(python["project"]["version"]), str(manifest["version"])}
    if len(versions) != 1:
        raise ValueError(f"Release versions differ: {sorted(versions)}")
    if node["license"] != "Apache-2.0" or python["project"]["license"] != "Apache-2.0":
        raise ValueError("All distributions must use Apache-2.0")


def validate_local_self_hosted_skill(manifest: dict[str, object]) -> None:
    canonical = REPOSITORY / "plugins" / "red" / "skills" / "red"
    installed = REPOSITORY / ".agents" / "skills" / "red"
    if not installed.exists():
        return
    install_metadata = load_json(installed / ".red-install.json")
    expected_metadata = {
        "distribution": "red",
        "protocolVersion": 1,
        "releaseVersion": manifest["version"],
    }
    if install_metadata != expected_metadata:
        raise ValueError("Local self-hosted RED Skill installation metadata is stale")

    canonical_files = {
        file.relative_to(canonical): file.read_bytes()
        for file in canonical.rglob("*")
        if file.is_file()
    }
    installed_files = {
        file.relative_to(installed): file.read_bytes()
        for file in installed.rglob("*")
        if file.is_file() and file.name != ".red-install.json"
    }
    if installed_files != canonical_files:
        raise ValueError("Local self-hosted RED Skill snapshot differs from canonical Skill")


def main() -> int:
    config_schema = load_json(REPOSITORY / "spec" / "config-schema.json")
    artifact_schema = load_json(REPOSITORY / "spec" / "artifact-schema.json")
    output_schema = load_json(REPOSITORY / "spec" / "output-schema.json")
    Draft202012Validator.check_schema(config_schema)
    Draft202012Validator.check_schema(artifact_schema)
    Draft202012Validator.check_schema(output_schema)
    with (REPOSITORY / "red.toml").open("rb") as source:
        config = tomllib.load(source)
    Draft202012Validator(config_schema).validate(config)
    validate_skill()
    manifest = validate_plugin()
    validate_versions(manifest)
    validate_local_self_hosted_skill(manifest)
    print("Repository metadata and Protocol 1 schemas are valid")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
