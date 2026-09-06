"""Run the shared protocol fixture against both CLI distributions."""

from __future__ import annotations

import json
import difflib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date


REPOSITORY = Path(__file__).resolve().parents[2]
CONFORMANCE = Path(__file__).resolve().parent
NODE_CLI = REPOSITORY / "cli" / "node" / "src" / "cli.js"
PYTHON_SOURCE = REPOSITORY / "cli" / "python" / "src"


def run(command: list[str], root: Path, environment: dict[str, str]) -> tuple[int, object, str]:
    result = subprocess.run(
        command,
        cwd=root,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        output: object = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = result.stdout
    return result.returncode, output, result.stderr


def tree(root: Path, allowed_dates: set[str]) -> dict[str, str]:
    def normalize_created_dates(content: str) -> str:
        def replace(match: re.Match[str]) -> str:
            created = match.group(1)
            if created not in allowed_dates:
                raise AssertionError(
                    f"{root}: generated non-local date {created}; expected one of "
                    f"{sorted(allowed_dates)}"
                )
            return 'created = "<date>"'

        return re.sub(
            r'(?m)^created = "(\d{4}-\d{2}-\d{2})"$',
            replace,
            content,
        )

    return {
        file.relative_to(root).as_posix(): normalize_created_dates(
            file.read_text(encoding="utf-8").replace("\r\n", "\n")
        )
        for file in sorted(root.rglob("*"))
        if file.is_file()
    }


def main() -> int:
    start_date = date.today().isoformat()
    specification = json.loads((CONFORMANCE / "cases.json").read_text(encoding="utf-8"))
    fixture = CONFORMANCE / "fixtures" / "existing-project"
    with tempfile.TemporaryDirectory(prefix="red-conformance-") as temporary:
        temporary_root = Path(temporary)
        roots = {"node": temporary_root / "node", "python": temporary_root / "python"}
        for root in roots.values():
            shutil.copytree(fixture, root)

        environments = {"node": os.environ.copy(), "python": os.environ.copy()}
        environments["python"]["PYTHONPATH"] = str(PYTHON_SOURCE)
        prefixes = {
            "node": [shutil.which("node") or "node", str(NODE_CLI)],
            "python": [sys.executable, "-m", "red_cli.cli"],
        }

        def assert_invalid_config(content: str, expected_error: str) -> None:
            for root in roots.values():
                (root / "red.toml").write_text(content, encoding="utf-8")
            invalid_results = {
                implementation: run(
                    prefixes[implementation] + ["check", "--json"],
                    roots[implementation],
                    environments[implementation],
                )
                for implementation in ("node", "python")
            }
            if invalid_results["node"][:2] != invalid_results["python"][:2]:
                raise AssertionError(
                    "invalid-schema output mismatch\n"
                    f"node={invalid_results['node'][:2]}\n"
                    f"python={invalid_results['python'][:2]}"
                )
            invalid_code, invalid_output, _ = invalid_results["node"]
            if invalid_code != 1 or not isinstance(invalid_output, dict):
                raise AssertionError(f"invalid schema returned {invalid_results['node']}")
            if expected_error not in invalid_output.get("errors", []):
                raise AssertionError(f"missing normalized schema error: {invalid_output}")

        for index, case in enumerate(specification["cases"], start=1):
            results = {
                implementation: run(
                    prefixes[implementation] + case["args"],
                    roots[implementation],
                    environments[implementation],
                )
                for implementation in ("node", "python")
            }
            for implementation, result in results.items():
                if result[0] != case["exitCode"]:
                    raise AssertionError(
                        f"case {index} {implementation} exited {result[0]}: {result[2]}"
                    )
            if results["node"][:2] != results["python"][:2]:
                raise AssertionError(
                    f"case {index} output mismatch\n"
                    f"node={results['node'][:2]}\npython={results['python'][:2]}"
                )

        allowed_dates = {start_date, date.today().isoformat()}
        node_tree = tree(roots["node"], allowed_dates)
        python_tree = tree(roots["python"], allowed_dates)
        if node_tree != python_tree:
            differing = sorted(set(node_tree) | set(python_tree))
            details = [name for name in differing if node_tree.get(name) != python_tree.get(name)]
            differences = []
            for name in details:
                differences.extend(
                    difflib.unified_diff(
                        node_tree.get(name, "").splitlines(),
                        python_tree.get(name, "").splitlines(),
                        fromfile=f"node/{name}",
                        tofile=f"python/{name}",
                        lineterm="",
                    )
                )
            raise AssertionError(
                f"final filesystem mismatch: {', '.join(details)}\n" + "\n".join(differences)
            )

        # Schema-engine diagnostics are normalized by the RED Protocol. Exercise
        # an invalid document outside the happy-path fixture so backend wording
        # cannot drift between Ajv and jsonschema.
        valid_config = (roots["node"] / "red.toml").read_text(encoding="utf-8")
        config_without_policy = re.sub(
            r"\n\[policy\][\s\S]*$",
            "\n",
            valid_config,
        )
        assert_invalid_config(
            config_without_policy, "RED_SCHEMA_REQUIRED red.toml/policy"
        )
        assert_invalid_config("", "RED_SCHEMA_REQUIRED red.toml/version")
        assert_invalid_config(
            "version = true\n", "RED_SCHEMA_TYPE red.toml/version"
        )
        assert_invalid_config(
            valid_config.replace("version = 1", "version = 2.0", 1),
            "Unsupported RED protocol; expected 1",
        )
        assert_invalid_config(
            valid_config.replace(
                "version = 1", "version = 9007199254740993", 1
            ),
            "RED_SCHEMA_MAXIMUM red.toml/version",
        )
        assert_invalid_config(
            valid_config.replace(
                "version = 1", '"version" = 9007199254740993', 1
            ),
            "RED_SCHEMA_MAXIMUM red.toml/version",
        )
        assert_invalid_config(
            valid_config.replace(
                "version = 1", "version = 9_007_199_254_740_993", 1
            ),
            "RED_SCHEMA_MAXIMUM red.toml/version",
        )
        assert_invalid_config(
            valid_config.replace(
                "version = 1", "version = 0x20000000000001", 1
            ),
            "RED_SCHEMA_MAXIMUM red.toml/version",
        )
        assert_invalid_config(
            valid_config.replace("version = 1", "version = 1e100", 1),
            "RED_SCHEMA_MAXIMUM red.toml/version",
        )

    print(f"RED Protocol {specification['protocolVersion']} conformance passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
