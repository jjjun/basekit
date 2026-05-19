# Discovery Guide

## Overview

`basekit.discovery` provides framework-neutral helpers for importing packages and modules dynamically. It is useful for model loading, route discovery, task registration, plugins, and other package-scanning workflows.

## Basic Usage

```python
from basekit.discovery import import_from_packages

failures = import_from_packages(["my_app.models", "my_app.tasks"])
if failures:
    for failure in failures:
        print(failure.to_dict())
```

## Security Validation

Use `allowed_prefixes` when package names may come from configuration.

```python
from basekit.discovery import import_from_packages

import_from_packages(
    "my_app.models,my_app.plugins",
    allowed_prefixes={"my_app.", "shared."},
    fail_on_error=True,
)
```

## Post Import Hook

Use `post_import_hook` when a framework needs a finalization step after all imports.

```python
from sqlalchemy.orm import configure_mappers

from basekit.discovery import import_from_packages

import_from_packages(
    ["my_app.models"],
    post_import_hook=configure_mappers,
    fail_on_error=True,
)
```

## Related Files

- `src/basekit/discovery.py`
- `tests/test_discovery.py`
