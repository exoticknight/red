# Scenario routing

| Situation | Route | Persistent artifact |
|---|---|---|
| Work already specified by Document | Implement | Usually none |
| Clear accepted feature request | Evolve | Persist for public or cross-task change |
| Ambiguous feature request | Research, then Evolve | Persist unresolved evidence and consequential change |
| Research has enough evidence for a proposal | Report findings and stop | Wait for explicit authority before Evolve |
| Diagnose a bug | Research | Persist when findings must survive the task |
| Repair behavior that violates Document | Research, then repair | Document stays unchanged |
| Change a public interface | Evolve | Persist and update Document after acceptance |
| Mechanical internal refactor | Implement | Usually none |
| Architectural refactor | Evolve | Persist |
| Experimental spike | Research | Do not promote without a decision |
| Document conflicts with implementation | Research | Persist unresolved conflict |
| Evolve item rejected | Close Evolve | Document stays unchanged |
| Evolve item partly accepted | Record boundary | Update Document for accepted part |
| Evolve passes its acceptance conditions | Report evidence and stop | Wait for explicit acceptance before Document |
| Urgent repair | Restore accepted behavior, then record material findings | Keep the record proportional |
| Repository is read-only | Analyze and report | No writes |
| User declines CLI or docs | Work in task context | Explain unresolved continuity risk |
| CLI cannot run | Follow artifact rules by hand | Report skipped structural validation |
| Concurrent Evolve items conflict | Preserve both and request a decision | Do not merge conclusions |

“Persist” means keep the work available beyond the current task. The project decides whether that means tracked files, local files, issues, pull requests, or another system.
