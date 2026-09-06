# Work with RED

Use this loop for engineering tasks.

## Discover

Locate the project root, repository instructions, `red.toml`, relevant Document sources, active Evolve items, and implementation evidence.

## Ground

Build the smallest useful context. Mark each input as Document, Evolve, Research, or implementation evidence. Do not load unrelated project history.

## Route

- Implement directly when accepted Document or an active Evolve item specifies the work and no decision-blocking unknown remains.
- Enter Research when an unknown can change the implementation or acceptance criteria.
- Enter Evolve when the task changes accepted behavior, a public interface, data, architecture, or an engineering rule.
- Investigate a Document/evidence conflict through Research before updating either side.

A clear feature request may enter Evolve without a separate Research artifact. A bug that violates existing Document may move from diagnosis to a direct repair without changing Document.

Route work by knowledge state instead of a required R-to-E-to-D sequence. The user's current request may authorize direct entry to Evolve when it already defines the change and its boundary.

## Persist

Create an artifact only when the persistence criteria in `protocol.md` apply. Use the CLI when available. Otherwise follow `artifacts.md` by hand.

Follow the project's storage and version-control policy. Do not treat artifact creation as authorization to stage or publish it.

## Research checkpoint

Investigate inside Research. When the evidence supports a proposed Evolve scope, report the findings, remaining uncertainty, risks, and proposed scope. Stop there unless the user or a project-authorized decision source explicitly advances the work to Evolve.

## Evolve loop and acceptance checkpoint

Design, implement, test, revise, and resolve tradeoffs inside the authorized Evolve scope. Ask for a new decision when work would expand that scope.

When acceptance conditions pass, report the implementation evidence and proposed Document changes. Stop there unless the user or a project-authorized decision source explicitly accepts the result. Then update Document and record the promotion. Do not treat the request that started Research or Evolve as advance acceptance of a result the user had not seen.
