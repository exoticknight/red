# RED plugin

This skills-only plugin packages the host-neutral RED Skill for Codex-compatible plugin hosts. The canonical Skill is `skills/red`; the plugin manifest supplies host presentation metadata.

The Skill routes clear changes to Evolve without Research and uses Research when an unknown can change the decision. It pauses before Research-to-Evolve and Evolve-to-Document transitions so a human or project-authorized process can decide. The RED CLI remains optional and supplies deterministic project operations when available.

Release archives follow the project release version. The Skill content has no separate version and declares only its supported RED protocol.

## Install with skills

From your target project, run:

```sh
npx skills add exoticknight/red --skill red
```

The [skills CLI](https://github.com/vercel-labs/skills) discovers `plugins/red/skills/red` directly. Select your agent during installation, or pass `--agent codex`, for example. Add `--global` for user scope. Use `npx skills update` to update installations managed by skills.
