"""Command-line entry point for RED."""

from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import shutil
import tomllib
from time import time_ns
from typing import Any, Sequence
import unicodedata

from jsonschema import Draft202012Validator, FormatChecker

from . import PROTOCOL_VERSION, __version__


DEFAULT_CONFIG = """version = 1

[document]
paths = ["README.md", "docs/**"]

[research]
path = "research"

[evolve]
path = "evolve"

[policy]
document_requires_approval = true
report_document_implementation_conflicts = true
"""
RED_START_MARKER = f"<!-- red:start protocol={PROTOCOL_VERSION} -->"
RED_END_MARKER = "<!-- red:end -->"


def load_protocol_schema(name: str) -> dict[str, Any]:
    candidates = [
        Path(__file__).resolve().parent / "bundled" / "protocol" / f"{name}-schema.json",
        Path(__file__).resolve().parents[4] / "spec" / f"{name}-schema.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Bundled RED {name} schema is missing")


CONFIG_VALIDATOR = Draft202012Validator(
    load_protocol_schema("config"), format_checker=FormatChecker()
)
ARTIFACT_VALIDATOR = Draft202012Validator(
    load_protocol_schema("artifact"), format_checker=FormatChecker()
)


def pointer_segment(value: object) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def normalized_schema_errors(prefix: str, errors: object) -> list[str]:
    normalized: set[str] = set()
    for error in errors:
        locations = [pointer_segment(part) for part in error.absolute_path]
        keyword = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", error.validator).upper()
        if error.validator == "required" and isinstance(error.instance, dict):
            missing = sorted(set(error.validator_value) - set(error.instance))
            for item in missing:
                location = prefix + "/" + "/".join(
                    [*locations, pointer_segment(item)]
                )
                normalized.add(f"RED_SCHEMA_{keyword} {location}")
            continue
        elif error.validator == "additionalProperties" and isinstance(
            error.instance, dict
        ):
            allowed = set(error.schema.get("properties", {}))
            extras = sorted(set(error.instance) - allowed)
            for item in extras:
                location = prefix + "/" + "/".join(
                    [*locations, pointer_segment(item)]
                )
                normalized.add(f"RED_SCHEMA_{keyword} {location}")
            continue
        location = prefix + ("/" + "/".join(locations) if locations else "")
        normalized.add(f"RED_SCHEMA_{keyword} {location or '/'}")
    return sorted(normalized)


def emit(payload: dict[str, Any], *, as_json: bool, message: str) -> None:
    print(json.dumps(payload, separators=(",", ":")) if as_json else message)


def load_config(root: Path) -> dict[str, Any]:
    with (root / "red.toml").open("rb") as config_file:
        return tomllib.load(config_file)


def is_project_relative(root: Path, configured_path: object) -> bool:
    if not isinstance(configured_path, str) or not configured_path:
        return False
    candidate = Path(configured_path[:-3] if configured_path.endswith("/**") else configured_path)
    return not candidate.is_absolute() and (root / candidate).resolve().is_relative_to(
        root.resolve()
    )


