# RED CLI for Python

This package is the Python distribution of the RED methodology CLI. It provides deterministic project initialization, artifact creation and promotion, structural validation, Skill lifecycle management, and lightweight instruction export.

```sh
pipx run --spec red-cli red version
pipx run --spec red-cli red skill install --scope repo
pipx run --spec red-cli red init
pipx run --spec red-cli red check --json
```

The CLI handles deterministic project files and validation. A human or project-authorized process decides when Research enters Evolve and when Evolve enters Document; promotion flags record that decision.

The Node distribution exposes the same command contract. See the [CLI specification](https://github.com/exoticknight/red/blob/main/spec/cli-interface.md).
