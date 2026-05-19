"""Shared Docker command and service manager helpers."""

import subprocess
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, ClassVar


class DockerCommandExecutor:
    """Stateless helpers for docker and docker-compose command execution."""

    @staticmethod
    def run_docker_compose(
        command: str,
        compose_file: Path,
        cwd: Path | None = None,
        capture_output: bool = False,
        project_name: str | None = None,
    ) -> str | None:
        if cwd is None:
            cwd = compose_file.parent

        cmd = ["docker-compose"]
        if project_name:
            cmd.extend(["-p", project_name])
        cmd.extend(["-f", str(compose_file)])
        cmd.extend(command.split())

        try:
            result = subprocess.run(
                cmd,
                check=True,
                cwd=str(cwd),
                capture_output=capture_output,
                text=True,
            )
            return result.stdout if capture_output else None
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "docker-compose command not found. "
                "Please install Docker Desktop: "
                "https://www.docker.com/products/docker-desktop"
            ) from exc

    @staticmethod
    def get_container_status(container_name: str) -> str:
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={container_name}",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "docker command not found. "
                "Please install Docker Desktop: "
                "https://www.docker.com/products/docker-desktop"
            ) from exc

    @staticmethod
    def is_container_running(container_name: str) -> bool:
        status = DockerCommandExecutor.get_container_status(container_name)
        return status.startswith("Up")

    @staticmethod
    def exec_command(
        container_name: str,
        command: list[str],
        stdin: bytes | None = None,
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess:
        cmd = ["docker", "exec"]
        if stdin is not None:
            cmd.append("-i")
        cmd.append(container_name)
        cmd.extend(command)

        try:
            return subprocess.run(
                cmd,
                input=stdin,
                capture_output=capture_output,
                check=True,
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "docker command not found. "
                "Please install Docker Desktop: "
                "https://www.docker.com/products/docker-desktop"
            ) from exc

    @staticmethod
    def wait_for_readiness(
        check_func: Callable[[], bool],
        max_retries: int = 30,
        interval_sec: int = 1,
        service_name: str = "Service",
    ) -> None:
        for attempt in range(max_retries):
            if check_func():
                return

            if (attempt + 1) % 5 == 0:
                print(f"  Still waiting... ({attempt + 1}/{max_retries}s)")

            time.sleep(interval_sec)

        raise TimeoutError(
            f"{service_name} did not start within {max_retries} seconds"
        )


def print_message(
    symbol: str, message: str, details: list[str] | None = None
) -> None:
    """Print a user-facing message with a cp932-safe fallback."""
    try:
        print(f"{symbol} {message}")
    except UnicodeEncodeError:
        print(f"[*] {message}")

    if details:
        for detail in details:
            print(f"  {detail}")


def validate_compose_file_exists(compose_file: Path, service_name: str) -> None:
    """Validate that a generated Docker Compose file exists."""
    if compose_file.exists():
        return

    print_message("WARNING:", "docker-compose.generated.yml was not found")
    print(f"   Expected: {compose_file}")
    print()
    print(f"Hint: generate the {service_name} Docker Compose file first")
    raise FileNotFoundError(f"Compose file not found: {compose_file}")


def format_connection_info(**kwargs) -> list[str]:
    return [f"{key}: {value}" for key, value in kwargs.items()]


class DockerManager(ABC):
    """Base class for Docker-backed service managers."""

    SERVICE_NAME: ClassVar[str]
    INIT_SUBDIR: ClassVar[str]
    GENERATE_COMMAND: ClassVar[str]

    def __init__(self, *, data_path: str | Path):
        if data_path is None:
            raise ValueError("data_path is required")
        self._data_path = Path(data_path)

    @abstractmethod
    def get_container_name(self) -> str:
        pass

    def get_generate_hint(self) -> str:
        return f"Hint: Run 'uv run {self.GENERATE_COMMAND}' first"

    def get_compose_file_path(self) -> Path:
        compose_file = self.get_compose_dir() / "docker-compose.generated.yml"
        if not compose_file.exists():
            raise FileNotFoundError(
                f"Compose file not found: {compose_file}\n{self.get_generate_hint()}"
            )
        return compose_file

    @abstractmethod
    def wait_for_service(self, max_retries: int = 30) -> None:
        pass

    def get_project_name(self) -> str:
        return self.get_container_name()

    def get_compose_dir(self) -> Path:
        compose_dir = self._data_path / self.SERVICE_NAME
        compose_dir.mkdir(parents=True, exist_ok=True)
        return compose_dir

    def get_init_dir(self) -> Path:
        init_dir = self.get_compose_dir() / self.INIT_SUBDIR
        init_dir.mkdir(parents=True, exist_ok=True)
        return init_dir

    def start(self, timeout_seconds: int = 30) -> None:
        print()
        print_message("START:", f"Starting {self.get_container_name()} container...")

        try:
            compose_file = self.get_compose_file_path()
        except FileNotFoundError as exc:
            print_message("ERROR:", str(exc))
            sys.exit(1)

        try:
            DockerCommandExecutor.run_docker_compose(
                "up -d",
                compose_file,
                cwd=compose_file.parent,
                project_name=self.get_project_name(),
            )
        except subprocess.CalledProcessError as exc:
            print_message("ERROR:", f"Failed to start container: {exc}")
            sys.exit(1)
        except FileNotFoundError as exc:
            print_message("ERROR:", str(exc))
            sys.exit(1)

        print_message("WAIT:", "Waiting for service to be ready...")

        try:
            self.wait_for_service(max_retries=timeout_seconds)
            print_message("OK:", f"{self.get_container_name()} is ready")
        except TimeoutError as exc:
            print_message("ERROR:", str(exc))
            sys.exit(1)

    def stop(self) -> None:
        try:
            compose_file = self.get_compose_file_path()
            validate_compose_file_exists(compose_file, self.get_container_name())
        except FileNotFoundError:
            return

        print_message("STOP:", f"Stopping {self.get_container_name()} container...")

        try:
            DockerCommandExecutor.run_docker_compose(
                "stop",
                compose_file,
                cwd=compose_file.parent,
                project_name=self.get_project_name(),
            )
            print_message("OK:", f"{self.get_container_name()} stopped")
        except subprocess.CalledProcessError as exc:
            print_message("ERROR:", f"Failed to stop container: {exc}")
            sys.exit(1)

    def remove(self) -> None:
        try:
            compose_file = self.get_compose_file_path()
            validate_compose_file_exists(compose_file, self.get_container_name())
        except FileNotFoundError:
            return

        print_message(
            "REMOVE:", f"Removing {self.get_container_name()} container and volumes..."
        )

        try:
            DockerCommandExecutor.run_docker_compose(
                "down -v",
                compose_file,
                cwd=compose_file.parent,
                project_name=self.get_project_name(),
            )
            print_message("OK:", f"{self.get_container_name()} removed")
        except subprocess.CalledProcessError as exc:
            print_message("ERROR:", f"Failed to remove container: {exc}")
            sys.exit(1)

    def status(self) -> bool:
        try:
            return bool(
                DockerCommandExecutor.get_container_status(self.get_container_name())
            )
        except FileNotFoundError:
            return False

    def is_running(self) -> bool:
        return self.status()


__all__ = [
    "DockerCommandExecutor",
    "DockerManager",
    "format_connection_info",
    "print_message",
    "validate_compose_file_exists",
]
