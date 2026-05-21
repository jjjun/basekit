# basekit

Shared Python application foundation utilities.

Initial scope:

- `basekit.config_hook`: shared `Config` base class and `CONFIG_HOOK` loader
- `basekit.vault`: small TOML-backed local vault helper
- `basekit.logging`: daily log file handler and opt-in logging setup helpers
- `basekit.discovery`: generic package and module discovery helpers
- `basekit.docker_compose`: small Docker Compose YAML generator
- `basekit.docker_manager`: shared Docker command and service manager helpers

## Documentation

- `docs/guides/`: usage guides for current basekit features
- `docs/issues/`: basekit implementation task tracking
- `docs/proposals/`: temporary proposals for external project changes
- `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`: AI agent instructions
