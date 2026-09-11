# RED CLI

Prefer the CLI for configuration, identifiers, templates, installation, status, and structural checks.

## Detection and enablement

1. Use an existing `red` executable.
2. In a Node project, try the project-local package or the official pinned `npx` package.
3. In a Python project, try the installed package or the official pinned `pipx` runner.
4. Make at most one network-backed attempt in a task. Follow the host's approval rules.
5. Do not install globally or change project dependencies unless the user asks.
6. Continue by hand when the CLI is unavailable, incompatible, declined, or offline.

## Commands

```text
red init
red new research --title <title>
red new evolve --title <title> [--from <id>]
red status --json
red check --json
red promote <artifact> --to evolve
red promote <artifact> --to document --accepted --verified --document <path>
red skill install [--scope user|repo]
red skill status [--scope user|repo]
red skill update [--scope user|repo]
red skill uninstall [--scope user|repo]
red instructions install --target AGENTS.md
red instructions uninstall --target AGENTS.md
red instructions export --output RED.md
```

One-shot forms:

```text
npx -y @exoticknight/red@latest <command>
pipx run --spec red-methodology red <command>
```

The CLI installs the Skill snapshot shipped in its own release. Use `skill status` to inspect `.red-install.json` and `skill update` to replace only an installation managed by RED.

The CLI handles structure, not transition authority. Invoke Research-to-Evolve promotion only after the user or a project-authorized decision source approves the proposed scope. Pass `--accepted` and `--verified` only after Evolve evidence has been presented and the result has received separate acceptance. A successful command records those supplied assertions; it does not prove that the decision occurred.

Use `--json` when consuming command output. Protocol incompatibility is a hard stop for CLI mutation; fall back to manual work under the protocol supported by the project.
