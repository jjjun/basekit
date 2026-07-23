# Vault Guide

## Overview

`basekit.vault` provides a small, read-only helper for loading local TOML data.
The consuming application chooses the file location; basekit does not define a
global vault path or write secrets.

## Basic Usage

```toml
# vault.toml
[service]
token = "replace-me"
enabled = true
```

```python
from basekit import Vault

vault = Vault(vault_toml_file_path="vault.toml")

service = vault.get("service")
all_values = vault.get()
```

`get("service")` returns the named top-level value. Calling `get()` without a
name returns the complete parsed TOML mapping.

## Error Behavior

- A missing `vault_toml_file_path` raises `ValueError`.
- File opening and TOML parsing errors are propagated to the caller.
- A requested top-level name that does not exist raises `KeyError`.

Keep vault files that contain secrets out of version control. The application
that owns the file should define its storage and distribution policy.

## Related Files

- [Implementation](../../src/basekit/vault.py)
- [Tests](../../tests/test_vault.py)
