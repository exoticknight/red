"""Set coordinated build versions from a release tag."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


REPOSITORY = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(?:v)?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    content = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, content, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f"Could not set version in {path.relative_to(REPOSITORY)}")
    path.write_text(updated, encoding="utf-8", newline="\n")


def main(argument: str) -> int:
    match = SEMVER.fullmatch(argument)
    if not match:
        raise ValueError(f"Not a supported SemVer tag: {argument}")
    version = argument.removeprefix("v")

    package_file = REPOSITORY / "cli" / "node" / "package.json"
    package = json.loads(package_file.read_text(encoding="utf-8"))
    package["version"] = version
    package_file.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8", newline="\n")

    lock_file = REPOSITORY / "cli" / "node" / "package-lock.json"
    lock = json.loads(lock_file.read_text(encoding="utf-8"))
    lock["version"] = version
    lock["packages"][""]["version"] = version
    lock_file.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8", newline="\n")

    replace_once(
        REPOSITORY / "cli" / "python" / "pyproject.toml",
        r'^version = ".*"$',
        f'version = "{version}"',
    )
    replace_once(
        REPOSITORY / "cli" / "python" / "src" / "red_cli" / "__init__.py",
        r'^__version__ = ".*"$',
        f'__version__ = "{version}"',
    )

    manifest_file = REPOSITORY / "plugins" / "red" / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["version"] = version
    manifest_file.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(version)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: set_release_version.py vMAJOR.MINOR.PATCH")
    raise SystemExit(main(sys.argv[1]))
