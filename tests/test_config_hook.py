import pytest

from basekit.config_hook import Config, ConfigHookLoadError, get_config_from_hook


def test_get_config_from_hook_returns_config_when_hook_missing(monkeypatch):
    monkeypatch.delenv("CONFIG_HOOK", raising=False)
    config = Config()

    result = get_config_from_hook(config)

    assert result is config


def test_get_config_from_hook_raises_when_module_missing(monkeypatch):
    monkeypatch.setenv("CONFIG_HOOK", "missing_package.config:hook_config")
    config = Config()

    with pytest.raises(ConfigHookLoadError, match="Failed to import config hook module"):
        get_config_from_hook(config)


def test_config_computes_data_and_log_paths(tmp_path):
    config = Config(root_path=str(tmp_path))
    config.package_name = "example"

    assert config.data_path == str(tmp_path / "data" / "example")
    assert config.log_path == str(tmp_path / "data" / "example" / "logs")
    assert config.log_file == ("test" if config.exec_env == "test" else "main")
    assert config.log_file_path == str(
        tmp_path / "data" / "example" / "logs" / config.log_file
    )
