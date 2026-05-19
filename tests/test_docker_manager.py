import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from basekit.docker_manager import (
    DockerCommandExecutor,
    DockerManager,
    format_connection_info,
    print_message,
    validate_compose_file_exists,
)


class SampleDockerManager(DockerManager):
    SERVICE_NAME = "test_service"
    INIT_SUBDIR = "init"
    GENERATE_COMMAND = "test_generate"

    def __init__(self, data_path: Path, container_name: str = "test_container"):
        super().__init__(data_path=data_path)
        self.container_name = container_name

    def get_container_name(self) -> str:
        return self.container_name

    def wait_for_service(self, max_retries: int = 30) -> None:
        return None


def test_docker_manager_requires_data_path():
    with pytest.raises(ValueError, match="data_path is required"):
        DockerManager.__init__(object(), data_path=None)


def test_get_compose_dir_uses_injected_data_path(tmp_path):
    manager = SampleDockerManager(tmp_path)

    assert manager.get_compose_dir() == tmp_path / "test_service"
    assert manager.get_compose_dir().exists()


def test_get_init_dir_uses_injected_data_path(tmp_path):
    manager = SampleDockerManager(tmp_path)

    assert manager.get_init_dir() == tmp_path / "test_service" / "init"
    assert manager.get_init_dir().exists()


def test_get_compose_file_path_uses_generate_hint(tmp_path):
    manager = SampleDockerManager(tmp_path)

    with pytest.raises(FileNotFoundError, match="uv run test_generate"):
        manager.get_compose_file_path()


def test_start_runs_docker_compose_and_waits(tmp_path):
    manager = SampleDockerManager(tmp_path)
    compose_file = manager.get_compose_dir() / "docker-compose.generated.yml"
    compose_file.write_text("version: '3.8'\n", encoding="utf-8")

    with patch("basekit.docker_manager.DockerCommandExecutor.run_docker_compose") as run:
        with patch.object(manager, "wait_for_service") as wait:
            manager.start(timeout_seconds=45)

    run.assert_called_once()
    wait.assert_called_once_with(max_retries=45)


def test_start_exits_when_compose_command_fails(tmp_path):
    manager = SampleDockerManager(tmp_path)
    compose_file = manager.get_compose_dir() / "docker-compose.generated.yml"
    compose_file.write_text("version: '3.8'\n", encoding="utf-8")

    with patch("basekit.docker_manager.DockerCommandExecutor.run_docker_compose") as run:
        run.side_effect = subprocess.CalledProcessError(1, "docker-compose")
        with pytest.raises(SystemExit):
            manager.start()


def test_stop_returns_when_compose_file_missing(tmp_path):
    manager = SampleDockerManager(tmp_path)

    manager.stop()


def test_status_returns_bool_from_container_status(tmp_path):
    manager = SampleDockerManager(tmp_path)

    with patch("basekit.docker_manager.DockerCommandExecutor.get_container_status") as status:
        status.return_value = "Up 10 minutes"
        assert manager.status() is True

        status.return_value = ""
        assert manager.status() is False


def test_run_docker_compose_builds_expected_command(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("version: '3.8'\n", encoding="utf-8")

    with patch("basekit.docker_manager.subprocess.run") as run:
        run.return_value.stdout = "ok"
        result = DockerCommandExecutor.run_docker_compose(
            "up -d",
            compose_file,
            capture_output=True,
            project_name="project",
        )

    assert result == "ok"
    run.assert_called_once()
    assert run.call_args.args[0] == [
        "docker-compose",
        "-p",
        "project",
        "-f",
        str(compose_file),
        "up",
        "-d",
    ]


def test_utility_functions(tmp_path, capsys):
    compose_file = tmp_path / "docker-compose.generated.yml"
    with pytest.raises(FileNotFoundError):
        validate_compose_file_exists(compose_file, "test")

    compose_file.write_text("version: '3.8'\n", encoding="utf-8")
    validate_compose_file_exists(compose_file, "test")

    print_message("OK:", "message", ["detail"])
    captured = capsys.readouterr()
    assert "OK: message" in captured.out
    assert "  detail" in captured.out

    assert format_connection_info(Host="localhost", Port=5432) == [
        "Host: localhost",
        "Port: 5432",
    ]
