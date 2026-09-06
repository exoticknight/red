# Contributing to RED

RED has two CLI implementations but one protocol. A behavior change is complete only when both implementations and the shared conformance suite agree.

## Local checks

Install the development dependencies and generate ignored package inputs first:

```sh
python -m pip install -r requirements-dev.txt
python scripts/sync_distribution.py
(cd cli/node && npm ci && npm test && npm run check)
(cd cli/python && python -m unittest discover -s tests -v)
python cli/conformance/run.py
python scripts/validate_repository.py
```

## Change rules

- Write a failing behavior test before changing either CLI.
- Mirror protocol behavior in Node and Python.
- Add or update a shared conformance case when observable behavior changes.
- Edit the canonical Skill under `plugins/red/skills/red`, then run `python scripts/sync_distribution.py`. Do not edit generated package or `.agents` copies.
- Keep the canonical Skill host-neutral; put host-specific presentation in plugin metadata.
- Keep file-backed Research and Evolve out of commits. Use an issue or pull request when other contributors need the working state.
- Change Protocol 1 only in a backward-compatible way. Start a new protocol version for incompatible configuration, artifact, or command semantics.
- Record an architectural or dependency choice in `docs/architecture.md` when it changes a maintained boundary.

All contributions are accepted under Apache-2.0.
