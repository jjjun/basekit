# CLAUDE.md - basekit Project

## Project Overview

basekit is a small shared Python foundation package. It provides reusable configuration hook and logging utilities for packages and applications.

The package should stay generic. Do not add behavior that only makes sense for one consuming project.

## Stack

- Python 3.12+
- uv
- hatchling
- pytest
- ruff
- python-dotenv

## Important Commands

```bash
uv run pytest
uv run pytest tests/test_config_hook.py
uv run pytest tests/test_logging.py
uv run ruff check .
uv build
```

## Public API

Public exports live in `src/basekit/__init__.py`.

Current public modules:

- `basekit.config_hook`
- `basekit.discovery`
- `basekit.docker_compose`
- `basekit.docker_manager`
- `basekit.logging`

## Configuration Hook Contract

`CONFIG_HOOK` may be:

```text
package.module:function_name
package.module
```

When the function name is omitted, basekit loads `hook_config`.

Invalid modules, missing functions, and non-callable targets raise `ConfigHookLoadError`.

## Logging Contract

`DateNamedDailyFileHandler` writes directly to the date-named active file:

```text
<base>_<YYYY-MM-DD>.log
```

Do not reintroduce an undated active log file unless the public contract is intentionally changed and tests/docs are updated.

## Docker Helper Contract

`DockerManager` must not import configuration from consuming projects. Subclasses pass `data_path` into `super().__init__(data_path=...)`.

`DockerCommandExecutor` wraps docker and docker-compose subprocess calls. Keep it stateless.

## Development Rules

- Keep changes small and focused.
- Add or update tests for public behavior changes.
- Use `monkeypatch` for environment-variable tests.
- Use `tmp_path` for filesystem tests.
- Use injected paths for Docker manager tests.
- Reset or clean up process-global logging state in tests that modify handlers.
- Prefer `pathlib.Path` for filesystem paths.
- Keep examples framework-neutral unless documenting a specific integration.

## Documentation

- Usage guides: `docs/guides/`
- basekit implementation tasks: `docs/issues/`
- external coordination notes: `docs/proposals/`

When a basekit change requires another project to change first or in parallel, create a proposal under `docs/proposals/` instead of turning that external work into a basekit issue.
