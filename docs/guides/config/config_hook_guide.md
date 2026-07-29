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
- `auto_create_dirs`
- `data_path`
- `log_path`
- `log_file`
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

`log_file` defaults to `test` when `EXEC_ENV=test`; otherwise it defaults to `main`.

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
