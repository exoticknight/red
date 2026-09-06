# Adoption guide

RED does not require reorganizing an existing repository.

## Full form

Use the RED Skill plus either CLI when agents can load Skills and a Node or Python runner is available. Install the Skill at repository scope so every compatible agent sees the same instructions, then run `red init` and edit `red.toml` to map the existing docs and artifact directories.

Repository scope selects the agent discovery path; it does not select a Git policy. A project may track `.agents/skills/red` to distribute the installed Skill with the repository or generate it in each checkout and ignore it. Keep a separate canonical source when the project publishes the Skill itself.

Do not reconstruct historical Research or Evolve records. Classify current maintained sources and apply RED from the adoption point forward.

Choose how the project shares Research and Evolve. It may track the files, keep them local, or use issues and pull requests. Record the choice in existing repository guidance or ignore rules so agents do not infer it from RED. Tracking an artifact does not make it Document.

## Working flow

Route work by its current knowledge state. A clear request with defined acceptance conditions may enter Evolve directly. Use Research when an unknown can change the decision or its acceptance conditions.

When Research supports an actionable scope, the agent presents its findings and waits for a human or project-authorized decision before entering Evolve. Design, implementation, tests, and revision take place inside Evolve. Once the acceptance conditions pass, the agent presents the evidence and proposed Document changes, then waits for a separate acceptance before updating Document. CLI promotion flags record those decisions; they do not grant authority.

## Skill-only form

Use the Skill without a CLI in offline, restricted, or runtime-free environments. The agent follows the same protocol and artifact templates manually. Deterministic identifier allocation and structural validation are weaker, so concurrent artifact creation needs extra care.

## Lightweight bridge

For a legacy project or a host without Skill support, install the managed RED block into `AGENTS.md`. This adds the state distinction and workflow without replacing existing instructions. Export `RED.md` when the host can load a standalone project instruction file.

`red.toml` is not required for the lightweight bridge. Add it only when the project wants explicit path mapping or CLI-backed operations.

## Selection rule

Start with the smallest form the host can reliably consume. Prefer Skill + CLI when both are available; degrade to Skill only, then to a managed instructions block or `RED.md`. These are delivery forms for one protocol, not four competing methodologies.
