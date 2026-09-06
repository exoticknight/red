# RED plugin

This skills-only plugin packages the host-neutral RED Skill for Codex-compatible plugin hosts. The canonical Skill is `skills/red`; the plugin manifest supplies host presentation metadata.

The Skill routes clear changes to Evolve without Research and uses Research when an unknown can change the decision. It pauses before Research-to-Evolve and Evolve-to-Document transitions so a human or project-authorized process can decide. The RED CLI remains optional and supplies deterministic project operations when available.

Release archives follow the project release version. The Skill content has no separate version and declares only its supported RED protocol.
