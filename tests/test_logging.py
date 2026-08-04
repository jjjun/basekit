import logging
from datetime import date

import pytest

from basekit.logging import (
    DateNamedDailyFileHandler,
    get_logger,
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
