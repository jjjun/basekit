# Docker Compose Guide

## Overview

`basekit.docker_compose` provides a small object-based generator for simple Docker Compose files. It is intentionally lightweight and is best suited for predictable service definitions.

## Basic Usage

```python
from pathlib import Path

from basekit.docker_compose import DockerComposeGenerator, DockerService, DockerVolume

service = DockerService(
    name="redis",
    image="redis:7-alpine",
    container_name="my_redis",
    ports=["6379:6379"],
    volumes=["redis_data:/data"],
)

generator = DockerComposeGenerator()
generator.add_service(service)
generator.add_volume(DockerVolume(name="redis_data"))
generator.write_to_file(Path("docker-compose.generated.yml"))
```

## Notes

The generator writes straightforward YAML strings. For highly dynamic or nested Compose features, consider extending the generator carefully or using a structured YAML library in the consuming project.

## Related Files

- `src/basekit/docker_compose.py`
- `tests/test_docker_compose.py`
