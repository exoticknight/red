# RED Agent Instructions

This project uses RED Protocol 1 to separate unresolved research, ongoing change, and accepted project knowledge.

## Knowledge states

### Research

Research contains unresolved questions, evidence, hypotheses, experiments, and conflicting claims. Do not treat it as accepted requirements.

### Evolve

Evolve contains proposed or active changes, their rationale, affected areas, acceptance conditions, and open questions. Preserve unresolved alternatives until the user or project policy decides them.

### Document

Document contains accepted project goals, terminology, interfaces, architecture rules, operating instructions, and contribution rules. Treat it as the normative baseline.

Code, tests, configuration, and runtime output provide implementation evidence. Report conflicts with Document and investigate them through Research. A resulting decision may repair the implementation or create an Evolve item that changes Document.

## Workflow

1. Read repository instructions and `red.toml` when present.
2. Load only the Document, active Evolve, Research, and implementation evidence relevant to the task.
3. Implement directly when accepted knowledge specifies the work.
4. Use Research when an unknown can change the decision. Report findings and wait for explicit authority before entering Evolve.
5. Use Evolve when the task changes accepted behavior, data, public interfaces, architecture, or engineering rules. A clear change may enter Evolve directly.
6. Design, implement, test, and revise inside the authorized Evolve scope.
7. When acceptance conditions pass, report evidence and proposed Document changes. Wait for separate acceptance before updating Document.
8. Persist R or E when work crosses tasks, needs review, presents alternatives, or leaves an unresolved conflict.
9. Run `red check --json` when the CLI is available.

Prefer the RED CLI for deterministic operations. If it is unavailable, follow the same protocol by hand. CLI promotion records a decision supplied by the user or project; it does not authorize the transition. Follow the project's version-control policy for Research and Evolve; RED does not require tracked files, local files, or an external tracker. Do not reorganize existing documentation or install tools globally without authorization.
