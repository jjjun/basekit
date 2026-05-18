# basekit Documentation

basekit is a small shared foundation package for Python applications. It contains cross-project utilities that should stay independent from any single application domain.

## Documentation Map

- [guides/](guides/) - practical usage guides for basekit features
- [issues/](issues/) - implementation tasks and completed work records for basekit itself
- [proposals/](proposals/) - temporary proposals for changes that must happen in another project or package

## Current Scope

- `basekit.config_hook`: `Config` base class and `CONFIG_HOOK` loader
- `basekit.logging`: date-named log file handler and opt-in logger setup helpers

## Maintenance Rules

- Keep examples framework-agnostic unless a guide is explicitly about an integration.
- Prefer adding small, reusable utilities over application-specific behavior.
- When changing public behavior, update the relevant guide and add or update tests.
- Use `docs/issues/` for basekit implementation work.
- Use `docs/proposals/` only when basekit cannot complete the overall goal without changes in another project.
