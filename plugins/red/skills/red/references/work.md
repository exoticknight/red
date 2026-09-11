# Work with RED

## Ground and route

Use the entrypoint's context-loading rules. Start from the relevant Document baseline and active E summary; follow R or historical evidence to resolve current questions.

- Implement directly when Document or active E specifies the work and no decision-blocking unknown remains.
- Use Research for unknowns that can change implementation or acceptance, including Document/evidence conflicts.
- Use Evolve for changes to accepted behavior, public interfaces, data, architecture, or engineering rules.

A clear feature request may authorize direct entry to Evolve. A bug violating Document may proceed from diagnosis to repair without changing Document. Route by knowledge state rather than a mandatory R-to-E-to-D sequence.

## Maintain active E

On resumption or new instructions, compare active E with the request and current evidence. Before dependent work, record material changes to scope, design, acceptance, decisions, or constraints, including findings that change the plan. Distinguish authorized decisions from unresolved alternatives; a user request clearly authorizing an adjustment supplies that authority. Ordinary E maintenance needs no separate approval.

After meaningful results, record concise evidence, verification status (including failed or pending checks), and remaining work. Before pause, handoff, or completion, reconcile E with actual work and current decisions. Batch minor edits until these triggers. If storage is unavailable, preserve the update in the task and identify the blocker.

Keep current scope, decisions, acceptance, verification, and next steps easy to resume. Replace stale status while retaining decision rationale, unresolved alternatives, and review evidence. Link detailed logs or experiments from R/E instead of copying output or appending every turn. Update affected sections without re-reading the whole record after each edit.

## Reconcile replaced knowledge

When a proposed change alters an existing decision, search the affected Document sections and active R/E for the same behavior, rule, or assumption. Include the affected owners and outstanding conflicts in the reviewable E result. After acceptance, reconcile that scope with the accepted decision:

- Fully replaced: update the owning Document explanation and its current-use links; mark affected working records as superseded or close them using the project's existing conventions.
- Partly replaced: state which conditions or parts changed and preserve the still-valid constraints, rationale, and open work.
- Still applicable: retain it. A newer decision alone does not invalidate an older one.

Carry accepted, durable rationale into Document using [the writing guidance](artifacts.md#write-document-for-its-readers) before retiring its working record. Retain useful evidence and rejected alternatives in R/E under the project's retention policy. Keep historical records distinguishable from current guidance; preserve frozen archives. Record replacement relationships on the R/E side. Concurrent changes with unresolved conflicts remain open for a decision.

## Persist

Persist work that crosses tasks, needs review, presents alternatives, affects public behavior or architecture, or leaves an unresolved conflict. Keep small local work in task context when persistence is unnecessary. Use the CLI when available; consult `artifacts.md` for record structure. Follow project storage and version-control policy; artifact creation does not authorize publication.

## Execute and report

Investigate within Research; design, implement, verify, and revise within authorized Evolve scope. Seek a decision for scope expansion. Apply the entrypoint's transition boundary:

- Present R findings, uncertainty, risks, and proposed E scope for a decision.
- Present E verification evidence and proposed Document changes for acceptance.
- Record authorized promotions; synchronize accepted E behavior with Document.
