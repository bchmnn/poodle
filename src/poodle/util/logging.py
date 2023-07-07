import logging
from http.client import HTTPConnection
from logging import Logger, StreamHandler
from typing import Optional


class Loggable:
    _logger: Logger = logging.getLogger()

    def init_logger(
        self, name, level: int = logging.ERROR, sh: Optional[StreamHandler] = None
    ):
        if sh is None:
            sh = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        sh.setFormatter(formatter)
        self._logger = logging.getLogger(name)
        self._logger.addHandler(sh)
        self._logger.setLevel(level)


def requests_logging(level: int):
    if level <= logging.DEBUG:
        HTTPConnection.debuglevel = 1
    else:
        HTTPConnection.debuglevel = 0

    logging.basicConfig()
    logging.getLogger().setLevel(level)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(level)
