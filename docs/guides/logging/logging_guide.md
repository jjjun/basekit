# Logging Guide

## Overview

`basekit.logging` provides opt-in logging helpers for packages that want a default logger only when the consuming application has not already configured logging.

The active file uses this date-named format:

```text
<base>_<YYYY-MM-DD>.log
```

For example, a base path of `data/example/logs/main` writes to:

```text
data/example/logs/main_2026-05-19.log
```

## Public API

```python
from basekit.logging import (
    DateNamedDailyFileHandler,
    configure_default_logging,
    configure_sqlalchemy_logging,
    get_logger,
    has_logging_handlers,
    make_timed_rotating_handler,
    reset_logging_state,
)
```

## Basic Usage

```python
import logging

from basekit.logging import get_logger

logger = get_logger(
    "worker",
    logger_name="my_package",
    log_file_path="data/my_package/logs/main",
    level=logging.INFO,
)

logger.info("started")
```

The logger name is `my_package.worker`.

Pass `level` to `get_logger()` or `configure_default_logging()` to set the
package logger and file handler threshold. It defaults to `logging.DEBUG`.
The console handler uses `max(level, logging.INFO)`, so it remains at `INFO`
with the default and follows higher thresholds such as `WARNING`.

## Handler Behavior

`DateNamedDailyFileHandler` opens the current date's active file directly. It does not write to an undated `main` file and then rename it later.

```python
from basekit.logging import make_timed_rotating_handler

handler = make_timed_rotating_handler("data/my_package/logs/main")
```

Old dated logs are removed after `backup_count` files. The default is `30`.
New log files default to owner-only permissions (`0o600`). This mode is reapplied
whenever the active file is opened, including restarts and date rotation. Pass
`file_mode` when a different mode is required, such as `file_mode=0o640` for
group-readable logs.

## Application Logging Policy

`configure_default_logging()` checks existing root handlers and package handlers before adding file and console handlers. This keeps basekit-friendly packages from overriding application-level logging configuration.

When called through `get_logger()`, default configuration is attempted once per `logger_name`, rather than once per process. A call without `log_file_path` does not consume that attempt, so a later call for the same package can configure logging when it supplies a path. `configure_default_logging()` returns `True` when it installs handlers and `False` when it declines to configure them.

SQLAlchemy echo configuration remains process-global, but a later `get_logger()` call can enable it even if an earlier caller left `sqlalchemy_echo` disabled.

## SQLAlchemy Logging

SQLAlchemy engine logging can be enabled explicitly:

```python
from basekit.logging import get_logger

logger = get_logger(
    "db",
    logger_name="my_package",
    log_file_path="data/my_package/logs/main",
    sqlalchemy_echo=True,
    sqlalchemy_echo_level="INFO",
)
```

Valid levels are currently `INFO` and `DEBUG`; unknown values fall back to `INFO`.

## Testing Notes

- Call `basekit.logging.reset_logging_state()` in focused tests when verifying first-time setup.
- Remove handlers created during tests to avoid leaking logging state across test cases.
- Use `tmp_path` for log file paths.

## Related Files

- [Implementation](../../../src/basekit/logging.py)
- [Tests](../../../tests/test_logging.py)
