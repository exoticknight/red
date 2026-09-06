# Adopt RED

Adopt RED without reorganizing the repository.

1. Inventory existing README files, maintained docs, ADRs, proposals, investigations, issues, and contribution rules.
2. Propose a mapping for Document, Evolve, and Research. Explain ambiguous locations.
3. Prefer the RED CLI. Run `red init` only after the task authorizes project setup.
4. Edit the generated `red.toml` to reflect the accepted mapping.
5. Run `red check --json`.

Do not migrate old documents or reconstruct historical decisions. Classify current sources and use RED for work from this point forward.

Choose whether the project tracks Research and Evolve files, keeps them local, or uses its issue or pull-request system. Record the choice in repository guidance or ignore rules; RED supplies no default.

For agents without Skill support, use `red instructions install --target AGENTS.md` or `red instructions export --output RED.md`.
