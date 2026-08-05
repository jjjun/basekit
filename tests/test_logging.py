import logging
import os
import stat
import sys
from datetime import date

import pytest

from basekit.logging import (
    DateNamedDailyFileHandler,
    configure_default_logging,
    get_logger,
    has_logging_handlers,
    make_timed_rotating_handler,
    reset_logging_state,
)


def test_get_logger_returns_basekit_logger():
    logger = get_logger("test")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "basekit.test"


def test_get_logger_can_configure_custom_namespace(tmp_path):
    reset_logging_state()
    root_logger = logging.getLogger("example")
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    logger = get_logger(
        "test",
        logger_name="example",
        log_file_path=str(tmp_path / "main"),
    )
    logger.debug("message")

    active_log_file = tmp_path / f"main_{date.today().isoformat()}.log"
    assert active_log_file.exists()
    assert "example.test" in active_log_file.read_text(encoding="utf-8")


def test_get_logger_uses_configured_level_for_file_output(tmp_path):
    reset_logging_state()
    root_logger = logging.getLogger("example_level")
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    try:
        logger = get_logger(
            "test",
            logger_name="example_level",
            log_file_path=str(tmp_path / "main"),
            level=logging.INFO,
        )
        logger.debug("debug message")
        logger.info("info message")

        active_log_file = tmp_path / f"main_{date.today().isoformat()}.log"
        contents = active_log_file.read_text(encoding="utf-8")
        assert "debug message" not in contents
        assert "info message" in contents
    finally:
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        reset_logging_state()


def test_configure_default_logging_uses_level_for_console_handler(tmp_path):
    root_logger = logging.getLogger("example_warning")
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    try:
        assert configure_default_logging(
            "example_warning",
            str(tmp_path / "main"),
            level=logging.WARNING,
        )
        console_handler = next(
            handler
            for handler in root_logger.handlers
            if isinstance(handler, logging.StreamHandler)
            and not isinstance(handler, logging.FileHandler)
        )

        assert root_logger.level == logging.WARNING
        assert console_handler.level == logging.WARNING
    finally:
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)


def test_configure_default_logging_defaults_to_debug_file_and_info_console(tmp_path):
    root_logger = logging.getLogger("example_default_level")
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    try:
        assert configure_default_logging("example_default_level", str(tmp_path / "main"))
        file_handler = next(
            handler
            for handler in root_logger.handlers
            if isinstance(handler, logging.FileHandler)
        )
        console_handler = next(
            handler
            for handler in root_logger.handlers
            if isinstance(handler, logging.StreamHandler)
            and not isinstance(handler, logging.FileHandler)
        )

        assert root_logger.level == logging.DEBUG
        assert file_handler.level == logging.DEBUG
        assert console_handler.level == logging.INFO
    finally:
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)


@pytest.mark.parametrize(
    ("first_name", "second_name"),
    [("pkg_a", "pkg_b"), ("pkg_b", "pkg_a")],
)
def test_get_logger_configures_each_package_namespace(
    tmp_path, first_name, second_name
):
    reset_logging_state()
    logger_names = (first_name, second_name)
    root_loggers = [logging.getLogger(name) for name in logger_names]
    for root_logger in root_loggers:
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)

    try:
        for logger_name in logger_names:
            logger = get_logger(
                "worker",
                logger_name=logger_name,
                log_file_path=str(tmp_path / logger_name),
            )
            logger.info(f"{logger_name} message")

        for logger_name in logger_names:
            active_log_file = tmp_path / f"{logger_name}_{date.today().isoformat()}.log"
            assert active_log_file.exists()
            assert f"{logger_name}.worker" in active_log_file.read_text(
                encoding="utf-8"
            )
    finally:
        for root_logger in root_loggers:
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
        reset_logging_state()


def test_get_logger_configures_a_namespace_only_once(tmp_path):
    reset_logging_state()
    root_logger = logging.getLogger("example_once")
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    try:
        for name in ("first", "second"):
            get_logger(
                name,
                logger_name="example_once",
                log_file_path=str(tmp_path / "main"),
            )

        assert len(root_logger.handlers) == 2
    finally:
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        reset_logging_state()


