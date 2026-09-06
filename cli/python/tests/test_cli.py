import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PACKAGE_ROOT / "src"
with (PACKAGE_ROOT / "pyproject.toml").open("rb") as project_file:
    RELEASE_VERSION = tomllib.load(project_file)["project"]["version"]


def run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SOURCE_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "red_cli.cli", *args],
        cwd=cwd,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


def run_cli_unchecked(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SOURCE_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "red_cli.cli", *args],
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


class CliTests(unittest.TestCase):
    def test_version_reports_release_and_protocol_versions_as_json(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-version-") as directory:
            result = run_cli("version", "--json", cwd=Path(directory))

        self.assertEqual(
            json.loads(result.stdout),
            {"ok": True, "protocolVersion": 1, "releaseVersion": RELEASE_VERSION},
        )

    def test_init_creates_a_parseable_project_configuration(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-init-") as directory:
            root = Path(directory)
            result = run_cli("init", "--json", cwd=root)
            config = (root / "red.toml").read_text(encoding="utf-8")

        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["created"], "red.toml")
        self.assertRegex(config, r"(?m)^version = 1")
        self.assertRegex(config, r'(?m)^paths = \["README\.md", "docs/\*\*"\]')
        self.assertRegex(config, r'(?m)^path = "research"')
        self.assertRegex(config, r'(?m)^path = "evolve"')

    def test_new_creates_sequential_research_and_evolve_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-new-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)
            research = json.loads(
                run_cli(
                    "new", "research", "--title", "Tag semantics", "--json", cwd=root
                ).stdout
            )
            evolve = json.loads(
                run_cli(
                    "new",
                    "evolve",
                    "--title",
                    "Add tags",
                    "--from",
                    research["id"],
                    "--json",
                    cwd=root,
                ).stdout
            )
            evolve_content = (root / evolve["path"]).read_text(encoding="utf-8")

        self.assertEqual(research["id"], "R-1")
        self.assertEqual(research["path"], "research/R-1-tag-semantics.md")
        self.assertEqual(evolve["id"], "E-1")
        self.assertEqual(evolve["path"], "evolve/E-1-add-tags.md")
        self.assertIn('based_on = ["R-1"]', evolve_content)

    def test_status_counts_artifacts_and_check_rejects_unsupported_protocol(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-status-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)
            run_cli("new", "research", "--title", "One", "--json", cwd=root)
            run_cli("new", "evolve", "--title", "Two", "--json", cwd=root)

            status = json.loads(run_cli("status", "--json", cwd=root).stdout)
            config_file = root / "red.toml"
            config_file.write_text(
                config_file.read_text(encoding="utf-8").replace(
                    "version = 1", "version = 99"
                ),
                encoding="utf-8",
            )
            invalid = run_cli_unchecked("check", "--json", cwd=root)

        self.assertEqual(
            status["counts"], {"document": 0, "evolve": 1, "research": 1}
        )
        self.assertEqual(invalid.returncode, 1)
        self.assertFalse(json.loads(invalid.stdout)["ok"])
        self.assertEqual(len(json.loads(invalid.stdout)["errors"]), 1)

    def test_instructions_preserve_agents_content_and_remain_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-instructions-") as directory:
            root = Path(directory)
            agents = root / "AGENTS.md"
            agents.write_text("# Existing instructions\n", encoding="utf-8")

            run_cli(
                "instructions",
                "install",
                "--target",
                "AGENTS.md",
                "--json",
                cwd=root,
            )
            run_cli(
                "instructions",
                "install",
                "--target",
                "AGENTS.md",
                "--json",
                cwd=root,
            )
            run_cli(
                "instructions",
                "export",
                "--output",
                "RED.md",
                "--json",
                cwd=root,
            )
            installed = agents.read_text(encoding="utf-8")
            exported = (root / "RED.md").read_text(encoding="utf-8")

        self.assertTrue(installed.startswith("# Existing instructions"))
        self.assertEqual(installed.count("<!-- red:start protocol=1 -->"), 1)
        self.assertTrue(exported.startswith("# RED Agent Instructions"))

    def test_skill_installs_into_repository_scope_with_release_metadata(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-skill-") as directory:
            root = Path(directory)
            result = json.loads(
                run_cli(
                    "skill", "install", "--scope", "repo", "--json", cwd=root
                ).stdout
            )
            installed = root / ".agents" / "skills" / "red"
            skill = (installed / "SKILL.md").read_text(encoding="utf-8")
            metadata = json.loads(
                (installed / ".red-install.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result["path"], ".agents/skills/red")
        self.assertIn("name: red", skill)
        self.assertEqual(
            metadata,
            {
                "distribution": "red",
                "protocolVersion": 1,
                "releaseVersion": RELEASE_VERSION,
            },
        )

    def test_skill_reports_updates_and_uninstalls_managed_installations(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-skill-lifecycle-") as directory:
            root = Path(directory)
            run_cli("skill", "install", "--scope", "repo", "--json", cwd=root)
            status = json.loads(
                run_cli("skill", "status", "--scope", "repo", "--json", cwd=root).stdout
            )
            skill_file = root / ".agents" / "skills" / "red" / "SKILL.md"
            skill_file.write_text("changed", encoding="utf-8")
            run_cli("skill", "update", "--scope", "repo", "--json", cwd=root)
            updated = skill_file.read_text(encoding="utf-8")
            run_cli("skill", "uninstall", "--scope", "repo", "--json", cwd=root)

            self.assertFalse(skill_file.parent.exists())

        self.assertTrue(status["installed"])
        self.assertEqual(status["releaseVersion"], RELEASE_VERSION)
        self.assertIn("name: red", updated)

    def test_instructions_can_remove_only_their_managed_block(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-instruction-remove-") as directory:
            root = Path(directory)
            agents = root / "AGENTS.md"
            agents.write_text("# Existing\n", encoding="utf-8")
            run_cli("instructions", "install", "--json", cwd=root)
            run_cli("instructions", "uninstall", "--json", cwd=root)
            remaining = agents.read_text(encoding="utf-8")

        self.assertEqual(remaining, "# Existing\n")

    def test_promote_creates_evolve_then_records_document_synchronization(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-promote-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)
            research = json.loads(
                run_cli("new", "research", "--title", "Need policy", "--json", cwd=root).stdout
            )
            evolve = json.loads(
                run_cli(
                    "promote",
                    research["id"],
                    "--to",
                    "evolve",
                    "--title",
                    "Adopt policy",
                    "--json",
                    cwd=root,
                ).stdout
            )
            (root / "README.md").write_text("# Project\n", encoding="utf-8")
            evolve_file = root / evolve["path"]
            evolve_file.write_text(
                evolve_file.read_text(encoding="utf-8")
                + '\n```toml\nverified = false\ndocument_paths = ["body.md"]\n```\n',
                encoding="utf-8",
            )
            accepted = json.loads(
                run_cli(
                    "promote",
                    evolve["id"],
                    "--to",
                    "document",
                    "--accepted",
                    "--verified",
                    "--document",
                    "README.md",
                    "--json",
                    cwd=root,
                ).stdout
            )
            content = evolve_file.read_text(encoding="utf-8")

        self.assertEqual(evolve["id"], "E-1")
        self.assertEqual(accepted["status"], "accepted")
        self.assertIn('status = "accepted"', content)
        self.assertIn("verified = true", content)
        self.assertIn('document_paths = ["README.md"]', content)
        self.assertIn('verified = false\ndocument_paths = ["body.md"]', content)

    def test_check_validates_artifact_identities_and_references(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-check-artifacts-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)
            evolve = {"path": "evolve/E-1-broken-reference.md"}
            (root / "evolve").mkdir()
            (root / evolve["path"]).write_text(
                '+++\nid = "E-1"\nstate = "evolve"\nstatus = "open"\n'
                'title = "Broken reference"\ncreated = "2026-09-05"\n'
                'based_on = ["R-9999"]\n+++\n',
                encoding="utf-8",
            )
            invalid = json.loads(run_cli_unchecked("check", "--json", cwd=root).stdout)
            evolve_file = root / evolve["path"]
            evolve_file.write_text(
                evolve_file.read_text(encoding="utf-8").replace(
                    'id = "E-1"', 'id = "R-1"'
                ),
                encoding="utf-8",
            )
            mismatched = json.loads(
                run_cli_unchecked("check", "--json", cwd=root).stdout
            )

        self.assertRegex("\n".join(invalid["errors"]), r"unknown artifact R-9999")
        self.assertRegex("\n".join(mismatched["errors"]), r"does not match evolve state")

    def test_configuration_paths_cannot_escape_project_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-path-safety-") as directory:
            base = Path(directory)
            root = base / "project"
            root.mkdir()
            run_cli("init", "--json", cwd=root)
            config_file = root / "red.toml"
            config_file.write_text(
                config_file.read_text(encoding="utf-8").replace(
                    'path = "research"', 'path = "../escaped"'
                ),
                encoding="utf-8",
            )

            result = run_cli_unchecked(
                "new", "research", "--title", "Unsafe", "--json", cwd=root
            )
            escaped = (base / "escaped").exists()

        self.assertEqual(result.returncode, 2)
        self.assertFalse(escaped)

    def test_new_rejects_references_to_artifacts_that_do_not_exist(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-reference-safety-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)
            result = run_cli_unchecked(
                "new",
                "evolve",
                "--title",
                "Invalid",
                "--from",
                "R-9999",
                "--json",
                cwd=root,
            )
            evolve_exists = (root / "evolve").exists()

        self.assertEqual(result.returncode, 2)
        self.assertFalse(evolve_exists)

    def test_instructions_refuse_malformed_managed_block_without_changes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-marker-safety-") as directory:
            root = Path(directory)
            agents = root / "AGENTS.md"
            original = "# Existing\n\n<!-- red:start protocol=1 -->\nUser-owned content\n"
            agents.write_text(original, encoding="utf-8")
            result = run_cli_unchecked("instructions", "install", "--json", cwd=root)
            remaining = agents.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 2)
        self.assertEqual(remaining, original)

    def test_promotion_rejects_document_path_outside_project(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-document-safety-") as directory:
            base = Path(directory)
            root = base / "project"
            root.mkdir()
            run_cli("init", "--json", cwd=root)
            research = json.loads(
                run_cli("new", "research", "--title", "Source", "--json", cwd=root).stdout
            )
            evolve = json.loads(
                run_cli("promote", research["id"], "--to", "evolve", "--json", cwd=root).stdout
            )
            (base / "outside.md").write_text("# Outside\n", encoding="utf-8")
            result = run_cli_unchecked(
                "promote",
                evolve["id"],
                "--to",
                "document",
                "--accepted",
                "--verified",
                "--document",
                "docs/../../outside.md",
                "--json",
                cwd=root,
            )
            content = (root / evolve["path"]).read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 2)
        self.assertIn('status = "open"', content)

    def test_renaming_artifact_cannot_cause_identifier_reuse(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-id-safety-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)
            research = json.loads(
                run_cli("new", "research", "--title", "First", "--json", cwd=root).stdout
            )
            (root / research["path"]).rename(root / "research" / "renamed.md")
            result = run_cli_unchecked(
                "new", "research", "--title", "Second", "--json", cwd=root
            )

        self.assertEqual(result.returncode, 2)

    def test_check_enforces_required_configuration_policy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-config-schema-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)
            config_file = root / "red.toml"
            config_file.write_text(
                re.sub(
                    r"\n\[policy\][\s\S]*$",
                    "\n",
                    config_file.read_text(encoding="utf-8"),
                ),
                encoding="utf-8",
            )
            result = run_cli_unchecked("check", "--json", cwd=root)

        self.assertEqual(result.returncode, 1)
        self.assertTrue(
            any("policy" in item for item in json.loads(result.stdout)["errors"])
        )

    def test_mutations_reject_invalid_prospective_metadata_before_writing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-prospective-schema-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)

            empty_title = run_cli_unchecked(
                "new", "research", "--title", "", "--json", cwd=root
            )
            self.assertEqual(empty_title.returncode, 2)
            self.assertFalse((root / "research").exists())

            source = json.loads(
                run_cli("new", "research", "--title", "Source", "--json", cwd=root).stdout
            )
            duplicate_reference = run_cli_unchecked(
                "new", "evolve", "--title", "Duplicate", "--from",
                source["id"], source["id"], "--json", cwd=root
            )
            self.assertEqual(duplicate_reference.returncode, 2)
            self.assertFalse((root / "evolve").exists())

            evolve = json.loads(
                run_cli("promote", source["id"], "--to", "evolve", "--json", cwd=root).stdout
            )
            (root / "README.md").write_text("# Project\n", encoding="utf-8")
            duplicate_document = run_cli_unchecked(
                "promote", evolve["id"], "--to", "document", "--accepted", "--verified",
                "--document", "README.md", "README.md", "--json", cwd=root
            )
            self.assertEqual(duplicate_document.returncode, 2)
            self.assertIn(
                'status = "open"', (root / evolve["path"]).read_text(encoding="utf-8")
            )

    def test_identifier_allocation_crosses_four_digits(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-unbounded-id-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)
            (root / "research").mkdir()
            (root / "research" / "R-9999-last.md").write_text(
                '+++\nid = "R-9999"\nstate = "research"\nstatus = "open"\n'
                'title = "Last"\ncreated = "2026-09-06"\n+++\n',
                encoding="utf-8",
            )

            created = json.loads(
                run_cli(
                    "new", "research", "--title", "Beyond four digits", "--json", cwd=root
                ).stdout
            )

        self.assertEqual(created["id"], "R-10000")
        self.assertEqual(created["path"], "research/R-10000-beyond-four-digits.md")

    def test_check_rejects_calendar_invalid_creation_dates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="red-python-date-schema-") as directory:
            root = Path(directory)
            run_cli("init", "--json", cwd=root)
            (root / "research").mkdir()
            (root / "research" / "R-1-impossible.md").write_text(
                '+++\nid = "R-1"\nstate = "research"\nstatus = "open"\n'
                'title = "Impossible"\ncreated = "2026-02-31"\n+++\n',
                encoding="utf-8",
            )
            result = run_cli_unchecked("check", "--json", cwd=root)

        self.assertEqual(result.returncode, 1)
        self.assertTrue(
            any(
                item.startswith("RED_SCHEMA_FORMAT ") and item.endswith("/created")
                for item in json.loads(result.stdout)["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
