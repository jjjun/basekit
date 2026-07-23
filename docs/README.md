# basekit Documentation

basekit is a small shared foundation package for Python applications. It
contains cross-project utilities that should stay independent from any single
application domain.

## Documentation Map

- [Usage guides](guides/README.md) - practical references for public features
- [Project profile](../ISSUEKIT.md) - basekit responsibilities and scope
- [Contributor instructions](../AGENTS.md) - repository-specific development
  and handoff rules

## Current Scope

- `basekit.config_hook`: `Config` base class and `CONFIG_HOOK` loader
- `basekit.vault`: TOML-backed local vault helper
- `basekit.logging`: date-named log file handler and opt-in logger setup helpers
- `basekit.discovery`: generic package and module discovery helpers
- `basekit.docker_compose`: small Docker Compose YAML generator
- `basekit.docker_manager`: Docker command and service manager helpers

## Maintenance Rules

- Keep examples framework-agnostic unless a guide is explicitly about an
  integration.
- Prefer adding small, reusable utilities over application-specific behavior.
- When changing public behavior, update the relevant guide and add or update tests.
- Track basekit implementation work in the issuekit API (`project = "basekit"`).
- Send work owned by another project to its issuekit proposal inbox rather than
  duplicating that project's specification here.
