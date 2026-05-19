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
│   └── logging.py
├── tests/
│   ├── test_config_hook.py
│   └── test_logging.py
├── docs/
│   ├── guides/
│   ├── issues/
│   └── proposals/
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
- `docs/issues/` contains basekit implementation tasks.
- `docs/proposals/` contains temporary proposals for external projects/packages when basekit cannot complete the overall goal alone.

## Proposal Management

Use `docs/proposals/` when work in basekit reveals that another project or package must change before the overall goal can be completed.

When creating a proposal:

1. Check Markdown files directly under `docs/proposals/`.
2. Ignore `README.md` and `_template.md` when choosing the number.
3. Use the next number after the current maximum, zero-padded to three digits.
4. Copy `docs/proposals/_template.md` to `docs/proposals/NNN_<target>_<slug>.md`.
5. Fill in why basekit cannot complete the change alone, what the target should change, and what follow-up remains in basekit.
6. Continue implementing any part that can be handled inside basekit.

Delete proposal files after the target project has accepted, rejected, or otherwise completed the proposal and basekit no longer needs the tracking note.

## Issue Management

When an issue is completed:

- Keep the file name unchanged.
- Move the file from `docs/issues/active/` to `docs/issues/completed/`.
- Update `docs/issues/README.md` to move the entry from active to completed.

## Notes For AI Assistants

- This project uses **uv**. Always use `uv run` when executing tests or tools.
- Do not introduce dependencies unless the shared utility clearly needs them.
- Avoid copying large repom-specific documentation into basekit.
- If a change is primarily needed by repom, keep basekit generic and document any repom-side work as a proposal or follow-up.
