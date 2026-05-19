"""Small Docker Compose YAML generator."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DockerService:
    """Docker Compose service definition."""

    name: str
    image: str
    container_name: str
    ports: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    volumes: list[str] = field(default_factory=list)
    command: str | None = None
    healthcheck: dict[str, Any] | None = None
    depends_on: dict[str, Any] | None = None


@dataclass
class DockerVolume:
    """Docker Compose volume definition."""

    name: str
    driver: str = "local"


class DockerComposeGenerator:
    """Generate simple Docker Compose YAML from service and volume objects."""

    def __init__(self, version: str = "3.8"):
        self.version = version
        self.services: list[DockerService] = []
        self.volumes: list[DockerVolume] = []

    def add_service(self, service: DockerService) -> "DockerComposeGenerator":
        self.services.append(service)
        return self

    def add_volume(self, volume: DockerVolume) -> "DockerComposeGenerator":
        self.volumes.append(volume)
        return self

    def generate(self) -> str:
        lines = [f"version: '{self.version}'", "", "services:"]

        for service in self.services:
            lines.extend(self._generate_service(service))

        if self.volumes:
            lines.extend(["", "volumes:"])
            for volume in self.volumes:
                lines.append(f"  {volume.name}:")
                lines.append(f"    name: {volume.name}")
                if volume.driver != "local":
                    lines.append(f"    driver: {volume.driver}")

        return "\n".join(lines)

    def _generate_service(self, service: DockerService) -> list[str]:
        lines = [
            f"  {service.name}:",
            f"    image: {service.image}",
            f"    container_name: {service.container_name}",
        ]

        if service.environment:
            lines.append("    environment:")
            for key, value in service.environment.items():
                lines.append(f"      {key}: {value}")

        if service.ports:
            lines.append("    ports:")
            for port in service.ports:
                lines.append(f'      - "{port}"')

        if service.volumes:
            lines.append("    volumes:")
            for volume in service.volumes:
                lines.append(f"      - {volume}")

        if service.command:
            lines.append(f"    command: {service.command}")

        if service.healthcheck:
            lines.append("    healthcheck:")
            for key, value in service.healthcheck.items():
                lines.append(f"      {key}: {value}")

        if service.depends_on:
            lines.append("    depends_on:")
            for service_name, config in service.depends_on.items():
                lines.append(f"      {service_name}:")
                if isinstance(config, dict):
                    for key, value in config.items():
                        lines.append(f"        {key}: {value}")
                else:
                    lines.append(f"        condition: {config}")

        return lines

    def write_to_file(self, filepath: Path) -> None:
        filepath.write_text(self.generate(), encoding="utf-8")


__all__ = ["DockerComposeGenerator", "DockerService", "DockerVolume"]
