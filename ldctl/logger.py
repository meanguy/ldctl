import logging
import threading

type _Level = int | str

_logger: logging.Logger | None = None
_lock = threading.Lock()


class _LowerLevelnameFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.levelname = record.levelname.lower()

        return super().format(record)


def configure_formatter() -> logging.Formatter:
    fmt = "[%(asctime)s][%(levelname)8s] - %(name)s %(filename)s:%(lineno)d: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    return _LowerLevelnameFormatter(fmt=fmt, datefmt=datefmt)


def configure_handler(
    level: _Level = logging.WARNING,
    formatter: logging.Formatter | None = None,
) -> logging.Handler:
    if formatter is None:
        formatter = configure_formatter()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(level)

    return handler


def configure_logger(
    level: _Level = logging.WARNING,
    handler: logging.Handler | None = None,
    formatter: logging.Formatter | None = None,
) -> logging.Logger:
    global _logger

    with _lock:
        if _logger is None:
            _logger = logging.getLogger(__name__)
            _logger.setLevel(level)

            if handler is None:
                handler = configure_handler(level, formatter)

            _logger.addHandler(handler)

    return _logger