def test_get_logger_can_configure_after_missing_log_file_path(tmp_path):
    reset_logging_state()
    root_logger = logging.getLogger("late_path")
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    try:
        get_logger("first", logger_name="late_path")
        get_logger(
            "second",
            logger_name="late_path",
            log_file_path=str(tmp_path / "main"),
        )

        assert len(root_logger.handlers) == 2
    finally:
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        reset_logging_state()


def test_get_logger_respects_application_basic_configuration(tmp_path):
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level
    root_logger.handlers.clear()
    logging.basicConfig()
    reset_logging_state()

    package_loggers = [logging.getLogger(name) for name in ("app_a", "app_b")]
    try:
        get_logger(
            "worker", logger_name="app_a", log_file_path=str(tmp_path / "unused_a")
        )
        get_logger(
            "worker", logger_name="app_b", log_file_path=str(tmp_path / "unused_b")
        )

        assert all(not logger.handlers for logger in package_loggers)
    finally:
        for handler in root_logger.handlers[:]:
            handler.close()
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)
        reset_logging_state()


@pytest.mark.parametrize("placement", ["package", "root"])
def test_marked_non_output_handler_does_not_prevent_default_logging(
    tmp_path, placement
):
    logger_name = f"marked_{placement}"
    package_logger = logging.getLogger(logger_name)
    root_logger = logging.getLogger()
    original_root_handlers = root_logger.handlers[:]
    original_root_level = root_logger.level
    marked_handler = logging.Handler()
    marked_handler.basekit_configures_output = False
    for handler in package_logger.handlers[:]:
        handler.close()
        package_logger.removeHandler(handler)
    root_logger.handlers.clear()
    reset_logging_state()

    try:
        (package_logger if placement == "package" else root_logger).addHandler(
            marked_handler
        )

        assert configure_default_logging(logger_name, str(tmp_path / "main"))
        assert any(
            isinstance(handler, DateNamedDailyFileHandler)
            for handler in package_logger.handlers
        )
    finally:
        for handler in package_logger.handlers[:]:
            handler.close()
            package_logger.removeHandler(handler)
        marked_handler.close()
        root_logger.handlers = original_root_handlers
        root_logger.setLevel(original_root_level)
        reset_logging_state()


@pytest.mark.parametrize("placement", ["package", "root"])
def test_null_handler_does_not_prevent_default_logging(tmp_path, placement):
    logger_name = f"null_{placement}"
    package_logger = logging.getLogger(logger_name)
    root_logger = logging.getLogger()
    original_root_handlers = root_logger.handlers[:]
    original_root_level = root_logger.level
    for handler in package_logger.handlers[:]:
        handler.close()
        package_logger.removeHandler(handler)
    root_logger.handlers.clear()

    try:
        (package_logger if placement == "package" else root_logger).addHandler(
            logging.NullHandler()
        )

        assert configure_default_logging(logger_name, str(tmp_path / "main"))
    finally:
        for handler in package_logger.handlers[:]:
            handler.close()
            package_logger.removeHandler(handler)
        root_logger.handlers = original_root_handlers
        root_logger.setLevel(original_root_level)


@pytest.mark.parametrize("placement", ["package", "root"])
def test_unmarked_handler_still_prevents_default_logging(tmp_path, placement):
    logger_name = f"unmarked_{placement}"
    package_logger = logging.getLogger(logger_name)
    root_logger = logging.getLogger()
    original_root_handlers = root_logger.handlers[:]
    original_root_level = root_logger.level
    for handler in package_logger.handlers[:]:
        handler.close()
        package_logger.removeHandler(handler)
    root_logger.handlers.clear()

    try:
        (package_logger if placement == "package" else root_logger).addHandler(
            logging.Handler()
        )

        assert not configure_default_logging(logger_name, str(tmp_path / "main"))
    finally:
        for handler in package_logger.handlers[:]:
            handler.close()
            package_logger.removeHandler(handler)
        root_logger.handlers = original_root_handlers
        root_logger.setLevel(original_root_level)