def validate_config(root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        config = load_config(root)
    except (OSError, tomllib.TOMLDecodeError) as error:
        return None, [f"Cannot read red.toml: {error}"]

    errors = normalized_schema_errors("red.toml", CONFIG_VALIDATOR.iter_errors(config))
    if errors:
        return config, errors
    version = config["version"]
    if version != PROTOCOL_VERSION:
        return config, [
            f"Unsupported RED protocol; expected {PROTOCOL_VERSION}"
        ]
    if isinstance(config.get("document", {}).get("paths"), list):
        for document_path in config["document"]["paths"]:
            if not is_project_relative(root, document_path):
                errors.append(
                    f"document path must stay within the project: {document_path}"
                )
    for state in ("research", "evolve"):
        configured_path = config.get(state, {}).get("path")
        if isinstance(configured_path, str) and not is_project_relative(root, configured_path):
            errors.append(f"{state}.path must stay within the project")
    return config, errors


def read_artifact(file: Path, expected_state: str) -> dict[str, Any]:
    content = file.read_text(encoding="utf-8")
    match = re.match(r"^\+\+\+\r?\n(.*?)\r?\n\+\+\+(?:\r?\n|$)", content, re.DOTALL)
    if not match:
        raise ValueError(f"{file} has no TOML frontmatter")
    metadata = tomllib.loads(match.group(1))
    return {
        "content": content,
        "file": file,
        "metadata": metadata,
        "expected_state": expected_state,
    }


def replace_artifact_frontmatter(content: str, metadata: dict[str, Any]) -> str:
    match = re.match(r"^\+\+\+\r?\n.*?\r?\n\+\+\+(?:\r?\n|$)", content, re.DOTALL)
    if not match:
        raise ValueError("Artifact has no TOML frontmatter")
    lines = [
        f"id = {toml_string(metadata['id'])}",
        f"state = {toml_string(metadata['state'])}",
        f"status = {toml_string(metadata['status'])}",
        f"title = {toml_string(metadata['title'])}",
        f"created = {toml_string(metadata['created'])}",
    ]
    if "based_on" in metadata:
        lines.append(
            "based_on = ["
            + ", ".join(toml_string(item) for item in metadata["based_on"])
            + "]"
        )
    if "document_paths" in metadata:
        lines.append(
            "document_paths = ["
            + ", ".join(toml_string(item) for item in metadata["document_paths"])
            + "]"
        )
    if "verified" in metadata:
        lines.append(f"verified = {'true' if metadata['verified'] else 'false'}")
    trailing_newline = "\n" if re.search(r"\r?\n$", match.group(0)) else ""
    return (
        "+++\n"
        + "\n".join(lines)
        + "\n+++"
        + trailing_newline
        + content[match.end() :]
    )


def validate_artifacts(
    root: Path, config: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str]]:
    artifacts: list[dict[str, Any]] = []
    errors: list[str] = []
    for state in ("research", "evolve"):
        for file in markdown_files(root / config[state]["path"]):
            try:
                artifacts.append(read_artifact(file, state))
            except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
                errors.append(f"{file.relative_to(root).as_posix()}: {error}")

    identifiers: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        metadata = artifact["metadata"]
        identifier = metadata.get("id")
        state = artifact["expected_state"]
        prefix = "R" if state == "research" else "E"
        display_path = artifact["file"].relative_to(root).as_posix()
        errors.extend(
            normalized_schema_errors(
                display_path, ARTIFACT_VALIDATOR.iter_errors(metadata)
            )
        )
        if (
            metadata.get("state") != state
            or not isinstance(identifier, str)
            or not re.fullmatch(rf"{prefix}-(?:[1-9]\d*|0\d{{3}})", identifier)
        ):
            errors.append(f"{display_path}: identity does not match {state} state")
        if isinstance(identifier, str) and not artifact["file"].name.startswith(
            f"{identifier}-"
        ):
            errors.append(f"{display_path}: filename must start with {identifier}-")
        if isinstance(identifier, str):
            if identifier in identifiers:
                errors.append(f"{display_path}: duplicate artifact id {identifier}")
            identifiers[identifier] = artifact

    for artifact in artifacts:
        references = artifact["metadata"].get("based_on", [])
        display_path = artifact["file"].relative_to(root).as_posix()
        if not isinstance(references, list):
            errors.append(f"{display_path}: based_on must be an array")
            continue
        for reference in references:
            if reference not in identifiers:
                errors.append(f"{display_path}: unknown artifact {reference}")
        document_paths = artifact["metadata"].get("document_paths", [])
        if isinstance(document_paths, list):
            for document_path in document_paths:
                if (
                    not is_project_relative(root, document_path)
                    or not accepts_document_path(root, document_path, config["document"]["paths"])
                    or not (root / document_path).resolve().exists()
                ):
                    errors.append(f"{display_path}: invalid Document path {document_path}")
    return artifacts, errors


def markdown_files(directory: Path) -> list[Path]:
    return sorted(directory.rglob("*.md")) if directory.exists() else []


def document_count(root: Path, patterns: list[str]) -> int:
    found: set[Path] = set()
    for pattern in patterns:
        if pattern.endswith("/**"):
            found.update(markdown_files(root / pattern[:-3]))
        else:
            target = root / pattern
            if target.exists():
                found.add(target.resolve())
    return len(found)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).lower()
    characters = [character if character.isalnum() else "-" for character in normalized]
    return re.sub(r"-+", "-", "".join(characters)).strip("-") or "untitled"


