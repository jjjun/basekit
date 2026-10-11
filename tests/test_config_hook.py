import logging
import os
import subprocess
import sys
from types import ModuleType

import pytest

from basekit.config_hook import (
    Config,
    ConfigHookLoadError,
    get_config_from_hook,
    load_hook_function,
)


def test_get_config_from_hook_returns_config_when_hook_missing(monkeypatch):
    monkeypatch.delenv("CONFIG_HOOK", raising=False)
    config = Config()

    result = get_config_from_hook(config)

    assert result is config


def test_get_config_from_hook_raises_when_module_missing(monkeypatch):
    monkeypatch.setenv("CONFIG_HOOK", "missing_package.config:hook_config")
    config = Config()

    with pytest.raises(ConfigHookLoadError) as exc_info:
        get_config_from_hook(config)

    assert str(exc_info.value) == (
        "Failed to import config hook module 'missing_package.config' from "
        "CONFIG_HOOK='missing_package.config:hook_config': "
        "No module named 'missing_package'"
    )


def test_load_hook_function_preserves_default_source_messages(monkeypatch):
    module = ModuleType("test_config_hook_default_source")
    module.not_callable = "value"
    monkeypatch.setitem(sys.modules, module.__name__, module)

    with pytest.raises(
        ConfigHookLoadError,
        match=(
            "Config hook function 'missing' was not found in module "
            "'test_config_hook_default_source' "
            "\\(CONFIG_HOOK='test_config_hook_default_source:missing'\\)"
        ),
    ):
        load_hook_function("test_config_hook_default_source:missing")

    with pytest.raises(
        ConfigHookLoadError,
        match=(
            "Config hook target 'test_config_hook_default_source:not_callable' "
            "is not callable "
            "\\(CONFIG_HOOK='test_config_hook_default_source:not_callable'\\)"
        ),
    ):
        load_hook_function("test_config_hook_default_source:not_callable")


def test_load_hook_function_uses_custom_source_in_all_error_messages(monkeypatch):
    module = ModuleType("test_config_hook_custom_source")
    module.not_callable = "value"
    monkeypatch.setitem(sys.modules, module.__name__, module)

    with pytest.raises(ConfigHookLoadError, match="from pre_migration_hook="):
        load_hook_function(
            "missing_package.config:hook_config",
            source="pre_migration_hook",
        )

    with pytest.raises(
        ConfigHookLoadError,
        match="\\(pre_migration_hook='test_config_hook_custom_source:missing'\\)",
    ):
        load_hook_function(
            "test_config_hook_custom_source:missing",
            source="pre_migration_hook",
        )

    with pytest.raises(
        ConfigHookLoadError,
        match=(
            "\\(pre_migration_hook="
            "'test_config_hook_custom_source:not_callable'\\)"
        ),
    ):
        load_hook_function(
            "test_config_hook_custom_source:not_callable",
            source="pre_migration_hook",
        )


def test_load_hook_function_requires_explicit_function_when_default_is_none():
    with pytest.raises(
        ConfigHookLoadError,
        match=(
            "Config hook target from pre_migration_hook='example.hooks' must use "
            "'module:function_name' format"
        ),
    ):
        load_hook_function(
            "example.hooks",
            source="pre_migration_hook",
            default_function=None,
        )


def test_load_hook_function_uses_default_function_for_colonless_path(monkeypatch):
    module = ModuleType("test_config_hook_default_function")

    def hook_config(config):
        return config

    module.hook_config = hook_config
    monkeypatch.setitem(sys.modules, module.__name__, module)

    assert load_hook_function(module.__name__) is hook_config


def test_config_computes_data_and_log_paths(tmp_path):
    config = Config(root_path=str(tmp_path))
    config.package_name = "example"

    assert config.data_path == str(tmp_path / "data" / "example")
    assert config.log_path == str(tmp_path / "data" / "example" / "logs")
    assert config.log_file == (
        "test" if config.normalized_exec_env == "test" else "main"
    )
    assert config.log_file_path == str(
        tmp_path / "data" / "example" / "logs" / config.log_file
    )


