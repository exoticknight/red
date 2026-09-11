# RED

[![Maintained with RED](https://img.shields.io/badge/maintained_with-RED-C1121F?style=for-the-badge)](red.toml)
[![GitHub](https://img.shields.io/badge/GitHub-exoticknight%2Fred-181717?style=for-the-badge&logo=github)](https://github.com/exoticknight/red)

> **RED runs on RED.** This repository uses the same Research → Evolve → Document protocol that it ships. Open questions stay visible, changes carry their rationale, and accepted decisions live in the project’s normal documentation.

RED is a project-knowledge methodology for AI-assisted engineering. It keeps three kinds of knowledge distinct:

- **Research:** unresolved questions, evidence, hypotheses, and conflicts.
- **Evolve:** proposed or active changes, with rationale and acceptance conditions.
- **Document:** accepted project knowledge, including goals, interfaces, architecture, and operating rules.

The distinction matters because an agent should not turn a research note into a requirement, or treat a proposal as accepted behavior. Source code, tests, configuration, and runtime output remain implementation evidence; when they conflict with Document, RED routes the conflict through Research instead of silently choosing a winner.

## Methodology

- [Introducing RED: A Methodology for AI Understanding](methodology/introducing-red.md): the original paper, motivation, and conceptual model.
- [RED Protocol 1](spec/protocol.md): the normative definitions, artifact rules, and transition semantics.
- [Adoption guide](docs/adoption.md): delivery forms and guidance for adding RED to an existing project.

## This repository runs on RED

RED maintains itself as a RED Protocol 1 project. The root [`red.toml`](red.toml) maps accepted documentation and the local `research/` and `evolve/` workspaces. [`plugins/red/skills/red`](plugins/red/skills/red) is the only tracked Skill source. Maintainers install its release-matched snapshot into the ignored `.agents/skills/red` directory when working on RED itself.

Changes to RED's public behavior, protocol, architecture, or release policy begin in Evolve. Decision-blocking unknowns go to Research; clear changes do not pass through Research as a ritual. When Research produces an actionable scope, the agent reports its findings and waits for a maintainer to authorize Evolve. Evolve includes design, implementation, tests, and revision. Once its acceptance conditions pass, the agent reports the evidence and waits for a separate acceptance before updating Document.

This repository keeps Research and Evolve files out of Git and uses issues or pull requests when contributors need to share working state. Other RED projects choose their own version-control policy. CI runs `red check --json` against the checked-out project configuration.

Install the self-hosted Skill on a fresh checkout with one of the commands under [Install the Skill](#install-the-skill). During release development, synchronize the package trees before using the source CLI:

```sh
python scripts/sync_distribution.py
# Fresh checkout
node cli/node/src/cli.js skill install --scope repo --json
# Existing installation after a Skill change
node cli/node/src/cli.js skill update --scope repo --json
```

Git ignores the installed snapshot, so the repository maintains one tracked Skill source.

## Choose the smallest form

| Project situation | Recommended form |
|---|---|
| Normal use, deterministic project operations available | RED Skill + RED CLI |
| Strong agent, offline environment, or no Node/Python runtime | RED Skill only |
| Existing project that cannot add a Skill | Managed block in `AGENTS.md` |
| Agent reads standalone instructions but not Skills | `RED.md` |

There is one RED Skill. Its internal modes cover engineering work, adoption, inspection, artifact handling, and CLI fallback. `red.toml` is optional until a project needs explicit, machine-readable path and policy mapping.

## Install the Skill

Use either distribution as a one-shot runner. Both install the same Skill snapshot:

```sh
npx -y @exoticknight/red-cli@latest skill install --scope repo
```

```sh
pipx run --spec red-cli red skill install --scope repo
```

Repository scope writes `.agents/skills/red`; user scope writes the corresponding user-level `.agents/skills/red`. The installer records its release and protocol in `.red-install.json`, enabling safe status, update, and uninstall operations.

The one-shot commands run the CLI to install the Skill; they do not install a permanent `red` command. For regular CLI use, install either distribution:

```sh
npm install -g @exoticknight/red-cli
# Or, with Python:
pipx install red-cli
```

Both expose `red`. Run `red skill install --scope repo` from the target project to install the Skill, then `red init` when explicit project configuration is needed. After upgrading the CLI package, run `red skill update --scope repo` to update an existing managed Skill installation.

For lightweight adoption:

```sh
npx -y @exoticknight/red-cli@latest instructions install --target AGENTS.md
npx -y @exoticknight/red-cli@latest instructions export --output RED.md
```

The `AGENTS.md` command owns only a marked block and preserves the rest of the file.

## Initialize a project

```sh
red init
red new research --title "Unknown cache behavior"
red new evolve --title "Change cache policy" --from R-1
red check --json
red status --json
```

`red init` creates `red.toml`; edit its paths to match the repository instead of moving existing documentation into a RED-specific directory.

The commands manage files and validation; they do not define an automatic R-to-E-to-D pipeline. After Research, the agent presents its findings and waits for authorization to enter Evolve. After Evolve passes its acceptance conditions, the agent presents verification evidence and waits for acceptance before updating Document. Clear, authorized work may begin in Evolve without Research.

Promotion records an explicit decision:

```sh
red promote R-1 --to evolve --title "Adopt cache policy"
red promote E-1 --to document --accepted --verified --document README.md
```

The second command requires the caller to assert acceptance and verification, checks that the declared Document exists, and records synchronization on the Evolve artifact. The flags record a decision already made by a human or project-authorized process. They never create that authority, and the CLI never writes the substantive Document change itself.

Implementation details live in the [CLI contract](spec/cli-interface.md), [architecture](docs/architecture.md), and [release process](docs/releasing.md).

## Repository layout

```text
cli/
  node/                 npm distribution
  python/               PyPI distribution
  conformance/          shared cross-implementation fixtures
plugins/red/            skills-only Codex plugin
methodology/             original methodology paper
spec/                   normative protocol and machine-readable contracts
docs/                   accepted project documentation
scripts/                validation and release tooling
```

## Versioning and license

Release tags use `vMAJOR.MINOR.PATCH`. The npm package, Python package, plugin archive, and Skill snapshot share that release version. Protocol compatibility is versioned separately by `red.toml`'s `version` field; the Skill does not carry an independent version number.

RED is licensed under the [Apache License 2.0](LICENSE).
