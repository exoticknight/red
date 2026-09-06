# Exit codes

| Code | Meaning |
|---:|---|
| `0` | Command completed and validation passed |
| `1` | `check` completed and found protocol or project validation errors |
| `2` | Usage error, unsafe/unmanaged target, missing input, conflict, or failed mutation |

With `check --json`, code `1` writes a structured result to standard output. Command failures write a concise message to standard error.