def next_identifier(artifacts: list[dict[str, Any]], prefix: str) -> str:
    numbers = []
    for artifact in artifacts:
        match = re.fullmatch(
            rf"{prefix}-((?:[1-9]\d*)|(?:0\d{{3}}))",
            str(artifact["metadata"].get("id", "")),
        )
        if match:
            numbers.append(int(match.group(1)))
    return f"{prefix}-{max(numbers, default=0) + 1}"


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_artifact(
    state: str, identifier: str, title: str, based_on: list[str], created: str
) -> str:
    metadata = [
        f"id = {toml_string(identifier)}",
        f"state = {toml_string(state)}",
        'status = "open"',
        f"title = {toml_string(title)}",
        f'created = "{created}"',
    ]
    if based_on:
        metadata.append(f"based_on = [{', '.join(toml_string(item) for item in based_on)}]")
    sections = (
        ["Question", "Evidence", "Unknowns"]
        if state == "research"
        else ["Change", "Rationale", "Acceptance", "Open questions"]
    )
    body = "\n".join(f"## {section}\n" for section in sections)
    return (
        "+++\n"
        + "\n".join(metadata)
        + f"\n+++\n\n# {identifier}: {title}\n\n{body}\n"
    )


def create_artifact(
    root: Path, state: str, title: str, based_on: list[str]
) -> dict[str, Any]:
    if state not in {"research", "evolve"}:
        raise ValueError("state must be research or evolve")
    config, errors = validate_config(root)
    if errors or config is None:
        raise ValueError("; ".join(errors))
    artifacts, artifact_errors = validate_artifacts(root, config)
    if artifact_errors:
        raise ValueError("; ".join(artifact_errors))
    if based_on:
        identifiers = {artifact["metadata"].get("id") for artifact in artifacts}
        unknown = [identifier for identifier in based_on if identifier not in identifiers]
        if unknown:
            raise ValueError(f"Unknown source artifact: {', '.join(unknown)}")
    prefix = "R" if state == "research" else "E"
    identifier = next_identifier(artifacts, prefix)
    created = date.today().isoformat()
    metadata: dict[str, Any] = {
        "id": identifier,
        "state": state,
        "status": "open",
        "title": title,
        "created": created,
    }
    if based_on:
        metadata["based_on"] = based_on
    prospective_errors = normalized_schema_errors(
        identifier, ARTIFACT_VALIDATOR.iter_errors(metadata)
    )
    if prospective_errors:
        raise ValueError("; ".join(prospective_errors))
    directory = root / config[state]["path"]
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{identifier}-{slugify(title)}.md"
    with destination.open("x", encoding="utf-8", newline="\n") as artifact_file:
        artifact_file.write(
            render_artifact(state, identifier, title, based_on, created)
        )
    return {
        "ok": True,
        "id": identifier,
        "path": destination.relative_to(root).as_posix(),
        "state": state,
    }


def skill_source() -> Path:
    candidates = [
        Path(__file__).resolve().parent / "bundled" / "skill" / "red",
        Path(__file__).resolve().parents[4] / "plugins" / "red" / "skills" / "red",
    ]
    for candidate in candidates:
        if (candidate / "SKILL.md").is_file():
            return candidate
    raise FileNotFoundError("Bundled RED Skill is missing from this distribution")


def skill_asset(name: str) -> str:
    asset = skill_source() / "assets" / name
    if not asset.is_file():
        raise FileNotFoundError(f"Bundled RED asset is missing: {name}")
    return asset.read_text(encoding="utf-8")


def install_instructions(root: Path, target: str) -> dict[str, Any]:
    destination = (root / target).resolve()
    fragment = skill_asset("AGENTS.fragment.md").rstrip()
    current = destination.read_text(encoding="utf-8") if destination.exists() else ""
    start = current.find(RED_START_MARKER)
    end = current.find(RED_END_MARKER, max(start, 0))
    if (
        (start >= 0) != (end >= 0)
        or current.count(RED_START_MARKER) > 1
        or current.count(RED_END_MARKER) > 1
    ):
        raise ValueError(
            "Managed RED instructions block is malformed; refusing to modify it"
        )
    if start >= 0 and end >= start:
        updated = current[:start] + fragment + current[end + len(RED_END_MARKER) :]
    else:
        prefix = current.rstrip()
        updated = prefix + ("\n\n" if prefix else "") + fragment + "\n"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(updated, encoding="utf-8", newline="\n")
    return {
        "ok": True,
        "path": destination.relative_to(root).as_posix(),
        "protocolVersion": PROTOCOL_VERSION,
    }


