# RED Protocol 1

This document is the normative definition of RED Protocol 1. The methodology paper explains the model; this specification defines interoperable project behavior.

## Knowledge states

### Research

Research contains unresolved questions, observations, external evidence, hypotheses, experiments, and conflicts. Its claims are not accepted requirements. A Research artifact uses an `R-<positive integer>` identifier and may reference other artifacts.

### Evolve

Evolve contains a proposed or active change: its rationale, affected area, acceptance conditions, alternatives, and open questions. An Evolve artifact uses an `E-<positive integer>` identifier. Its `based_on` field makes supporting Research or prior Evolve work explicit.

### Document

Document contains accepted project goals, terminology, interfaces, architecture, operating instructions, and contribution rules. Document is a logical classification over the repository's normal documentation; it is not a required directory.

Code, tests, configuration, and runtime behavior are implementation evidence, not automatically Document. A conflict between Document and evidence becomes Research until an authorized decision either repairs the implementation or changes Document through Evolve.

## Project declaration

A project may declare Protocol 1 with a root `red.toml` conforming to [config-schema.json](config-schema.json). Without this file, a RED-capable agent may apply the state distinctions from repository context, but deterministic CLI operations that require path mapping must not guess.

`document.paths` lists files or directory trees ending in `/**`. Research and Evolve each declare one artifact directory. Paths are repository-relative.

## Artifacts

Research and Evolve artifacts are UTF-8 Markdown with TOML front matter delimited by `+++` lines. Metadata conforms to [artifact-schema.json](artifact-schema.json). Required fields are:

| Field | Type | Rule |
|---|---|---|
| `id` | string | `R-<positive integer>` for Research; `E-<positive integer>` for Evolve |
| `state` | string | `research` or `evolve`, matching its configured directory |
| `status` | string | Initially `open`; accepted Evolve is `accepted` |
| `title` | string | Non-empty human-readable title |
| `created` | local date | Creation date |

`based_on` is an optional array of existing artifact identifiers. Accepted Evolve records `verified = true` and `document_paths`, an array of existing paths declared by `document.paths`.

New identifiers use sequential positive decimal integers without leading zeros and are unique within each state. Readers and validators also accept legacy four-digit, zero-padded identifiers such as `R-0001` and `E-0001`. Allocation considers both forms, emits the unpadded form, imposes no fixed digit width, and promotion retains the source artifact.

## Transitions

- RED does not prescribe one mandatory sequence. A clear, authorized change may enter Evolve directly. Research is needed when an unresolved question can change the decision or its acceptance conditions.
- Once work enters Research, an agent presents its findings and waits at the Research checkpoint. Research to Evolve requires an explicit human decision or a decision source that the project has authorized. The Evolve artifact references the Research identifier.
- Evolve includes design, implementation, tests, revision, and the interaction needed to resolve tradeoffs inside the authorized scope.
- Once Evolve meets its acceptance conditions, the agent presents the verification evidence and proposed Document changes, then waits at the acceptance checkpoint. Evolve to Document requires a separate explicit acceptance and synchronization with the relevant Document sources.
- Rejected Evolve leaves Document unchanged.
- Partial acceptance records the accepted boundary and synchronizes only that boundary.

An agent must not infer a later transition from a broad request that started the work before the transition was ready for review. A project may delegate transition authority through a defined process such as an approved issue state or pull-request review.

The CLI may create and validate artifacts and record a supplied decision. For Evolve-to-Document promotion, `--accepted` and `--verified` are caller assertions: the CLI checks them and the target paths, but cannot judge the decision source or the semantic quality of the verification. CLI flags record authority; they do not create it. The CLI must not invent acceptance or author substantive Document content.

## Persistence

RED classifies knowledge in every task but does not require an artifact for every thought. Persist Research or Evolve when work crosses tasks, needs review, contains consequential alternatives, changes public behavior or architecture, or leaves a conflict unresolved.

A clear change may enter Evolve directly. Research is required only when an unresolved question can change the decision or its acceptance conditions.

Persistence does not prescribe a version-control policy. A project may track Research and Evolve files, keep them local, or publish them through an issue tracker or another collaboration system. The project must define that choice. Research and Evolve retain their working-state semantics even when tracked; version control does not promote them to Document.

## Compatibility

Protocol versions are integers. An implementation must stop mutating a project whose version it does not support. Release versions of tools and Skill snapshots do not change the project protocol unless the protocol contract changes incompatibly.
