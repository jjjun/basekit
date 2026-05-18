import logging
from datetime import date

from basekit.logging import (
    DateNamedDailyFileHandler,
    get_logger,
    make_timed_rotating_handler,
)


def test_get_logger_returns_basekit_logger():
    logger = get_logger("test")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "basekit.test"


def test_get_logger_can_configure_custom_namespace(tmp_path):
    import basekit.logging as logging_module

    logging_module._logger_initialized = False
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
