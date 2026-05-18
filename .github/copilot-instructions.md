# GitHub Copilot Instructions - basekit

basekit is a small shared Python application foundation package. Keep it generic, conservative, and independent from any single consuming application.

## Project Basics

- Python 3.12+
- Package manager: uv
- Build backend: hatchling
- Tests: pytest
- Linting: ruff

## Commands

Use `uv run`:

```bash
uv run pytest
uv run ruff check .
uv build
```

## Public API

Treat exports in `src/basekit/__init__.py` as public API.

Main modules:

- `src/basekit/config_hook.py`
- `src/basekit/logging.py`

## Coding Guidance

- Keep utilities framework-agnostic.
- Avoid adding app-specific or domain-specific settings.
- Prefer simple dataclass-based configuration patterns.
- Use `pathlib.Path` for path handling.
- Add tests for public behavior changes.
- Keep logging setup opt-in and respectful of application-level handlers.
- Avoid hidden global side effects at import time beyond loading `.env`.

## Testing Guidance

- Use `monkeypatch` for `CONFIG_HOOK` and `EXEC_ENV` tests.
- Use `tmp_path` for filesystem and logging tests.
- Clean up logging handlers in tests that attach them.
- Remember that Python logging state is process-global.

## Documentation Guidance

- Update `docs/guides/` when changing documented behavior.
- Use `docs/issues/` for basekit work items.
- Use `docs/proposals/` for changes needed in external projects such as repom.

Do not copy repom-specific behavior into basekit unless it is clearly a generic foundation utility.
