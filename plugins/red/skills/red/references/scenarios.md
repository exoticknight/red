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

## Package installation guide

A package registry reader wants to install the tool and run a first command. Locate the guide that owns installation and check the package metadata and executable entry point. Use the registry README for the steps needed there, with links to shared workflow explanations. Walk through prerequisites, installation, invocation, and the observable first result; record verification in E. Derive instructions from the accepted distribution choices. If support for another runtime is undecided, retain that question in E. Apply [Document writing guidance](artifacts.md#write-document-for-its-readers) to make the page usable from the registry alone.

## Package name changes, executable stays the same

An accepted change replaces a distribution's package name while retaining its executable name. Search installation commands, package metadata, owning guides, and active R/E for both names. Replace the package identifier in current installation guidance and retain valid executable examples. Keep an old name in a migration procedure only when existing users need it. Record the scope of replacement in E; unrelated runtime constraints and open work remain applicable. Follow [replacement guidance](work.md#reconcile-replaced-knowledge) to avoid treating the whole previous decision as obsolete.

## Retiring a design record

An accepted export design uses streaming to bound memory use. Before retiring its E record, ensure the owning D explains streaming's memory benefit and any accepted constraint on global sorting. A maintainer should be able to assess a sorting change from that explanation. Keep experiment logs and the sequence of rejected attempts in E; extract a rejected alternative's lasting consequence when it affects future choices. If sorting behavior was never decided, leave it open instead of supplying an invented rationale.
