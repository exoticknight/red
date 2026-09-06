# Conformance fixtures

A fixture is a small, controlled example project plus a sequence of commands and expected outcomes. It is test data, not production configuration.

`cases.json` runs the same workflow through the Node and Python CLIs. `run.py` compares exit codes, parsed JSON, and the final file tree. A change that makes the two distributions behave differently fails CI even when each implementation's unit tests pass on its own.

The runner first verifies every generated creation date against the local dates observed at the start and end of the run, then normalizes it for filesystem comparison. This permits a midnight rollover without hiding UTC/local-date regressions or arbitrary dates.
