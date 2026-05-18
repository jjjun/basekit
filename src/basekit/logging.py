import logging
from datetime import date
from pathlib import Path
from typing import Optional

_logger_initialized = False
_sqlalchemy_logging_initialized = False


class DateNamedDailyFileHandler(logging.FileHandler):
    """Write logs to the active ``<base>_<YYYY-MM-DD>.log`` file."""

    def __init__(
        self,
        base_path: str,
        backup_count: int = 30,
        encoding: str = "utf-8",
    ):
        self.base_path = Path(base_path)
        self.backup_count = backup_count
        self.base_path.parent.mkdir(parents=True, exist_ok=True)
        self.current_date = self._today()
        super().__init__(
            self._path_for_date(self.current_date),
            mode="a",
            encoding=encoding,
        )
        self._cleanup_old_logs()

    def emit(self, record: logging.LogRecord) -> None:
        today = self._today()
        if today != self.current_date:
            self._switch_to_date(today)
        super().emit(record)

    def _today(self) -> date:
        return date.today()

    def _path_for_date(self, target_date: date) -> str:
        return str(
            self.base_path.with_name(
                f"{self.base_path.name}_{target_date.isoformat()}.log"
            )
        )

    def _switch_to_date(self, target_date: date) -> None:
        if self.stream:
            self.stream.flush()
            self.stream.close()
            self.stream = None
        self.current_date = target_date
        self.baseFilename = self._path_for_date(target_date)
        self.stream = self._open()
        self._cleanup_old_logs()

    def _cleanup_old_logs(self) -> None:
        if self.backup_count <= 0:
            return

        candidates: list[tuple[date, Path]] = []
        prefix = f"{self.base_path.name}_"
        for path in self.base_path.parent.glob(f"{prefix}*.log"):
            date_text = path.name[len(prefix) : -4]
            try:
                log_date = date.fromisoformat(date_text)
            except ValueError:
                continue
            candidates.append((log_date, path))

        candidates.sort(key=lambda item: item[0], reverse=True)
        for _, path in candidates[self.backup_count :]:
            try:
                path.unlink()
            except FileNotFoundError:
                continue


def make_timed_rotating_handler(
    base_path: str, backup_count: int = 30
) -> DateNamedDailyFileHandler:
    """Create a daily rotating handler using ``<base_path>_<YYYY-MM-DD>.log``."""
    return DateNamedDailyFileHandler(base_path, backup_count=backup_count)


def has_logging_handlers(logger_name: str) -> bool:
    """Return whether root or the package logger already has real handlers."""
    root_handlers = [
        handler
        for handler in logging.getLogger().handlers
        if not type(handler).__module__.startswith("_pytest.")
    ]
    return bool(logging.getLogger(logger_name).handlers or root_handlers)


def configure_default_logging(
    logger_name: str,
    log_file_path: Optional[str],
) -> None:
    """Configure a package root logger when the application has no handlers."""
    if has_logging_handlers(logger_name) or not log_file_path:
        return

    root_logger = logging.getLogger(logger_name)
    root_logger.setLevel(logging.DEBUG)

    file_handler = make_timed_rotating_handler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root_logger.addHandler(console_handler)


def configure_sqlalchemy_logging(
    *,
    enabled: bool,
    echo_level: str = "INFO",
    log_file_path: Optional[str] = None,
) -> None:
    """Configure SQLAlchemy engine logging if requested by the caller."""
    if not enabled:
        return

    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine.Engine")
    level_map = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }
    log_level = level_map.get(echo_level, logging.INFO)
    sqlalchemy_logger.setLevel(log_level)

    if sqlalchemy_logger.handlers:
        return

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter("SQL: %(message)s"))
    sqlalchemy_logger.addHandler(console_handler)

    if log_file_path:
        file_handler = make_timed_rotating_handler(log_file_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - sqlalchemy.engine.Engine - %(levelname)s - %(message)s"
            )
        )
        sqlalchemy_logger.addHandler(file_handler)


def get_logger(
    name: str,
    *,
    logger_name: str = "basekit",
    log_file_path: Optional[str] = None,
    sqlalchemy_echo: bool = False,
    sqlalchemy_echo_level: str = "INFO",
) -> logging.Logger:
    """Return a logger and optionally configure package default handlers."""
    global _logger_initialized, _sqlalchemy_logging_initialized

    logger = logging.getLogger(f"{logger_name}.{name}")

    if not _logger_initialized:
        _logger_initialized = True
        configure_default_logging(logger_name, log_file_path)

        if not _sqlalchemy_logging_initialized:
            _sqlalchemy_logging_initialized = True
            configure_sqlalchemy_logging(
                enabled=sqlalchemy_echo,
                echo_level=sqlalchemy_echo_level,
                log_file_path=log_file_path,
            )

    return logger


__all__ = [
    "DateNamedDailyFileHandler",
    "configure_default_logging",
    "configure_sqlalchemy_logging",
    "get_logger",
    "has_logging_handlers",
    "make_timed_rotating_handler",
]
