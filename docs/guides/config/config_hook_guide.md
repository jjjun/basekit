# Config Hook Guide

## Overview

`basekit.config_hook` provides a small configuration base class and an environment-driven hook loader. Packages such as repom can create their own config object, then let consuming applications modify or replace values through `CONFIG_HOOK`.

## Public API

```python
from basekit import (
    Config,
    ConfigHookLoadError,
    get_config_from_hook,
    load_hook_function,
)
```

`Config` currently provides:

- `root_path`
- `exec_env`
- `normalized_exec_env`
- `auto_create_dirs`
- `data_path`
- `log_path`
- `log_file`
- `log_level`
- `log_file_path`
- `init()`
- `cleanup()`
- `clone()`

## Basic Usage

```python
from basekit.config_hook import Config, get_config_from_hook

config = Config(root_path=".")
config.package_name = "my_package"
config = get_config_from_hook(config)
config.init()

print(config.data_path)
print(config.log_file_path)
```

When `CONFIG_HOOK` is unset or blank, `get_config_from_hook()` returns the original config object.

## Hook Format

`CONFIG_HOOK` accepts either:

- `package.module:function_name`
- `package.module`

When the function name is omitted, `hook_config` is used.

`load_hook_function()` is also available for settings other than `CONFIG_HOOK`.
Use `source` to identify the setting in error messages:

```python
hook = load_hook_function(path, source="pre_migration_hook")
```

Colonless paths use `hook_config` by default. Set `default_function` to choose a
different callable name, or pass `default_function=None` to require the
explicit `package.module:function_name` form.

Importing `basekit.config_hook`, including through the top-level `basekit`
exports, calls `load_dotenv()` and may populate `os.environ` from a `.env` file.
Set `BASEKIT_NO_SIDE_EFFECTS` to `1`, `true`, `yes`, or `on` before importing
basekit to skip that call.

Example:

```powershell
$env:CONFIG_HOOK='my_app.config:get_basekit_config'
```

```python
# my_app/config.py
from basekit import Config


def get_basekit_config(config: Config) -> Config:
    config.root_path = "."
    config.package_name = "my_app"
    config.log_file = "app"
    return config
```

## Error Handling

Invalid hook modules, missing functions, and non-callable hook targets raise `ConfigHookLoadError`.

```python
from basekit import Config, ConfigHookLoadError, get_config_from_hook

try:
    config = get_config_from_hook(Config())
except ConfigHookLoadError as exc:
    raise RuntimeError("Application configuration hook is invalid") from exc
```

## Path Behavior

If `root_path` is set, `data_path` defaults to:

```text
<root_path>/data/<package_name>
```

When `package_name` is not set, it defaults to:

```text
<root_path>/data
```

`log_path` defaults to:

```text
<data_path>/logs
```

`exec_env` retains the value provided to `Config`. `normalized_exec_env` strips
whitespace, lowercases the value, and maps `production` to `prod`; other values
pass through after stripping and lowercasing. The `log_file` default is `test`
when `normalized_exec_env` is `test`; otherwise it is `main`.
This changes prior logging defaults for values such as `production`, ` Prod `,
and `TEST`, which now receive the same defaults as normalized `prod` and `test`.

`log_level` defaults to `logging.DEBUG` except when `normalized_exec_env` is
`prod`, where it defaults to `logging.INFO`. Unknown environment names keep
their normalized value and use the defaults `main` and `logging.DEBUG`. Set
`LOG_LEVEL` to a case-insensitive logging level name such as `WARNING` to
override the default. Invalid values raise `ValueError` when `log_level` is
accessed. Assign `config.log_file` or `config.log_level` directly to override
the corresponding default.

## Resolving Configuration Without Side Effects

`Config.auto_create_dirs` defaults to `True`. Calling `init()` creates the
configured `data_path` and `log_path` directories. Pass `auto_create_dirs=False`
to skip that creation while resolving configuration for another environment:

```python
config = Config(
    root_path=".",
    exec_env="staging",
    auto_create_dirs=False,
)
config = get_config_from_hook(config)
config.init()
```

A `CONFIG_HOOK` function can also disable directory creation for the config it
receives:

```python
def hook_config(config: Config) -> Config:
    config.auto_create_dirs = False
    return config
```

Subclasses that create their own directories must check
`self.auto_create_dirs` before doing so. The `auto_create_dirs` constructor
argument takes precedence over `BASEKIT_NO_SIDE_EFFECTS`; otherwise the flag
sets its default, which is `True` when the flag is unset or unrecognized.
Values `1`, `true`, `yes`, and `on` enable the flag after stripping whitespace
and ignoring case. Set it before importing packages that create a config at
module scope.

When a tool changes `EXEC_ENV` after importing basekit, pass `exec_env=`
explicitly to `Config`: its default is evaluated when the class is defined.

## Testing Notes

Use `monkeypatch` for hook-related tests:

```python
def test_config_hook_disabled(monkeypatch):
    monkeypatch.delenv("CONFIG_HOOK", raising=False)
```

Avoid tests that depend on a developer's shell environment.

## Related Files

- [Implementation](../../../src/basekit/config_hook.py)
- [Tests](../../../tests/test_config_hook.py)
