# Testing Guide

## Overview

basekit uses pytest for focused unit tests around shared utilities. Tests should avoid application-specific fixtures and should not depend on a developer's machine-level environment variables.

## Commands

Run all tests:

```bash
uv run pytest
```

Run a single test module:

```bash
uv run pytest tests/test_config_hook.py
uv run pytest tests/test_logging.py
```

Run lint checks:

```bash
uv run ruff check .
```

## Environment Variables

Use `monkeypatch` for environment-dependent behavior:

```python
def test_hook_missing(monkeypatch):
    monkeypatch.delenv("CONFIG_HOOK", raising=False)
```

Do not rely on persistent shell values such as `CONFIG_HOOK` or `EXEC_ENV` in tests.

## Logging Tests

Logging state is process-global. Tests that verify first-time logger setup should restore state and remove handlers they create.

```python
import basekit.logging as logging_module

logging_module._logger_initialized = False
```

Use `tmp_path` for file output and close handlers before assertions that inspect files.

## Test Scope

Add tests when:

- public behavior changes
- a new helper is exported
- error messages or exception types become part of the expected contract
- path or environment handling changes

Avoid adding app-specific fixtures to this repository. Integration examples for consuming projects belong in that project's tests or in `docs/proposals/` when a coordinated change is needed.