def uninstall_instructions(root: Path, target: str) -> dict[str, Any]:
    destination = (root / target).resolve()
    if not destination.exists():
        raise FileNotFoundError(f"Instructions file does not exist: {target}")
    current = destination.read_text(encoding="utf-8")
    start = current.find(RED_START_MARKER)
    end = current.find(RED_END_MARKER, max(start, 0))
    if (
        start < 0
        or end < start
        or current.count(RED_START_MARKER) != 1
        or current.count(RED_END_MARKER) != 1
    ):
        raise ValueError(
            "Exactly one complete managed RED instructions block is required"
        )
    remaining = (current[:start] + current[end + len(RED_END_MARKER) :]).rstrip()
    destination.write_text(remaining + ("\n" if remaining else ""), encoding="utf-8", newline="\n")
    return {
        "ok": True,
        "path": destination.relative_to(root).as_posix(),
        "protocolVersion": PROTOCOL_VERSION,
    }


def skill_destination(root: Path, scope: str) -> Path:
    return (
        root / ".agents" / "skills" / "red"
        if scope == "repo"
        else Path.home() / ".agents" / "skills" / "red"
    )


def managed_skill_metadata(destination: Path) -> dict[str, Any]:
    metadata_file = destination / ".red-install.json"
    if not metadata_file.is_file():
        raise FileNotFoundError(f"No managed RED Skill at {destination}")
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    if metadata.get("distribution") != "red":
        raise ValueError(f"Refusing to modify unmanaged Skill at {destination}")
    return metadata


def install_skill(root: Path, scope: str) -> dict[str, Any]:
    destination = skill_destination(root, scope)
    if destination.exists():
        raise FileExistsError(f"RED Skill already exists at {destination}")
    write_skill(destination)
    return {
        "ok": True,
        "path": ".agents/skills/red" if scope == "repo" else str(destination),
        "scope": scope,
    }


