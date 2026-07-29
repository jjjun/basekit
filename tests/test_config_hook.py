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
    assert config.log_file == ("test" if config.exec_env == "test" else "main")
    assert config.log_file_path == str(
        tmp_path / "data" / "example" / "logs" / config.log_file
    )