def test_pytest_root_handler_is_ignored_but_package_handler_is_not():
    logger_name = "pytest_handler"
    package_logger = logging.getLogger(logger_name)
    root_logger = logging.getLogger()
    original_root_handlers = root_logger.handlers[:]
    pytest_handler_type = type(
        "PytestHandler", (logging.Handler,), {"__module__": "_pytest.capture"}
    )
    pytest_handler = pytest_handler_type()
    for handler in package_logger.handlers[:]:
        handler.close()
        package_logger.removeHandler(handler)
    root_logger.handlers.clear()

    try:
        root_logger.addHandler(pytest_handler)
        assert not has_logging_handlers(logger_name)

        package_logger.addHandler(pytest_handler)
        assert has_logging_handlers(logger_name)
    finally:
        for handler in package_logger.handlers[:]:
            handler.close()
            package_logger.removeHandler(handler)
        root_logger.handlers = original_root_handlers


def test_get_logger_configures_after_marked_package_handler(tmp_path):
    logger_name = "marked_ordering"
    package_logger = logging.getLogger(logger_name)
    marked_handler = logging.Handler()
    marked_handler.basekit_configures_output = False
    for handler in package_logger.handlers[:]:
        handler.close()
        package_logger.removeHandler(handler)
    package_logger.addHandler(marked_handler)
    reset_logging_state()

    try:
        get_logger(
            "worker",
            logger_name=logger_name,
            log_file_path=str(tmp_path / "main"),
            level=logging.INFO,
        )

        assert any(
            isinstance(handler, DateNamedDailyFileHandler)
            for handler in package_logger.handlers
        )
        assert (tmp_path / f"main_{date.today().isoformat()}.log").exists()
    finally:
        for handler in package_logger.handlers[:]:
            handler.close()
            package_logger.removeHandler(handler)
        reset_logging_state()


def test_get_logger_can_enable_sqlalchemy_after_echo_was_disabled(monkeypatch):
    import basekit.logging as logging_module

    reset_logging_state()
    calls = []
    monkeypatch.setattr(
        logging_module,
        "configure_sqlalchemy_logging",
        lambda **kwargs: calls.append(kwargs),
    )

    get_logger("first", logger_name="sqlalchemy_first")
    get_logger("second", logger_name="sqlalchemy_second", sqlalchemy_echo=True)
    get_logger("third", logger_name="sqlalchemy_third", sqlalchemy_echo=True)

    assert calls == [{"enabled": True, "echo_level": "INFO", "log_file_path": None}]


def test_make_handler_writes_to_dated_active_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        DateNamedDailyFileHandler,
        "_today",
        lambda self: date(2026, 5, 5),
    )

    handler = make_timed_rotating_handler(str(tmp_path / "main"))
    logger = logging.getLogger("basekit.handler_test")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    logger.info("active file message")
    handler.flush()
    handler.close()

    active_file = tmp_path / "main_2026-05-05.log"
    assert active_file.exists()
    assert not (tmp_path / "main").exists()
    assert "active file message" in active_file.read_text(encoding="utf-8")


@pytest.mark.skipif(
    sys.platform == "win32", reason="Windows does not preserve POSIX modes"
)
def test_handler_creates_owner_only_log_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        DateNamedDailyFileHandler,
        "_today",
        lambda self: date(2026, 5, 5),
    )

    handler = make_timed_rotating_handler(str(tmp_path / "main"))
    handler.close()

    active_file = tmp_path / "main_2026-05-05.log"
    assert stat.S_IMODE(active_file.stat().st_mode) == 0o600


@pytest.mark.skipif(
    sys.platform == "win32", reason="Windows does not preserve POSIX modes"
)
def test_handler_applies_owner_only_mode_to_existing_log_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        DateNamedDailyFileHandler,
        "_today",
        lambda self: date(2026, 5, 5),
    )

    active_file = tmp_path / "main_2026-05-05.log"
    active_file.touch()
    os.chmod(active_file, 0o644)

    handler = make_timed_rotating_handler(str(tmp_path / "main"))
    handler.close()

    assert stat.S_IMODE(active_file.stat().st_mode) == 0o600


