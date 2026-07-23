# Docker Manager Guide

## Overview

`basekit.docker_manager` contains shared Docker subprocess helpers and a base class for service managers. It does not import configuration from consuming projects; service-specific managers inject paths and settings.

## Basic Manager

```python
from pathlib import Path

from basekit.docker_manager import DockerManager, DockerCommandExecutor


class RedisManager(DockerManager):
    SERVICE_NAME = "redis"
    INIT_SUBDIR = "redis_init"
    GENERATE_COMMAND = "redis_generate"

    def __init__(self, data_path: str | Path, container_name: str):
        super().__init__(data_path=data_path)
        self.container_name = container_name

    def get_container_name(self) -> str:
        return self.container_name

    def wait_for_service(self, max_retries: int = 30) -> None:
        DockerCommandExecutor.wait_for_readiness(
            lambda: DockerCommandExecutor.is_container_running(self.container_name),
            max_retries=max_retries,
            service_name="Redis",
        )
```

## Path Contract

`DockerManager` requires `data_path`:

```python
manager = RedisManager(data_path="data/my_app", container_name="my_redis")
```

Generated Compose files are expected at:

```text
<data_path>/<SERVICE_NAME>/docker-compose.generated.yml
```

Initialization files are stored below:

```text
<data_path>/<SERVICE_NAME>/<INIT_SUBDIR>/
```

## Related Files

- [Implementation](../../src/basekit/docker_manager.py)
- [Tests](../../tests/test_docker_manager.py)
