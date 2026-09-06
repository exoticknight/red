"""Verify that coordinated release archives contain their runtime resources."""

from __future__ import annotations

from pathlib import Path
import sys
import tarfile
import zipfile


REPOSITORY = Path(__file__).resolve().parents[1]


def require_members(actual: set[str], required: set[str], archive: Path) -> None:
    missing = required - actual
    if missing:
        raise ValueError(f"{archive.name} is missing: {', '.join(sorted(missing))}")


def main(version: str) -> int:
    npm = REPOSITORY / "dist" / "npm" / f"red-methodology-cli-{version}.tgz"
    with tarfile.open(npm, "r:gz") as archive:
        require_members(
            set(archive.getnames()),
            {
                "package/LICENSE",
                "package/NOTICE",
                "package/src/cli.js",
                "package/bundled/skill/red/SKILL.md",
                "package/bundled/protocol/config-schema.json",
                "package/bundled/protocol/artifact-schema.json",
            },
            npm,
        )

    wheels = list((REPOSITORY / "dist" / "python").glob(f"red_methodology_cli-{version}-*.whl"))
    source_distributions = list(
        (REPOSITORY / "dist" / "python").glob(f"red_methodology_cli-{version}.tar.gz")
    )
    if len(wheels) != 1 or len(source_distributions) != 1:
        raise ValueError("Expected one Python wheel and one source distribution")
    with zipfile.ZipFile(wheels[0]) as archive:
        require_members(
            set(archive.namelist()),
            {
                "red_cli/cli.py",
                "red_cli/bundled/skill/red/SKILL.md",
                "red_cli/bundled/protocol/config-schema.json",
                "red_cli/bundled/protocol/artifact-schema.json",
            },
            wheels[0],
        )
        if not any(name.endswith(".dist-info/licenses/LICENSE") for name in archive.namelist()):
            raise ValueError(f"{wheels[0].name} is missing LICENSE metadata")
    source_distribution = source_distributions[0]
    with tarfile.open(source_distribution, "r:gz") as archive:
        members = set(archive.getnames())
        required_suffixes = {
            "/src/red_cli/cli.py",
            "/src/red_cli/bundled/skill/red/SKILL.md",
            "/src/red_cli/bundled/protocol/config-schema.json",
            "/src/red_cli/bundled/protocol/artifact-schema.json",
            "/LICENSE",
        }
        missing_suffixes = {
            suffix
            for suffix in required_suffixes
            if not any(member.endswith(suffix) for member in members)
        }
        if missing_suffixes:
            raise ValueError(
                f"{source_distribution.name} is missing: "
                f"{', '.join(sorted(missing_suffixes))}"
            )

    plugin = REPOSITORY / "dist" / "bundles" / f"red-plugin-{version}.zip"
    skill = REPOSITORY / "dist" / "bundles" / f"red-skill-{version}.zip"
    with zipfile.ZipFile(plugin) as archive:
        require_members(
            set(archive.namelist()),
            {"red/.codex-plugin/plugin.json", "red/skills/red/SKILL.md", "red/LICENSE"},
            plugin,
        )
    with zipfile.ZipFile(skill) as archive:
        require_members(
            set(archive.namelist()),
            {"red/SKILL.md", "red/agents/openai.yaml", "red/LICENSE"},
            skill,
        )
    print(f"Verified coordinated release assets for {version}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_release_assets.py VERSION")
    raise SystemExit(main(sys.argv[1]))
