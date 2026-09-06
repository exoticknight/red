# RED CLI for Node

This package is the Node distribution of the RED methodology CLI. It provides deterministic project initialization, artifact creation and promotion, structural validation, Skill lifecycle management, and lightweight instruction export.

```sh
npx -y red-methodology-cli@latest version
npx -y red-methodology-cli@latest skill install --scope repo
npx -y red-methodology-cli@latest init
npx -y red-methodology-cli@latest check --json
```

The CLI handles deterministic project files and validation. A human or project-authorized process decides when Research enters Evolve and when Evolve enters Document; promotion flags record that decision.

The Python distribution exposes the same command contract. See the [CLI specification](https://github.com/exoticknight/red/blob/main/spec/cli-interface.md).
