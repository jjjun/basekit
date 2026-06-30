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
- basekit issues: tracked in the issuekit API (`project = "basekit"`); run `issuekit protocol` for the flow

When a basekit change requires another project to change first or in parallel, send a cross-project proposal with issuekit (`issuekit propose`) instead of turning that external work into a basekit issue. See `issuekit protocol`.

## Handoff protocol

This repo uses the issuekit multi-agent handoff. For the current steps, run
`issuekit protocol --agent <agent>` (e.g. `codex`, `claude`, or `kimi`) or
`issuekit protocol --role <role>` (e.g. `implementer` or `reviewer`), or read the
issuekit MCP server instructions / `get_protocol` tool.

Do not copy the steps here; issuekit is the source of truth. Launch your agent from the repo root so the MCP server resolves the repo configuration
(the `project` key and API settings).
