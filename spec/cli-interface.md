# CLI interface

The npm and PyPI distributions expose the same `red` command and JSON semantics.

| Command | Effect |
|---|---|
| `version` | Report release and protocol versions |
| `init` | Create `red.toml`; fail if it already exists |
| `new research` | Create the next Research artifact |
| `new evolve` | Create the next Evolve artifact, optionally with `--from` references |
| `promote R-N --to evolve` | Create an Evolve artifact referencing the Research source |
| `promote E-N --to document --accepted --verified` | Validate the caller's explicit assertions and supplied Document paths, then record acceptance/synchronization |
| `status` | Count mapped Document, Evolve, and Research files |
| `check` | Validate configuration, artifact identities, duplicates, and references |
| `skill install/status/update/uninstall` | Manage the release-matched RED Skill at repository or user scope |
| `instructions install/uninstall` | Manage only the marked RED block in an instructions file |
| `instructions export` | Create a standalone `RED.md` |

Commands that return data accept `--json`. JSON objects conform to [output-schema.json](output-schema.json). Paths in output use `/` separators even on Windows.

`skill update` and `skill uninstall` require `.red-install.json` with `distribution: "red"`; they refuse to alter an unmanaged directory. `instructions uninstall` similarly removes only the marked block.

## One-shot execution

```sh
npx -y @exoticknight/red@latest <command>
pipx run --spec red-methodology red <command>
```

Agents should prefer an existing project-local or user-installed `red`. A Skill may try one approved, network-backed one-shot runner when no CLI exists, then continue manually if unavailable. It must not add dependencies or install globally without authorization.

The CLI performs deterministic file operations and structural checks. It does not decide that Research may enter Evolve or that Evolve may enter Document. An agent invokes `promote` only after a human or a project-authorized decision source supplies that transition. The `--accepted` and `--verified` flags record caller assertions; an agent must not set them from its own assessment alone.
