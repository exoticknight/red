# RED artifacts

Use UTF-8 Markdown with TOML front matter delimited by `+++`.

## Research

```md
+++
id = "R-1"
state = "research"
status = "open"
title = "Tag semantics"
created = "2026-09-05"
+++

# R-1: Tag semantics

## Question

## Evidence

## Unknowns
```

## Evolve

```md
+++
id = "E-1"
state = "evolve"
status = "open"
title = "Add tags"
created = "2026-09-05"
based_on = ["R-1"]
+++

# E-1: Add tags

## Change

## Rationale

## Acceptance

## Open questions
```

Create new artifacts with sequential positive integers without leading zeros within each state. Identifiers have no fixed digit width. Accept legacy four-digit, zero-padded identifiers when reading an existing project, and count them during allocation. Filenames start with the identifier and a readable slug. Keep source artifacts in the working environment while their history remains useful.

Version control is project policy. Inspect repository guidance and ignore rules before staging Research or Evolve. A project may track the files, keep them local, or represent shared work in issues or pull requests.

The CLI may validate promotion readiness and record an accepted decision. The agent presents Research findings before Research-to-Evolve promotion and presents Evolve evidence plus proposed Document changes before Evolve-to-Document promotion. It must not invent agreement or rewrite Document content without an authorized decision.
