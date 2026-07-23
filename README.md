# basekit

Small, framework-agnostic Python application foundation utilities.

## Public modules

- `basekit.config_hook`: shared `Config` base class and `CONFIG_HOOK` loader
- `basekit.vault`: small TOML-backed local vault helper
- `basekit.logging`: daily log file handler and opt-in logging setup helpers
- `basekit.discovery`: generic package and module discovery helpers
- `basekit.docker_compose`: small Docker Compose YAML generator
- `basekit.docker_manager`: shared Docker command and service manager helpers

## Documentation

- [Documentation map](docs/README.md)
- [Usage guides](docs/guides/README.md)
- [Project profile](ISSUEKIT.md)
- AI agent instructions: [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), and
  [.github/copilot-instructions.md](.github/copilot-instructions.md)

Issues are tracked in the issuekit API for the `basekit` project. Run
`issuekit protocol --role <role>` for the current workflow. Cross-project work
is sent to the owning project's proposal inbox with `issuekit propose`; it is
not stored in this repository.

## Development

basekit requires Python 3.12 or later and uses `uv`:

```bash
uv sync
uv run pytest
uv run ruff check .
uv build
```
