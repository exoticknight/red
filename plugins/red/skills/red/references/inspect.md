# Inspect a RED project

Inspect these conditions:

- `red.toml` parses and uses a supported protocol version.
- Declared paths exist or have a clear reason to remain empty.
- R and E identifiers are unique.
- Research claims have not leaked into Document as accepted facts.
- Evolve alternatives have not been resolved without a recorded decision.
- Accepted changes have matching implementation and Document updates.
- Document meets the reader and writing criteria in [artifacts.md](artifacts.md): readers can find and use accepted knowledge without working history; dates and revisions have a reader-facing purpose or a required format; R/E record references and process narratives stay in R/E.
- Document conflicts with code, tests, configuration, or runtime evidence are visible.
- Installed Skill or exported instructions implement the configured protocol.

Use `red status --json` and `red check --json` when available. Add semantic findings from reading the relevant content; the CLI cannot make those judgments.
