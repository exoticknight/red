---
name: red
description: Manage project knowledge and engineering changes with Research, Evolve, and Document. Use when the user requests RED, or when a repository declares RED through red.toml, RED.md, or AGENTS.md. Do not impose RED on undeclared projects.
metadata:
  red-protocol: "1"
---

# RED

Keep accepted project knowledge separate from unresolved research and ongoing change.

## Invariants

- Treat Document as the normative project baseline.
- Treat Research as unverified evidence, claims, and open questions.
- Treat Evolve as proposed or ongoing change, not accepted behavior.
- Treat code, tests, configuration, and runtime output as implementation evidence.
- Report conflicts between Document and implementation evidence. Investigate the conflict before choosing a side.
- Never promote knowledge between states without a decision that the user or project policy authorizes.
- Do not force work through Research when the change and its acceptance conditions are clear.
- At a Research or Evolve boundary, report the reviewable result and wait for a separate authorized transition. Do not infer a later transition from a broad request made before that result existed.
- Preserve the project's existing documentation structure. RED classifies knowledge; it does not require a `.red` directory.
- Keep small, resolved work in the current task. Persist R or E when another task, person, or agent will need it.
- Follow the project's version-control policy for Research and Evolve. Do not infer that RED requires tracked files, local files, or an external tracker.

## Discover the project

1. Follow repository instructions, including every applicable `AGENTS.md`.
2. Read `red.toml` when present and use its paths.
3. Without `red.toml`, identify likely Document sources such as README, maintained docs, accepted ADRs, public interfaces, and contribution rules.
4. Read only the Document, active Evolve, Research, and implementation evidence relevant to the task.
5. Do not create `red.toml` unless the user asks to adopt or initialize RED, or deterministic RED operations need an explicit mapping.

## Route the request

- For ordinary engineering work, read [work.md](references/work.md).
- For first-time or brownfield adoption, read [adopt.md](references/adopt.md).
- For project health checks, read [inspect.md](references/inspect.md).
- Before creating or promoting an artifact, read [artifacts.md](references/artifacts.md).
- When using, enabling, or falling back from the CLI, read [cli.md](references/cli.md).
- For an unfamiliar edge case, consult [scenarios.md](references/scenarios.md).

## Finish the task

Before reporting completion:

- Verify that no Research claim became an accepted requirement by accident.
- Preserve unresolved alternatives in Evolve.
- When Research is ready for a decision, report findings and wait before entering Evolve.
- When Evolve is ready for acceptance, report verification evidence and proposed Document changes, then wait before updating Document.
- Synchronize behavior with the relevant Document sources only after acceptance.
- Report remaining conflicts and unknowns.
- Run `red check --json` when the CLI is available. State when you could not run it.
