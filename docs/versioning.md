# Versioning

RED has two version axes.

The release version follows SemVer and identifies one coordinated snapshot of the npm CLI, Python CLI, Codex plugin, and RED Skill. The Skill has no separate version field; `.red-install.json` records the release that supplied it.

The protocol version is the integer in `red.toml`. It changes only when configuration, artifact, transition, or command semantics become incompatible. A release can improve wording, add backward-compatible validation, or fix a CLI without changing the protocol.

Tags use `vMAJOR.MINOR.PATCH`. The release workflow verifies that the tag is valid, injects that version into build copies, runs unit and conformance tests, and publishes all artifacts from the same source commit.