def test_handler_writes_after_date_switch(tmp_path, monkeypatch):
    current_date = date(2026, 5, 5)
    monkeypatch.setattr(
        DateNamedDailyFileHandler,
        "_today",
        lambda self: current_date,
    )

    handler = make_timed_rotating_handler(str(tmp_path / "main"))
    current_date = date(2026, 5, 6)

    handler.emit(logging.makeLogRecord({"msg": "rotated file message"}))
    handler.close()

    active_file = tmp_path / "main_2026-05-06.log"
    assert "rotated file message" in active_file.read_text(encoding="utf-8")


@pytest.mark.skipif(
    sys.platform == "win32", reason="Windows does not preserve POSIX modes"
)
def test_handler_applies_file_mode_after_date_switch(tmp_path, monkeypatch):
    current_date = date(2026, 5, 5)
    monkeypatch.setattr(
        DateNamedDailyFileHandler,
        "_today",
        lambda self: current_date,
    )

    handler = make_timed_rotating_handler(str(tmp_path / "main"), file_mode=0o640)
    current_date = date(2026, 5, 6)
    handler.emit(logging.makeLogRecord({"msg": "rotated file message"}))
    handler.close()

    active_file = tmp_path / "main_2026-05-06.log"
    assert stat.S_IMODE(active_file.stat().st_mode) == 0o640


def test_handler_writes_when_log_cleanup_cannot_delete_file(tmp_path, monkeypatch):
    current_date = date(2026, 5, 5)
    monkeypatch.setattr(
        DateNamedDailyFileHandler,
        "_today",
        lambda self: current_date,
    )

    handler = make_timed_rotating_handler(str(tmp_path / "main"), backup_count=1)
    old_log_file = tmp_path / "main_2026-05-05.log"
    real_unlink = type(old_log_file).unlink

    def raise_permission_error(path, *args, **kwargs):
        if path == old_log_file:
            raise PermissionError
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(type(old_log_file), "unlink", raise_permission_error)
    current_date = date(2026, 5, 6)

    handler.emit(logging.makeLogRecord({"msg": "rotated file message"}))
    handler.flush()
    handler.close()

    active_file = tmp_path / "main_2026-05-06.log"
    assert "rotated file message" in active_file.read_text(encoding="utf-8")


def test_handler_does_not_raise_when_date_switch_fails(tmp_path, monkeypatch):
    current_date = date(2026, 5, 5)
    monkeypatch.setattr(
        DateNamedDailyFileHandler,
        "_today",
        lambda self: current_date,
    )
    monkeypatch.setattr(logging, "raiseExceptions", False)

    handler = make_timed_rotating_handler(str(tmp_path / "main"))

    def raise_runtime_error(target_date):
        raise RuntimeError

    monkeypatch.setattr(handler, "_switch_to_date", raise_runtime_error)
    current_date = date(2026, 5, 6)

    handler.emit(logging.makeLogRecord({"msg": "rotation failure message"}))
    handler.flush()
    handler.close()

    active_file = tmp_path / "main_2026-05-05.log"
    assert "rotation failure message" in active_file.read_text(encoding="utf-8")


def test_handler_does_not_raise_when_rotated_file_cannot_open(tmp_path, monkeypatch):
    current_date = date(2026, 5, 5)
    monkeypatch.setattr(
        DateNamedDailyFileHandler,
        "_today",
        lambda self: current_date,
    )
    monkeypatch.setattr(logging, "raiseExceptions", False)

    handler = make_timed_rotating_handler(str(tmp_path / "main"))

    def raise_permission_error():
        raise PermissionError

    monkeypatch.setattr(handler, "_open", raise_permission_error)
    current_date = date(2026, 5, 6)

    handler.emit(logging.makeLogRecord({"msg": "first rotated file open failure"}))
    handler.emit(logging.makeLogRecord({"msg": "second rotated file open failure"}))
    handler.close()

    old_active_file = tmp_path / "main_2026-05-05.log"
    rotated_file = tmp_path / "main_2026-05-06.log"
    assert old_active_file.read_text(encoding="utf-8") == ""
    assert not rotated_file.exists()
