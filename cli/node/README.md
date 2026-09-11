# RED: Research, Evolve, Document

Keep your AI collaborator grounded in what your project has agreed, what is changing, and what still needs investigation.

RED is a methodology for maintaining project knowledge across AI conversations. Use it when an agent confuses an old idea with a current requirement, loses the reasoning behind a design, or leaves you with discussions that never turn into decisions and working changes.

**Read the paper:** [English](https://github.com/exoticknight/red/blob/main/methodology/introducing-red.en.md) · [中文](https://github.com/exoticknight/red/blob/main/methodology/introducing-red.md)

## How RED works

| State | What belongs here | How you use it |
|---|---|---|
| **Research** | Evidence, hypotheses, unknowns, and conflicting information | Investigate questions that could change a decision |
| **Evolve** | Proposed changes, alternatives, implementation, and acceptance evidence | Develop and review a change before accepting it |
| **Document** | Accepted goals, behavior, interfaces, and engineering rules | Give people and agents a shared baseline for current work |

Start a task from the relevant Document sources and implementation evidence. Investigate decision-blocking unknowns in Research; a clear change can enter Evolve directly. Review the result before updating Document. Keep small, resolved work in the task; preserve R/E records when work needs handoff, review, or further investigation. Your project chooses whether those records live in Git, local files, issues, or pull requests.

## What this package provides

- **The RED Skill:** instructions that guide a compatible agent through investigation, implementation, review, and documentation. It includes references and artifact templates.
- **The `red` CLI:** project configuration, artifact identifiers, structural checks, Skill installation and updates, and instruction-file management.

The Skill guides the agent's work. The CLI manages files and records decisions you authorize. People or a project-authorized decision process approve transitions; passing a check does not accept a proposal. When code or runtime evidence conflicts with Document, investigate the discrepancy before changing the baseline.

This npm package and the [Python distribution](https://pypi.org/project/red-methodology/) provide the same command contract and Skill snapshot. Choose the runtime you already use.

## Install the Skill

Requires **Node.js 22.12 or later** and npm. From your project directory:

```sh
npx -y @exoticknight/red@latest skill install --scope repo
```

This installs the Skill into `.agents/skills/red`. Use a host that discovers Skills there, and ask the agent to use RED for the project. `--scope user` installs into your user-level `.agents/skills/red` instead. Repository scope selects the discovery location; your project decides whether to track or generate the installed files.

The one-shot command runs the installer without adding a permanent `red` executable to your PATH. For regular CLI use:

```sh
npm install -g @exoticknight/red
red version
```

## Start using RED

After installing the CLI, run these commands from the target project:

```sh
red init
# Edit red.toml to map your existing documentation and R/E locations.
red check --json
red status --json
```

`red init` creates `red.toml` and refuses to overwrite an existing configuration. Map the documentation you already maintain; no repository reorganization is required. The Skill can also work without the CLI or configuration when the agent can identify the project's knowledge sources.

Ask your agent, for example:

> Use RED to add CSV export. Read the existing requirements, investigate unknowns that affect the design, and show me the implementation and proposed documentation before acceptance.

When an investigation or change needs its own record:

```sh
red new research --title "Clarify CSV compatibility requirements"
red new evolve --title "Add CSV export"
```

These create records in the configured locations. Continue design, implementation, tests, and revision within the agreed scope. At review, the agent presents evidence and the proposed Document update. After acceptance, it synchronizes the maintained documentation. See the [CLI contract](https://github.com/exoticknight/red/blob/main/spec/cli-interface.md) for promotion commands and JSON output.

## Update or remove the Skill

Upgrade the CLI package first, then update the Skill snapshot it carries:

```sh
npm install -g @exoticknight/red@latest
red skill status --scope repo
red skill update --scope repo
```

For one-shot use, run `npx -y @exoticknight/red@latest skill update --scope repo`. Replacing the runner alone does not update an installed Skill.

```sh
red skill uninstall --scope repo
```

Update and uninstall use the installer's `.red-install.json` metadata and refuse to alter an unmanaged Skill directory.

## Hosts without Skill support

Use a managed block in an existing `AGENTS.md`, or export standalone instructions:

```sh
npx -y @exoticknight/red@latest instructions install --target AGENTS.md
npx -y @exoticknight/red@latest instructions export --output RED.md
```

The managed block preserves the rest of `AGENTS.md`. Choose the instruction form your host reads; see the [adoption guide](https://github.com/exoticknight/red/blob/main/docs/adoption.md).

## Learn more

- [Paper: English](https://github.com/exoticknight/red/blob/main/methodology/introducing-red.en.md) · [论文：中文](https://github.com/exoticknight/red/blob/main/methodology/introducing-red.md)
- [RED Protocol 1](https://github.com/exoticknight/red/blob/main/spec/protocol.md)
- [Source and contribution guide](https://github.com/exoticknight/red)
- [Report an issue](https://github.com/exoticknight/red/issues)
- [Releases, standalone Skill, and plugin archives](https://github.com/exoticknight/red/releases)

Licensed under [Apache-2.0](https://github.com/exoticknight/red/blob/main/LICENSE).
