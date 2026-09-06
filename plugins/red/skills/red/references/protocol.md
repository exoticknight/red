# RED Protocol 1

RED assigns project knowledge to one of three states.

## Research

Research holds unresolved questions, observations, external sources, hypotheses, experiments, and conflicting evidence. A Research item may stay incomplete. Label claims and uncertainty so an agent cannot mistake them for requirements.

Research supports an Evolve proposal through explicit references. Promotion does not copy every note into Evolve.

When Research can support an Evolve scope, the agent reports its findings and waits for an explicit human decision or a decision source that the project has authorized. RED does not require Research when the change and its acceptance conditions are already clear.

## Evolve

Evolve holds a proposed or active change. Record the problem, proposed change, tradeoffs, affected areas, acceptance conditions, and open questions. Design, implementation, tests, revision, and user interaction remain in Evolve until acceptance. An explicit user request can authorize work on an Evolve item. Open alternatives remain undecided until the user or project policy resolves them.

After implementation and verification, the agent reports its evidence and proposed Document changes, then waits for explicit acceptance. An accepted Evolve item updates the relevant Document sources. A rejected item leaves Document unchanged. A partially accepted item records the accepted boundary and updates Document only for that part.

## Document

Document contains accepted goals, boundaries, terminology, public interfaces, architecture rules, operating instructions, and contribution rules. Agents start from Document and treat it as the normative baseline.

Document can become stale. Code, tests, configuration, and runtime output provide implementation evidence. A conflict between the baseline and evidence enters Research. The resulting decision may restore the implementation to Document or create an Evolve item that changes the baseline.

## Transition authority

A broad request to complete work does not authorize later transitions whose results were not ready for review when the request was made. The user decides at the Research and Evolve checkpoints, unless the project defines another human-approved decision source such as an issue state or pull-request approval. CLI flags record a supplied decision; they do not create authority.

## Persistence

RED classifies knowledge in every task but does not require a file for every thought. Persist Research or Evolve when work crosses tasks, needs review, presents alternatives, affects public behavior or architecture, or leaves an unresolved conflict. Keep short-lived local reasoning in the active task.

Persistence and publication are separate decisions. Each project chooses whether to track Research and Evolve files, keep them local, or publish the work through another collaboration system. Tracking changes availability, not knowledge state: an R or E artifact does not become Document when committed.