def write_skill(destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill_source(), destination)
    metadata = {
        "distribution": "red",
        "protocolVersion": PROTOCOL_VERSION,
        "releaseVersion": __version__,
    }
    (destination / ".red-install.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


def update_skill(root: Path, scope: str) -> dict[str, Any]:
    destination = skill_destination(root, scope)
    managed_skill_metadata(destination)
    nonce = f"{os.getpid()}-{time_ns()}"
    staging = destination.with_name(f"{destination.name}.red-stage-{nonce}")
    backup = destination.with_name(f"{destination.name}.red-backup-{nonce}")
    try:
        write_skill(staging)
        destination.rename(backup)
        try:
            staging.rename(destination)
        except OSError:
            backup.rename(destination)
            raise
        shutil.rmtree(backup)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return {
        "ok": True,
        "path": ".agents/skills/red" if scope == "repo" else str(destination),
        "scope": scope,
    }


def find_artifact(root: Path, identifier: str, config: dict[str, Any]) -> dict[str, Any]:
    artifacts, errors = validate_artifacts(root, config)
    if errors:
        raise ValueError("; ".join(errors))
    resolved = (root / identifier).resolve()
    for artifact in artifacts:
        if artifact["metadata"].get("id") == identifier or artifact["file"].resolve() == resolved:
            return artifact
    raise FileNotFoundError(f"Artifact not found: {identifier}")


def accepts_document_path(root: Path, document_path: str, patterns: list[str]) -> bool:
    if not is_project_relative(root, document_path):
        return False
    normalized = document_path.replace("\\", "/")
    return any(
        normalized.startswith(pattern[:-2]) if pattern.endswith("/**") else normalized == pattern
        for pattern in patterns
    )


def accept_into_document(
    root: Path,
    artifact: dict[str, Any],
    document_paths: list[str],
    config: dict[str, Any],
    accepted: bool,
    verified: bool,
) -> dict[str, Any]:
    if artifact["expected_state"] != "evolve":
        raise ValueError("Only Evolve artifacts can promote to Document")
    if not accepted or not verified:
        raise ValueError(
            "Document promotion requires explicit --accepted and --verified assertions"
        )
    if not document_paths:
        raise ValueError("At least one --document path is required")
    for document_path in document_paths:
        if not accepts_document_path(root, document_path, config["document"]["paths"]):
            raise ValueError(f"{document_path} is not declared by document.paths")
        if not (root / document_path).exists():
            raise FileNotFoundError(f"Document does not exist: {document_path}")
    prospective = {
        **artifact["metadata"],
        "status": "accepted",
        "verified": True,
        "document_paths": document_paths,
    }
    prospective_errors = normalized_schema_errors(
        artifact["metadata"]["id"], ARTIFACT_VALIDATOR.iter_errors(prospective)
    )
    if prospective_errors:
        raise ValueError("; ".join(prospective_errors))
    updated = replace_artifact_frontmatter(artifact["content"], prospective)
    final_match = re.match(r"^\+\+\+\n(.*?)\n\+\+\+(?:\n|$)", updated, re.DOTALL)
    final_metadata = tomllib.loads(final_match.group(1)) if final_match else None
    if (
        final_metadata != prospective
        or list(ARTIFACT_VALIDATOR.iter_errors(final_metadata))
    ):
        raise ValueError("Refusing to write invalid promoted artifact metadata")
    artifact["file"].write_text(updated, encoding="utf-8", newline="\n")
    return {
        "ok": True,
        "id": artifact["metadata"]["id"],
        "path": artifact["file"].relative_to(root).as_posix(),
        "state": "document",
        "status": "accepted",
        "documentPaths": document_paths,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="red", description="Deterministic operations for the RED methodology"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    version = commands.add_parser("version")
    version.add_argument("--json", action="store_true")

    initialize = commands.add_parser("init")
    initialize.add_argument("--json", action="store_true")

    new = commands.add_parser("new")
    new.add_argument("state", choices=["research", "evolve"])
    new.add_argument("--title", required=True)
    new.add_argument("--from", dest="based_on", nargs="+", default=[])
    new.add_argument("--json", action="store_true")

    promote = commands.add_parser("promote")
    promote.add_argument("artifact")
    promote.add_argument("--to", choices=["evolve", "document"], required=True)
    promote.add_argument("--title")
    promote.add_argument("--document", nargs="+", default=[])
    promote.add_argument("--accepted", action="store_true")
    promote.add_argument("--verified", action="store_true")
    promote.add_argument("--json", action="store_true")

    status = commands.add_parser("status")
    status.add_argument("--json", action="store_true")

    check = commands.add_parser("check")
    check.add_argument("--json", action="store_true")

    instructions = commands.add_parser("instructions")
    instruction_commands = instructions.add_subparsers(
        dest="instruction_command", required=True
    )
    instruction_install = instruction_commands.add_parser("install")
    instruction_install.add_argument("--target", default="AGENTS.md")
    instruction_install.add_argument("--json", action="store_true")
    instruction_export = instruction_commands.add_parser("export")
    instruction_export.add_argument("--output", default="RED.md")
    instruction_export.add_argument("--json", action="store_true")
    instruction_uninstall = instruction_commands.add_parser("uninstall")
    instruction_uninstall.add_argument("--target", default="AGENTS.md")
    instruction_uninstall.add_argument("--json", action="store_true")

    skill = commands.add_parser("skill")
    skill_commands = skill.add_subparsers(dest="skill_command", required=True)
    skill_install = skill_commands.add_parser("install")
    skill_install.add_argument("--scope", choices=["repo", "user"], default="repo")
    skill_install.add_argument("--json", action="store_true")
    for action in ("status", "update", "uninstall"):
        lifecycle = skill_commands.add_parser(action)
        lifecycle.add_argument("--scope", choices=["repo", "user"], default="repo")
        lifecycle.add_argument("--json", action="store_true")

    return parser


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "version":
        payload = {
            "ok": True,
            "protocolVersion": PROTOCOL_VERSION,
            "releaseVersion": __version__,
        }
        emit(
            payload,
            as_json=args.json,
            message=f"RED {__version__} (protocol {PROTOCOL_VERSION})",
        )
        return 0

    if args.command == "init":
        destination = Path("red.toml")
        with destination.open("x", encoding="utf-8", newline="\n") as config_file:
            config_file.write(DEFAULT_CONFIG)
        emit(
            {"ok": True, "created": "red.toml", "protocolVersion": PROTOCOL_VERSION},
            as_json=args.json,
            message="Created red.toml",
        )
        return 0

    if args.command == "new":
        payload = create_artifact(Path.cwd(), args.state, args.title, args.based_on)
        emit(
            payload,
            as_json=args.json,
            message=f"Created {payload['id']} at {payload['path']}",
        )
        return 0

    if args.command == "promote":
        root = Path.cwd()
        config, errors = validate_config(root)
        if errors or config is None:
            raise ValueError("; ".join(errors))
        artifact = find_artifact(root, args.artifact, config)
        if args.to == "evolve":
            if artifact["expected_state"] != "research":
                raise ValueError("Only Research artifacts can promote to Evolve")
            payload = create_artifact(
                root,
                "evolve",
                args.title or artifact["metadata"]["title"],
                [artifact["metadata"]["id"]],
            )
        else:
            payload = accept_into_document(
                root,
                artifact,
                args.document,
                config,
                args.accepted,
                args.verified,
            )
        emit(payload, as_json=args.json, message=f"Promoted {args.artifact} to {args.to}")
        return 0

    if args.command == "status":
        root = Path.cwd()
        config, errors = validate_config(root)
        if errors or config is None:
            raise ValueError("; ".join(errors))
        payload = {
            "ok": True,
            "protocolVersion": PROTOCOL_VERSION,
            "counts": {
                "document": document_count(root, config["document"]["paths"]),
                "evolve": len(markdown_files(root / config["evolve"]["path"])),
                "research": len(markdown_files(root / config["research"]["path"])),
            },
        }
        emit(
            payload,
            as_json=args.json,
            message=(
                f"Document: {payload['counts']['document']}, "
                f"Evolve: {payload['counts']['evolve']}, "
                f"Research: {payload['counts']['research']}"
            ),
        )
        return 0

    if args.command == "check":
        root = Path.cwd()
        config, errors = validate_config(root)
        if config is not None and not errors:
            _, artifact_errors = validate_artifacts(root, config)
            errors.extend(artifact_errors)
        payload = {
            "ok": not errors,
            "errors": errors,
            "protocolVersion": PROTOCOL_VERSION,
        }
        emit(
            payload,
            as_json=args.json,
            message="RED project is valid" if not errors else "\n".join(errors),
        )
        return 0 if not errors else 1

    if args.command == "instructions":
        if args.instruction_command == "install":
            payload = install_instructions(Path.cwd(), args.target)
            emit(
                payload,
                as_json=args.json,
                message=f"Installed RED instructions in {payload['path']}",
            )
            return 0
        if args.instruction_command == "export":
            destination = (Path.cwd() / args.output).resolve()
            with destination.open("x", encoding="utf-8", newline="\n") as output_file:
                output_file.write(skill_asset("RED.md"))
            payload = {
                "ok": True,
                "path": destination.relative_to(Path.cwd()).as_posix(),
                "protocolVersion": PROTOCOL_VERSION,
            }
            emit(
                payload,
                as_json=args.json,
                message=f"Exported RED instructions to {payload['path']}",
            )
            return 0
        if args.instruction_command == "uninstall":
            payload = uninstall_instructions(Path.cwd(), args.target)
            emit(
                payload,
                as_json=args.json,
                message=f"Removed RED instructions from {payload['path']}",
            )
            return 0

    if args.command == "skill" and args.skill_command == "install":
        payload = install_skill(Path.cwd(), args.scope)
        emit(
            payload,
            as_json=args.json,
            message=f"Installed RED Skill at {payload['path']}",
        )
        return 0


    if args.command == "skill" and args.skill_command in {"status", "update", "uninstall"}:
        root = Path.cwd()
        destination = skill_destination(root, args.scope)
        metadata = managed_skill_metadata(destination)
        display_path = ".agents/skills/red" if args.scope == "repo" else str(destination)
        if args.skill_command == "status":
            payload = {"ok": True, "installed": True, "path": display_path, **metadata}
        elif args.skill_command == "update":
            payload = update_skill(root, args.scope)
        else:
            shutil.rmtree(destination)
            payload = {"ok": True, "removed": True, "path": display_path, "scope": args.scope}
        emit(
            payload,
            as_json=args.json,
            message=f"{args.skill_command} completed for {display_path}",
        )
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return run(argv)
    except (FileExistsError, FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
