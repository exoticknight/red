"""Copy canonical release-owned files into both package build trees."""

from __future__ import annotations

from pathlib import Path
import shutil


REPOSITORY = Path(__file__).resolve().parents[1]
SKILL_SOURCE = REPOSITORY / "plugins" / "red" / "skills" / "red"
SKILL_TARGETS = (
    REPOSITORY / "cli" / "node" / "bundled" / "skill" / "red",
    REPOSITORY / "cli" / "python" / "src" / "red_cli" / "bundled" / "skill" / "red",
)
PACKAGE_ROOTS = (REPOSITORY / "cli" / "node", REPOSITORY / "cli" / "python")
PROTOCOL_FILES = ("config-schema.json", "artifact-schema.json")


def assert_build_target(target: Path) -> None:
    resolved = target.resolve()
    if not resolved.is_relative_to(REPOSITORY.resolve()) or "bundled" not in resolved.parts:
        raise ValueError(f"Refusing to replace unexpected path: {resolved}")


def main() -> int:
    if not (SKILL_SOURCE / "SKILL.md").is_file():
        raise FileNotFoundError("Canonical RED Skill is missing")
    for target in SKILL_TARGETS:
        assert_build_target(target)
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL_SOURCE, target)
    protocol_targets = (
        REPOSITORY / "cli" / "node" / "bundled" / "protocol",
        REPOSITORY / "cli" / "python" / "src" / "red_cli" / "bundled" / "protocol",
    )
    for target in protocol_targets:
        assert_build_target(target)
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        for name in PROTOCOL_FILES:
            shutil.copy2(REPOSITORY / "spec" / name, target / name)
    for package_root in PACKAGE_ROOTS:
        for name in ("LICENSE", "NOTICE"):
            shutil.copy2(REPOSITORY / name, package_root / name)
    print("Synchronized Skill, protocol schemas, LICENSE, and NOTICE into package trees")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
