import copy
import importlib
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

from dotenv import load_dotenv

load_dotenv()


class ConfigHookLoadError(RuntimeError):
    """Raised when CONFIG_HOOK points to an invalid hook."""


def load_hook_function(hook_path: str):
    """Load a config hook function from ``module.path:function_name``."""
    if ":" in hook_path:
        module_path, function_name = hook_path.rsplit(":", 1)
    else:
        module_path = hook_path
        function_name = "hook_config"

    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise ConfigHookLoadError(
            f"Failed to import config hook module '{module_path}' "
            f"from CONFIG_HOOK='{hook_path}': {exc}"
        ) from exc

    if not hasattr(module, function_name):
        raise ConfigHookLoadError(
            f"Config hook function '{function_name}' was not found in module "
            f"'{module_path}' (CONFIG_HOOK='{hook_path}')"
        )

    hook_function = getattr(module, function_name)
    if not callable(hook_function):
        raise ConfigHookLoadError(
            f"Config hook target '{module_path}:{function_name}' is not callable "
            f"(CONFIG_HOOK='{hook_path}')"
        )
    return hook_function


def get_config_from_hook(config: dataclass) -> dataclass:
    """Return ``config`` after applying the hook specified by ``CONFIG_HOOK``."""
    hook_path = os.getenv("CONFIG_HOOK")

    if not hook_path or hook_path.strip() == "":
        return config

    hook_function = load_hook_function(hook_path)
    return hook_function(config)


@dataclass
class Config:
    package_name: Optional[str] = field(default=None, init=False)
    root_path: Optional[str] = field(default=None)
    exec_env: str = field(default=os.getenv("EXEC_ENV", "dev"))
    auto_create_dirs: bool = field(default=True)
    _data_path: Optional[str] = field(default=None, init=False, repr=False)
    _log_path: Optional[str] = field(default=None, init=False, repr=False)
    _log_file: Optional[str] = field(default=None, init=False, repr=False)

    def _get_or_default(self, private_attr: str, default_value):
        value = getattr(self, private_attr, None)
        if value is not None:
            return value
        return default_value

    def _ensure_path_exists(self, paths: Union[str, list[str]]):
        if paths is None:
            return

        if isinstance(paths, str):
            paths = [paths]

        for path in paths:
            if not path:
                continue
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                print(f"Warning: Could not create directory {path}: {exc}")

    def _retry_delete(self, path, retries=5, delay=1):
        for _ in range(retries):
            try:
                shutil.rmtree(path)
                break
            except PermissionError as exc:
                print(f"Retrying delete for {path}: {exc}")
                time.sleep(delay)
        else:
            raise Exception(f"Failed to delete {path} after {retries} retries")

    def _delete_path_if_exists(self, path):
        if os.path.exists(path):
            self._retry_delete(path)

    def init(self):
        if self.auto_create_dirs:
            self._ensure_path_exists(
                [
                    self.data_path,
                    self.log_path,
                ]
            )

    def cleanup(self) -> None:
        pass

    def clone(self) -> "Config":
        return copy.deepcopy(self)

    @property
    def data_path(self) -> Optional[str]:
        if self._data_path is not None:
            return self._data_path

        if self.root_path:
            path = Path(self.root_path) / "data"
            if self.package_name:
                path = path / self.package_name
            return str(path)

        return None

    @data_path.setter
    def data_path(self, value: Optional[str]):
        self._data_path = value

    @property
    def log_path(self) -> Optional[str]:
        return self._get_or_default(
            "_log_path",
            str(Path(self.data_path) / "logs") if self.data_path else None,
        )

    @log_path.setter
    def log_path(self, value: Optional[str]):
        self._log_path = value

    @property
    def log_file(self) -> Optional[str]:
        return self._get_or_default(
            "_log_file",
            "test" if self.exec_env == "test" else "main",
        )

    @log_file.setter
    def log_file(self, value: Optional[str]):
        self._log_file = value

    @property
    def log_file_path(self) -> Optional[str]:
        if not self.log_path:
            return None
        return str(Path(self.log_path) / self.log_file)
