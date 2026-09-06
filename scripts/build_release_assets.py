"""Build portable plugin and Skill archives from canonical sources."""

from __future__ import annotations

from pathlib import Path
import sys
import zipfile


REPOSITORY = Path(__file__).resolve().parents[1]


def add_tree(archive: zipfile.ZipFile, source: Path, prefix: str) -> None:
    for file in sorted(source.rglob("*")):
        if file.is_file():
            archive.write(file, (Path(prefix) / file.relative_to(source)).as_posix())


def make_archive(output: Path, source: Path, prefix: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        add_tree(archive, source, prefix)
        archive.write(REPOSITORY / "LICENSE", f"{prefix}/LICENSE")
        archive.write(REPOSITORY / "NOTICE", f"{prefix}/NOTICE")


def main(version: str) -> int:
    output = REPOSITORY / "dist" / "bundles"
    make_archive(output / f"red-plugin-{version}.zip", REPOSITORY / "plugins" / "red", "red")
    make_archive(
        output / f"red-skill-{version}.zip",
        REPOSITORY / "plugins" / "red" / "skills" / "red",
        "red",
    )
    print(f"Built release bundles in {output}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: build_release_assets.py VERSION")
    raise SystemExit(main(sys.argv[1]))
