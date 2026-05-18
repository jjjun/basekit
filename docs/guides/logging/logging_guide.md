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
)
```

## Basic Usage

```python
from basekit.logging import get_logger

logger = get_logger(
    "worker",
    logger_name="my_package",
    log_file_path="data/my_package/logs/main",
)

logger.info("started")
```

The logger name is `my_package.worker`.

## Handler Behavior

`DateNamedDailyFileHandler` opens the current date's active file directly. It does not write to an undated `main` file and then rename it later.

```python
from basekit.logging import make_timed_rotating_handler

handler = make_timed_rotating_handler("data/my_package/logs/main")
```

Old dated logs are removed after `backup_count` files. The default is `30`.

## Application Logging Policy

`configure_default_logging()` checks existing root handlers and package handlers before adding file and console handlers. This keeps basekit-friendly packages from overriding application-level logging configuration.

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

- Reset `basekit.logging._logger_initialized` in focused tests when verifying first-time setup.
- Remove handlers created during tests to avoid leaking logging state across test cases.
- Use `tmp_path` for log file paths.

## Related Files

- `src/basekit/logging.py`
- `tests/test_logging.py`