@pytest.mark.parametrize("value", [" 1 ", "TRUE", " yes ", "On"])
def test_config_disables_directory_creation_when_no_side_effects_enabled(
    monkeypatch, tmp_path, value
):
    monkeypatch.setenv("BASEKIT_NO_SIDE_EFFECTS", value)
    config = Config(root_path=str(tmp_path))

    assert config.auto_create_dirs is False
    assert Config(auto_create_dirs=True).auto_create_dirs is True

    config.init()

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("value", [None, "false", " off ", ""])
def test_config_keeps_directory_creation_enabled_for_unrecognized_flag_values(
    monkeypatch, value
):
    if value is None:
        monkeypatch.delenv("BASEKIT_NO_SIDE_EFFECTS", raising=False)
    else:
        monkeypatch.setenv("BASEKIT_NO_SIDE_EFFECTS", value)

    assert Config().auto_create_dirs is True


def test_load_dotenv_is_skipped_when_no_side_effects_are_enabled(
    monkeypatch, tmp_path
):
    (tmp_path / ".env").write_text("MARKER=loaded\n", encoding="utf-8")
    monkeypatch.delenv("MARKER", raising=False)
    environment = os.environ.copy()
    environment.pop("MARKER", None)
    environment.pop("BASEKIT_NO_SIDE_EFFECTS", None)

    result_with_dotenv = subprocess.run(
        [
            sys.executable,
            "-c",
            "import basekit.config_hook, os; print(os.getenv('MARKER'))",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        check=True,
        text=True,
    )

    environment["BASEKIT_NO_SIDE_EFFECTS"] = "true"
    result_without_dotenv = subprocess.run(
        [
            sys.executable,
            "-c",
            "import basekit.config_hook, os; print(os.getenv('MARKER'))",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        check=True,
        text=True,
    )

    assert result_with_dotenv.stdout.strip() == "loaded"
    assert result_without_dotenv.stdout.strip() == "None"


@pytest.mark.parametrize(
    ("exec_env", "normalized_exec_env", "log_level", "log_file"),
    [
        ("prod", "prod", logging.INFO, "main"),
        ("production", "prod", logging.INFO, "main"),
        (" Prod ", "prod", logging.INFO, "main"),
        ("test", "test", logging.DEBUG, "test"),
        ("TEST", "test", logging.DEBUG, "test"),
        ("dev", "dev", logging.DEBUG, "main"),
        (" STAGING ", "staging", logging.DEBUG, "main"),
        (None, "", logging.DEBUG, "main"),
    ],
)
def test_config_log_level_defaults_by_execution_environment(
    monkeypatch, exec_env, normalized_exec_env, log_level, log_file
):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    config = Config(exec_env=exec_env)

    assert config.exec_env == exec_env
    assert config.normalized_exec_env == normalized_exec_env
    assert config.log_level == log_level
    assert config.log_file == log_file


def test_config_log_file_setter_overrides_default():
    config = Config(exec_env="TEST")
    config.log_file = "custom"

    assert config.log_file == "custom"


def test_config_log_level_uses_environment_override(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "warning")

    assert Config(exec_env="dev").log_level == logging.WARNING
    assert Config(exec_env="prod").log_level == logging.WARNING


def test_config_log_level_rejects_invalid_environment_override(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "bogus")

    with pytest.raises(ValueError, match="LOG_LEVEL.*bogus"):
        Config().log_level


@pytest.mark.parametrize("value", ["", "   "])
def test_config_log_level_ignores_blank_environment_override(monkeypatch, value):
    monkeypatch.setenv("LOG_LEVEL", value)

    assert Config(exec_env="prod").log_level == logging.INFO


def test_config_log_level_setter_overrides_environment(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "warning")
    config = Config(exec_env="prod")
    config.log_level = logging.ERROR

    assert config.log_level == logging.ERROR
