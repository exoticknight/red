# Architecture

RED separates a human/agent protocol from deterministic tooling.

## Boundaries

- `spec/` owns the protocol contract.
- `plugins/red/skills/red` is the canonical Skill source and manual fallback.
- `.agents/skills/red` is an ignored, CLI-managed installation used to run RED on this repository.
- `cli/node` and `cli/python` implement deterministic operations independently.
- `cli/conformance` is the executable compatibility boundary shared by both implementations.
- Release scripts copy the canonical Skill into each package; generated copies are not edited.

The plugin is skills-only. Host presentation metadata stays in `plugins/red/.codex-plugin/plugin.json`; `SKILL.md` stays portable.

## Dependency decisions

The Node CLI uses Commander for the command surface, smol-toml for TOML parsing and writing, and Ajv for Protocol JSON Schema validation. smol-toml's lossless BigInt mode preserves legal TOML integers until the shared schema range is checked. These maintained libraries avoid custom argument, TOML, and schema implementations. The package requires Node 22.12 or newer because that is the stricter runtime floor of its dependency set.

The Python CLI uses `argparse` and `tomllib` from the supported Python standard library and jsonschema for Protocol validation. Its narrow TOML emission is limited to RED-owned templates rather than acting as a general parser.

Repository validation uses PyYAML and jsonschema instead of custom YAML or JSON Schema implementations. Python packaging uses the PyPA `build` frontend with Hatchling as the backend.

Separate Node and Python implementations are intentional distribution boundaries. Observable parity is enforced by shared fixtures rather than shared runtime code, so each package remains native and independently installable.

## Safety boundaries

Initializers and standalone exports use create-only writes. Skill update/uninstall operates only on a directory carrying RED-owned installation metadata. Instructions install/uninstall changes only the marked block. Unsupported protocol versions block mutations.

Research and Evolve directories are workspace state, not distribution inputs or accepted documentation. This repository ignores them in Git and uses issues or pull requests for shared review. Other projects choose their own storage and version-control policy. The CLI validates artifacts present in a working copy regardless of that choice.

The Skill owns state routing and conversational checkpoints. The CLI creates templates, validates structure, and records decisions supplied by a human or project-authorized process. It cannot determine whether a decision has authority, so an agent must not treat successful CLI execution as approval.

The repository tracks one Skill tree under the plugin. Release synchronization copies that source into ignored Node and Python package trees. A maintainer may install the synchronized snapshot into the ignored `.agents` directory for local self-hosting. Repository validation checks the local installation when it exists; a clean CI checkout does not require one.
