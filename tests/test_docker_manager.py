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


def test_stop_exits_when_compose_command_is_missing(tmp_path, capsys):
    manager = SampleDockerManager(tmp_path)
    compose_file = manager.get_compose_dir() / "docker-compose.generated.yml"
    compose_file.write_text("version: '3.8'\n", encoding="utf-8")

    with patch(
        "basekit.docker_manager.DockerCommandExecutor.run_docker_compose",
        side_effect=FileNotFoundError("compose command missing"),
    ):
        with pytest.raises(SystemExit):
            manager.stop()

    assert "ERROR: compose command missing" in capsys.readouterr().out


def test_remove_exits_when_compose_command_is_missing(tmp_path, capsys):
    manager = SampleDockerManager(tmp_path)
    compose_file = manager.get_compose_dir() / "docker-compose.generated.yml"
    compose_file.write_text("version: '3.8'\n", encoding="utf-8")

    with patch(
        "basekit.docker_manager.DockerCommandExecutor.run_docker_compose",
        side_effect=FileNotFoundError("compose command missing"),
    ):
        with pytest.raises(SystemExit):
            manager.remove()

    assert "ERROR: compose command missing" in capsys.readouterr().out


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


def test_get_container_status_returns_exact_name_match():
    output = (
        "mine_py_redis_dev\tUp 10 minutes\n"
        "mine_py_redis_test\tUp 5 minutes\n"
        "mine_py_redis\tUp 2 minutes\n"
    )
    command = [
        "docker",
        "ps",
        "--filter",
        "name=mine_py_redis",
        "--format",
        "{{.Names}}\\t{{.Status}}",
    ]

    with patch(
        "basekit.docker_manager.subprocess.run",
        return_value=subprocess.CompletedProcess(
            command, 0, stdout=output, stderr=""
        ),
    ) as run:
        assert (
            DockerCommandExecutor.get_container_status("mine_py_redis")
            == "Up 2 minutes"
        )

    run.assert_called_once_with(
        command,
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.mark.parametrize("container_name", ["x_dev", "abc123_x", "xx"])
def test_is_container_running_ignores_partial_name_matches(container_name):
    output = f"{container_name}\tUp 10 minutes\n"
    command = ["docker", "ps"]

    with patch(
        "basekit.docker_manager.subprocess.run",
        return_value=subprocess.CompletedProcess(
            command, 0, stdout=output, stderr=""
        ),
    ):
        assert DockerCommandExecutor.is_container_running("x") is False


def test_is_container_running_for_exact_name():
    output = "x_dev\tUp 10 minutes\nx\tUp 2 minutes\n"
    command = ["docker", "ps"]

    with patch(
        "basekit.docker_manager.subprocess.run",
        return_value=subprocess.CompletedProcess(
            command, 0, stdout=output, stderr=""
        ),
    ):
        assert DockerCommandExecutor.is_container_running("x") is True


def test_run_docker_compose_builds_expected_command(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("version: '3.8'\n", encoding="utf-8")

    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        if command == ["docker", "compose", "version"]:
            return subprocess.CompletedProcess(command, 0, stdout="v2", stderr="")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    with patch("basekit.docker_manager.subprocess.run", side_effect=fake_run):
        result = DockerCommandExecutor.run_docker_compose(
            "up -d",
            compose_file,
            capture_output=True,
            project_name="project",
        )

    assert result == "ok"
    assert calls[0] == (
        ["docker", "compose", "version"],
        {"capture_output": True, "text": True, "check": False},
    )
    assert calls[1][0] == [
        "docker",
        "compose",
        "-p",
        "project",
        "-f",
        str(compose_file),
        "up",
        "-d",
    ]


def test_run_docker_compose_falls_back_to_legacy_command_when_plugin_is_missing(
    tmp_path,
):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("version: '3.8'\n", encoding="utf-8")
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if command == ["docker", "compose", "version"]:
            return subprocess.CompletedProcess(
                command, 1, stdout="", stderr="missing"
            )
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    with patch("basekit.docker_manager.subprocess.run", side_effect=fake_run):
        DockerCommandExecutor.run_docker_compose("stop", compose_file)

    assert calls[1][0] == "docker-compose"
    assert calls[1][-1] == "stop"


def test_run_docker_compose_falls_back_when_docker_cli_is_missing(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("version: '3.8'\n", encoding="utf-8")
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if command == ["docker", "compose", "version"]:
            raise FileNotFoundError("docker not found")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    with patch("basekit.docker_manager.subprocess.run", side_effect=fake_run):
        DockerCommandExecutor.run_docker_compose("stop", compose_file)

    assert calls[1][0] == "docker-compose"
    assert calls[1][-1] == "stop"


def test_run_docker_compose_reports_when_both_commands_are_missing(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("version: '3.8'\n", encoding="utf-8")

    def fake_run(command, **kwargs):
        raise FileNotFoundError("command not found")

    with patch("basekit.docker_manager.subprocess.run", side_effect=fake_run):
        with pytest.raises(FileNotFoundError) as error:
            DockerCommandExecutor.run_docker_compose("stop", compose_file)

    assert "docker compose" in str(error.value)
    assert "docker-compose" in str(error.value)


def test_get_container_status_has_neutral_docker_install_message():
    with patch(
        "basekit.docker_manager.subprocess.run", side_effect=FileNotFoundError
    ):
        with pytest.raises(
            FileNotFoundError, match="Docker Engine or Docker Desktop"
        ):
            DockerCommandExecutor.get_container_status("test_container")


def test_exec_command_has_neutral_docker_install_message():
    with patch(
        "basekit.docker_manager.subprocess.run", side_effect=FileNotFoundError
    ):
        with pytest.raises(
            FileNotFoundError, match="Docker Engine or Docker Desktop"
        ):
            DockerCommandExecutor.exec_command("test_container", ["true"])


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
