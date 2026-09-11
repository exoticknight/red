---
name: red
description: Manage project knowledge and engineering changes with Research, Evolve, and Document. Use when the user requests RED, or when a repository declares RED through red.toml, RED.md, or AGENTS.md. Do not impose RED on undeclared projects.
metadata:
  red-protocol: "1"
---

# RED

Keep accepted knowledge, unresolved research, and ongoing change distinct.

## Knowledge and authority

- Document is the normative baseline for people and agents using, maintaining, or changing the project. Organize accepted knowledge and necessary rationale around their tasks; keep R/E record references, provenance, and work history on the R/E side. Use the Document writing guidance in `references/artifacts.md` when drafting or updating it.
- Research holds unverified evidence, claims, and questions. Evolve holds proposed or ongoing change and unresolved alternatives.
- Code, tests, configuration, and runtime output are implementation evidence. Investigate and report conflicts with Document before choosing a side.
- At an R/E boundary, present the reviewable result and wait for a separately authorized transition. A broad earlier request does not supply that decision. Update Document only after acceptance.
- Preserve existing documentation structure and project storage/version-control policy. Keep small, resolved work in the task; persist consequential or shared work using the criteria in `references/work.md`.

## Load context on demand

1. Follow applicable repository instructions. Read `red.toml` when present; otherwise locate likely Document sources. Create configuration only for requested adoption or deterministic operations needing a mapping.
2. Read the reference for the current route below. Load additional references only when their operation becomes necessary; links are lookup targets, not a recursive reading list.
3. Find relevant Document sections, active E items, R evidence, and implementation with filenames, headings, or scoped search before reading bodies. Widen the search when dependencies or conflicts require it.
4. Reuse instructions and evidence already available in context. Re-read changed sections, or missing material after compaction, rather than restarting discovery each turn. Keep tool output focused on relevant excerpts and results.

## Routes

- Engineering work and E maintenance: [work.md](references/work.md).
- First-time or brownfield adoption: [adopt.md](references/adopt.md).
- Project health checks: [inspect.md](references/inspect.md).
- Creating/promoting artifacts or drafting/updating Document: [artifacts.md](references/artifacts.md).
- Using, enabling, or falling back from the CLI: [cli.md](references/cli.md).
- Unclear state semantics: [protocol.md](references/protocol.md); unfamiliar routing cases: [scenarios.md](references/scenarios.md).

## Finish

Reconcile active E with current decisions, evidence, remaining work, and open alternatives. Report verification, conflicts, and unknowns; apply the transition boundary above. Run `red check --json` when the CLI is available, and state when it could not run.
