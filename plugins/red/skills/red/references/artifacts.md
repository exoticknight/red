# RED artifacts

Use UTF-8 Markdown with TOML front matter delimited by `+++` for Research and Evolve artifacts. Document follows the project's documentation format and the writing guidance below.

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

## Write Document for its readers

Document serves people and agents who need accepted project knowledge while using a feature, implementing a change, reviewing behavior, or diagnosing a problem. Assume they arrive through a search or a direct link without the originating conversation.

Before writing, identify the intended reader, the situation that brings them here, and the question or action the page should support. Use those answers to choose the scope and presentation: procedures for performing tasks, contracts and examples for implementing against interfaces, or boundaries and rationale for making design decisions. Fit the existing documentation structure; these are choices, not mandatory sections.

Locate the existing Document section that owns the subject before adding a page. Update that explanation in place. Create a new owner only when the reader's task or the subject's scope needs one; link other pages to it. Keep locally necessary instructions and constraints where readers use them, while giving shared explanations one maintained home. Preserve generated documentation workflows by editing their source.

When drafting proposed Document content or applying an accepted change:

1. Lead with the answer the reader needs. Extract the accepted definitions, behavior, rules, boundaries, and necessary rationale, and state them directly. Preserve accepted rationale that could change a future reader's use or design decision: why the choice fits, what it costs, its applicable conditions, and when to reconsider it. Derive this from recorded decisions and evidence; keep missing or disputed reasons open in E. Use descriptive headings and concrete examples where they help the reader act.
2. Keep working history and unresolved alternatives in R/E. Remove R/E record identifiers, links, citations, provenance footnotes, and narratives about how those records produced the result. This includes optional history or source links. Record any traceability from R/E to the relevant Document paths instead.
3. Omit authoring dates, last-updated stamps, implementation commit hashes, completion reports, and verification logs from ordinary knowledge pages. Keep delivery evidence in E or version-control history. Include a date, version, or revision only when it changes how the reader interprets or uses the content, or a project-required document format calls for it; explain its role. Examples include an effective date, a supported version range, or an exact revision required for a reproducible procedure. Preserve purposeful metadata in established ADR, release, or audit formats without spreading that format to other pages.
4. Review the page as its intended reader with R/E, task history, and commit history unavailable. Walk through a representative task: a new user installs and starts, a caller handles an interface's constraints, or a maintainer determines what a change may affect. Check the relevant prerequisites, instructions, expected result, and limits against available evidence; exercise documented commands when feasible and authorized, and report what remains unverified. Remove metadata that does not help those tasks. Fill gaps from accepted knowledge; if a gap needs a new decision, keep it open in E and obtain that decision before presenting it as accepted content.

For example, replace “Implemented retry handling in commit abc123 on 2026-09-11; verification passed” with the accepted contract: “Transient failures are retried up to three times. Authentication failures return immediately.” Add the rationale or usage detail the reader needs. Keep a migration deadline when it determines when the reader must act.

Completion requires both independent readability and absence of references to R/E working records. Existing Document-to-Document organization may be preserved. A document whose subject is RED may explain Research and Evolve as concepts; that does not make a particular working record part of Document.
