# RED CLI for Node

This package is the Node distribution of the RED methodology CLI. It provides deterministic project initialization, artifact creation and promotion, structural validation, Skill lifecycle management, and lightweight instruction export.

```sh
npx -y @exoticknight/red@latest version
npx -y @exoticknight/red@latest skill install --scope repo
npx -y @exoticknight/red@latest init
npx -y @exoticknight/red@latest check --json
```

The CLI handles deterministic project files and validation. A human or project-authorized process decides when Research enters Evolve and when Evolve enters Document; promotion flags record that decision.

The Python distribution exposes the same command contract. See the [CLI specification](https://github.com/exoticknight/red/blob/main/spec/cli-interface.md).
