"""Shared Python application foundation utilities."""

__version__ = "0.5.0"

from basekit.config_hook import (
    Config,
    ConfigHookLoadError,
    get_config_from_hook,
    load_hook_function,
)
from basekit.discovery import DiscoveryError, DiscoveryFailure
from basekit.docker_compose import DockerComposeGenerator, DockerService, DockerVolume
from basekit.docker_manager import DockerCommandExecutor, DockerManager
from basekit.logging import (
    DateNamedDailyFileHandler,
    make_timed_rotating_handler,
    reset_logging_state,
)
from basekit.vault import Vault

__all__ = [
    "__version__",
    "Config",
    "ConfigHookLoadError",
    "DateNamedDailyFileHandler",
    "DiscoveryError",
    "DiscoveryFailure",
    "DockerCommandExecutor",
    "DockerComposeGenerator",
    "DockerManager",
    "DockerService",
    "DockerVolume",
    "get_config_from_hook",
    "load_hook_function",
    "make_timed_rotating_handler",
    "reset_logging_state",
    "Vault",
]
