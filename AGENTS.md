# AGENTS.md - basekit Project

## Project Overview

**basekit** ships small, shared Python application foundation utilities that can be reused by packages such as repom and by application projects. Keep this package generic and independent from any single application domain.

## Technology Stack

- **Language**: Python 3.12+
- **Package Manager**: uv
- **Build Backend**: hatchling
- **Configuration**: python-dotenv
- **Testing Framework**: pytest
- **Linting**: ruff

## Project Structure

```text
basekit/
├── src/basekit/
│   ├── __init__.py
│   ├── config_hook.py
│   ├── discovery.py
│   ├── docker_compose.py
│   ├── docker_manager.py
│   ├── logging.py
│   └── vault.py
├── tests/
│   ├── test_config_hook.py
│   ├── test_discovery.py
│   ├── test_docker_compose.py
│   ├── test_docker_manager.py
│   ├── test_logging.py
│   └── test_vault.py
├── docs/
│   └── guides/
├── pyproject.toml
├── README.md
└── uv.lock
```

## Public Modules

### `basekit.config_hook`

- `Config`: generic base configuration class
- `get_config_from_hook()`: applies the `CONFIG_HOOK` function if configured
- `load_hook_function()`: imports a hook function from `module:function`
- `ConfigHookLoadError`: raised for invalid hook configuration

### `basekit.logging`

- `DateNamedDailyFileHandler`: writes active logs to `<base>_<YYYY-MM-DD>.log`
- `make_timed_rotating_handler()`: handler factory
- `get_logger()`: opt-in package logger setup helper
- `configure_default_logging()`: configures package logging only when no real handlers exist
- `configure_sqlalchemy_logging()`: optional SQLAlchemy engine logging helper

### `basekit.vault`

- `Vault`: reads complete TOML mappings or named top-level values from an
  injected local file path

### `basekit.discovery`

- `normalize_paths()`: normalizes strings, comma-separated strings, and lists
- `DiscoveryFailure` / `DiscoveryError`: structured import failure reporting
- `import_packages()` / `import_package_directory()` / `import_from_packages()`: generic import helpers

### `basekit.docker_compose`

- `DockerService`
- `DockerVolume`
- `DockerComposeGenerator`

### `basekit.docker_manager`

- `DockerCommandExecutor`: docker and docker-compose subprocess helpers
- `DockerManager`: base class for service managers; requires injected `data_path`
- `print_message()`, `validate_compose_file_exists()`, `format_connection_info()`

## Environment Variables

- `CONFIG_HOOK`: optional hook path in `package.module:function_name` format. If the function name is omitted, `hook_config` is used.
- `EXEC_ENV`: environment name used by `Config`; defaults to `dev`. `EXEC_ENV=test` changes the default `log_file` to `test`.

## Commands

Use `uv run` for all local commands:

```bash
uv run pytest
uv run pytest tests/test_config_hook.py
uv run pytest tests/test_logging.py
uv run ruff check .
uv build
```

## Development Guidelines

- Keep utilities framework-agnostic and application-agnostic.
- Do not move app-specific settings or domain concepts into basekit.
- Treat exported names in `src/basekit/__init__.py` as public API.
- When changing public behavior, update tests and the relevant guide in `docs/guides/`.
- Use `monkeypatch` for environment-variable tests.
- Be careful with logging tests because Python logging state is process-global.
- Inject `data_path` into `DockerManager` subclasses; do not import consumer project config from basekit.
- Prefer `pathlib.Path` for path logic.
- Keep comments short and only where they clarify non-obvious behavior.

## Documentation Guidelines

- `docs/guides/` contains user-facing usage guides.
- Issues live in the issuekit API (`project = "basekit"`); run `issuekit protocol` for the flow.

## Cross-Project Proposals

When basekit work reveals that another project or package must change first, send
a cross-project proposal with issuekit (`issuekit propose`), which posts to the
target project's API proposal inbox. See `issuekit protocol` for the flow. Do
not maintain a local `docs/proposals/` directory.

## Issue Management

Issues are tracked in the issuekit API (`project = "basekit"`); there is no local
`docs/issues/{active,completed,indexes}` tracker. Author with `issuekit author`
(the API allocates the id) and let the API own claim/review/completion. The
workflow steps are owned by issuekit: run `issuekit protocol --role <role>` (or
the MCP `get_protocol` tool).

## Notes For AI Assistants

- This project uses **uv**. Always use `uv run` when executing tests or tools.
- Do not introduce dependencies unless the shared utility clearly needs them.
- Avoid copying large repom-specific documentation into basekit.
- If a change is primarily needed by repom, keep basekit generic and document any repom-side work as a follow-up.

## Handoff protocol

This repo uses the issuekit multi-agent handoff. For the current steps, run
`issuekit protocol --agent <agent>` (e.g. `codex`, `claude`, or `kimi`) or
`issuekit protocol --role <role>` (e.g. `implementer` or `reviewer`), or read the
issuekit MCP server instructions / `get_protocol` tool.

Do not copy the steps here; issuekit is the source of truth. Launch your agent from the repo root so the MCP server resolves the repo configuration
(the `project` key and API settings).
